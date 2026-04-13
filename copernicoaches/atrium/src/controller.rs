use std::path::{Path, PathBuf};

use crate::display::{DisplayColumn, DisplayRow, DisplayRowKind, DisplayState};
use crate::filesystem::{DirectoryListing, FileInfo, Filesystem, FilesystemAdapter};
use crate::state::{AppState, build_initial_state};

pub struct NavigationController<F: Filesystem = FilesystemAdapter> {
    filesystem: F,
    pub state: AppState,
}

impl NavigationController<FilesystemAdapter> {
    pub fn new(start_path: Option<PathBuf>) -> Self {
        Self::with_filesystem(start_path, FilesystemAdapter)
    }
}

impl<F: Filesystem> NavigationController<F> {
    pub fn with_filesystem(start_path: Option<PathBuf>, filesystem: F) -> Self {
        let state = build_initial_state(start_path, &filesystem);
        Self { filesystem, state }
    }

    pub fn move_up(&mut self) {
        self.move_selection(-1);
    }

    pub fn move_down(&mut self) {
        self.move_selection(1);
    }

    pub fn enter_selection(&mut self) -> bool {
        let Some(selected) = self.state.selected.clone() else {
            return false;
        };
        if !selected.is_dir {
            return false;
        }

        self.load_directory(&selected.path);
        true
    }

    pub fn go_parent(&mut self) -> bool {
        let Some(parent_dir) = self.state.parent_dir.clone() else {
            return false;
        };
        let old_current_dir = self.state.current_dir.clone();
        self.load_directory(&parent_dir);

        let restored = self
            .state
            .current_entries
            .iter()
            .find(|entry| entry.path == old_current_dir)
            .cloned();
        self.state.selected = restored.clone();
        self.state.preview_target = restored;
        true
    }

    pub fn build_display_state(&self, column_width: usize, _viewport_height: usize) -> DisplayState {
        let parent_listing = self.parent_listing();
        let left_rows = self.directory_rows(
            parent_listing.as_ref(),
            Some(&self.state.current_dir),
            "Root",
        );
        let center_rows = self.directory_rows(
            Some(&DirectoryListing {
                path: self.state.current_dir.clone(),
                entries: self.state.current_entries.clone(),
                error: self.state.current_error.clone(),
            }),
            self.state
                .selected
                .as_ref()
                .map(|entry| entry.path.as_path()),
            "Empty directory",
        );
        let preview_rows = self.preview_rows();

        DisplayState {
            current_path: self.state.current_dir.display().to_string(),
            column_width,
            left: DisplayColumn {
                title: "Parent".to_string(),
                selected_index: selected_index(&left_rows),
                rows: left_rows,
                emphasized: false,
                scroll_offset: 0,
            },
            center: DisplayColumn {
                title: "Current".to_string(),
                selected_index: selected_index(&center_rows),
                rows: center_rows,
                emphasized: true,
                scroll_offset: 0,
            },
            right: DisplayColumn {
                title: "Preview".to_string(),
                selected_index: selected_index(&preview_rows),
                rows: preview_rows,
                emphasized: false,
                scroll_offset: 0,
            },
        }
    }

    fn move_selection(&mut self, offset: isize) {
        let Some(selected) = self.state.selected.clone() else {
            return;
        };
        let Some(current_index) = self
            .state
            .current_entries
            .iter()
            .position(|entry| entry == &selected)
        else {
            return;
        };

        let new_index = if offset.is_negative() {
            current_index.saturating_sub(offset.unsigned_abs())
        } else {
            (current_index + offset as usize)
                .min(self.state.current_entries.len().saturating_sub(1))
        };
        let selected = self.state.current_entries[new_index].clone();
        self.state.selected = Some(selected.clone());
        self.state.preview_target = Some(selected);
    }

    fn load_directory(&mut self, path: &Path) {
        let listing = self.filesystem.list_directory(path);
        let current_dir = listing.path;
        let selected = listing.entries.first().cloned();

        self.state.parent_dir = current_dir.parent().map(|path| path.to_path_buf());
        self.state.current_dir = current_dir;
        self.state.current_entries = listing.entries;
        self.state.selected = selected.clone();
        self.state.preview_target = selected;
        self.state.current_error = listing.error;
    }

    fn parent_listing(&self) -> Option<DirectoryListing> {
        self.state
            .parent_dir
            .as_ref()
            .map(|parent| self.filesystem.list_directory(parent))
    }

    fn directory_rows(
        &self,
        listing: Option<&DirectoryListing>,
        highlight_path: Option<&Path>,
        empty_text: &str,
    ) -> Vec<DisplayRow> {
        let Some(listing) = listing else {
            return vec![DisplayRow {
                text: empty_text.to_string(),
                kind: DisplayRowKind::Empty,
                highlighted: false,
            }];
        };

        if let Some(error) = &listing.error {
            return vec![DisplayRow {
                text: error.clone(),
                kind: DisplayRowKind::Error,
                highlighted: false,
            }];
        }

        if listing.entries.is_empty() {
            return vec![DisplayRow {
                text: empty_text.to_string(),
                kind: DisplayRowKind::Empty,
                highlighted: false,
            }];
        }

        listing
            .entries
            .iter()
            .map(|entry| DisplayRow {
                text: entry.name.clone(),
                kind: if entry.is_dir {
                    DisplayRowKind::Directory
                } else {
                    DisplayRowKind::File
                },
                highlighted: highlight_path.is_some_and(|path| entry.path == path),
            })
            .collect()
    }

    fn preview_rows(&self) -> Vec<DisplayRow> {
        let Some(target) = self.state.preview_target.as_ref() else {
            return Vec::new();
        };

        if target.is_dir {
            let listing = self.filesystem.list_directory(&target.path);
            return self.directory_rows(Some(&listing), None, "Empty directory");
        }

        let info = self.filesystem.describe_file(&target.path);
        self.file_rows(&info)
    }

    fn file_rows(&self, info: &FileInfo) -> Vec<DisplayRow> {
        let mut rows = vec![
            DisplayRow {
                text: format!("Name: {}", info.name),
                kind: DisplayRowKind::Info,
                highlighted: false,
            },
            DisplayRow {
                text: format!("Type: {}", info.file_type),
                kind: DisplayRowKind::Info,
                highlighted: false,
            },
            DisplayRow {
                text: format!("Size: {} B", info.size),
                kind: DisplayRowKind::Info,
                highlighted: false,
            },
        ];

        if let Some(error) = &info.error {
            rows.push(DisplayRow {
                text: error.clone(),
                kind: DisplayRowKind::Error,
                highlighted: false,
            });
            return rows;
        }

        rows.extend(info.excerpt.iter().cloned().map(|line| DisplayRow {
            text: line,
            kind: DisplayRowKind::Info,
            highlighted: false,
        }));

        rows
    }
}

fn selected_index(rows: &[DisplayRow]) -> Option<usize> {
    rows.iter().position(|row| row.highlighted)
}
