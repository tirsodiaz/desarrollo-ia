use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use crate::models::Entry;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DirectoryListing {
    pub path: PathBuf,
    pub entries: Vec<Entry>,
    pub error: Option<String>,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct FileInfo {
    pub name: String,
    pub file_type: String,
    pub size: u64,
    pub excerpt: Vec<String>,
    pub error: Option<String>,
}

pub trait Filesystem {
    fn list_directory(&self, path: &Path) -> DirectoryListing;
    fn describe_file(&self, path: &Path) -> FileInfo;
}

#[derive(Clone, Copy, Debug, Default)]
pub struct FilesystemAdapter;

impl FilesystemAdapter {
    fn resolve_path(path: &Path) -> PathBuf {
        path.canonicalize().unwrap_or_else(|_| path.to_path_buf())
    }
}

impl Filesystem for FilesystemAdapter {
    fn list_directory(&self, path: &Path) -> DirectoryListing {
        let resolved = Self::resolve_path(path);
        let read_dir = match fs::read_dir(&resolved) {
            Ok(read_dir) => read_dir,
            Err(error) => {
                return DirectoryListing {
                    path: resolved,
                    entries: Vec::new(),
                    error: Some(read_error_message(&error)),
                };
            }
        };

        let mut entries = read_dir
            .filter_map(|child| child.ok())
            .map(|child| Entry::from_path(&child.path()))
            .collect::<Vec<_>>();

        entries.sort_by(|left, right| {
            (!left.is_dir, left.name.to_lowercase())
                .cmp(&(!right.is_dir, right.name.to_lowercase()))
        });

        DirectoryListing {
            path: resolved,
            entries,
            error: None,
        }
    }

    fn describe_file(&self, path: &Path) -> FileInfo {
        let resolved = Self::resolve_path(path);
        let size = fs::metadata(&resolved)
            .map(|metadata| metadata.len())
            .unwrap_or(0);
        let file_type = resolved
            .extension()
            .and_then(|extension| extension.to_str())
            .filter(|extension| !extension.is_empty())
            .unwrap_or("file")
            .to_string();

        let sample = match fs::read(&resolved) {
            Ok(bytes) => bytes.into_iter().take(4096).collect::<Vec<_>>(),
            Err(error) => {
                return FileInfo {
                    name: resolved
                        .file_name()
                        .unwrap_or_default()
                        .to_string_lossy()
                        .into_owned(),
                    file_type,
                    size,
                    excerpt: Vec::new(),
                    error: Some(read_error_message(&error)),
                };
            }
        };

        let excerpt = if sample.contains(&0) {
            Vec::new()
        } else {
            String::from_utf8(sample)
                .ok()
                .map(|text| text.lines().take(5).map(ToOwned::to_owned).collect())
                .unwrap_or_default()
        };

        FileInfo {
            name: resolved
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned(),
            file_type,
            size,
            excerpt,
            error: None,
        }
    }
}

fn read_error_message(error: &io::Error) -> String {
    match error.kind() {
        io::ErrorKind::PermissionDenied => "Permission denied".to_string(),
        _ => error.to_string(),
    }
}
