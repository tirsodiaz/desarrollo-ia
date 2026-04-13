mod common;

use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

use atrium::{DirectoryListing, Entry, FileInfo, Filesystem, NavigationController};

use common::TempDir;

#[derive(Clone, Default)]
struct FakeFilesystem {
    listings: HashMap<PathBuf, DirectoryListing>,
    files: HashMap<PathBuf, FileInfo>,
}

impl Filesystem for FakeFilesystem {
    fn list_directory(&self, path: &Path) -> DirectoryListing {
        self.listings[&path.to_path_buf()].clone()
    }

    fn describe_file(&self, path: &Path) -> FileInfo {
        self.files[&path.to_path_buf()].clone()
    }
}

#[test]
fn vertical_movement_updates_selection_and_preview() {
    let temp = TempDir::new();
    let root = temp.path();
    fs::create_dir(root.join("alpha")).expect("create alpha");
    fs::create_dir(root.join("beta")).expect("create beta");

    let mut controller = NavigationController::new(Some(root.to_path_buf()));

    assert_eq!(
        controller
            .state
            .selected
            .as_ref()
            .map(|entry| entry.name.as_str()),
        Some("alpha")
    );
    controller.move_down();
    assert_eq!(
        controller
            .state
            .selected
            .as_ref()
            .map(|entry| entry.name.as_str()),
        Some("beta")
    );
    assert_eq!(controller.state.preview_target, controller.state.selected);
    controller.move_up();
    assert_eq!(
        controller
            .state
            .selected
            .as_ref()
            .map(|entry| entry.name.as_str()),
        Some("alpha")
    );
}

#[test]
fn enter_directory_loads_it_as_the_new_center_column() {
    let temp = TempDir::new();
    let root = temp.path().canonicalize().expect("resolved root");
    let child = root.join("child");
    fs::create_dir(&child).expect("create child");
    fs::write(child.join("inside.txt"), "hello").expect("write file");

    let mut controller = NavigationController::new(Some(root.clone()));

    assert!(controller.enter_selection());
    assert_eq!(controller.state.parent_dir, Some(root.clone()));
    assert_eq!(controller.state.current_dir, child);
    assert_eq!(
        controller
            .state
            .current_entries
            .iter()
            .map(|entry| entry.name.as_str())
            .collect::<Vec<_>>(),
        vec!["inside.txt"]
    );
    assert_eq!(
        controller
            .state
            .selected
            .as_ref()
            .map(|entry| entry.name.as_str()),
        Some("inside.txt")
    );
}

#[test]
fn enter_on_file_is_ignored() {
    let temp = TempDir::new();
    let root = temp.path();
    let file_path = root.join("note.txt");
    fs::write(&file_path, "hello").expect("write file");

    let mut controller = NavigationController::new(Some(root.to_path_buf()));
    let before = controller.state.current_dir.clone();

    assert!(!controller.enter_selection());
    assert_eq!(controller.state.current_dir, before);
    assert_eq!(
        controller
            .state
            .selected
            .as_ref()
            .map(|entry| entry.path.clone()),
        Some(file_path.canonicalize().expect("resolved file"))
    );
}

#[test]
fn returning_to_parent_restores_the_directory_just_exited() {
    let temp = TempDir::new();
    let root = temp.path().canonicalize().expect("resolved root");
    let first = root.join("first");
    let second = root.join("second");
    fs::create_dir(&first).expect("create first");
    fs::create_dir(&second).expect("create second");
    fs::write(first.join("child.txt"), "hello").expect("write file");

    let mut controller = NavigationController::new(Some(root.clone()));
    assert!(controller.enter_selection());

    assert!(controller.go_parent());
    assert_eq!(controller.state.current_dir, root);
    assert_eq!(
        controller
            .state
            .selected
            .as_ref()
            .map(|entry| entry.path.clone()),
        Some(first.clone())
    );
    assert_eq!(
        controller
            .state
            .preview_target
            .as_ref()
            .map(|entry| entry.path.clone()),
        Some(first)
    );
}

#[test]
fn root_navigation_is_stable() {
    let mut controller = NavigationController::new(Some(PathBuf::from("/")));
    let before = controller.state.current_dir.clone();

    assert!(!controller.go_parent());
    assert_eq!(controller.state.current_dir, before);
    assert!(controller.state.parent_dir.is_none());
}

#[test]
fn permission_error_is_captured_without_breaking_navigation() {
    let root = PathBuf::from("/virtual");
    let denied = root.join("denied");
    let sibling = root.join("sibling");

    let fake = FakeFilesystem {
        listings: HashMap::from([
            (
                root.clone(),
                DirectoryListing {
                    path: root.clone(),
                    entries: vec![
                        Entry {
                            name: "denied".to_string(),
                            path: denied.clone(),
                            is_dir: true,
                        },
                        Entry {
                            name: "sibling".to_string(),
                            path: sibling.clone(),
                            is_dir: true,
                        },
                    ],
                    error: None,
                },
            ),
            (
                denied.clone(),
                DirectoryListing {
                    path: denied.clone(),
                    entries: Vec::new(),
                    error: Some("Permission denied".to_string()),
                },
            ),
            (
                sibling,
                DirectoryListing {
                    path: root.join("sibling"),
                    entries: Vec::new(),
                    error: None,
                },
            ),
        ]),
        files: HashMap::new(),
    };

    let mut controller = NavigationController::with_filesystem(Some(root.clone()), fake);

    assert!(controller.enter_selection());
    assert_eq!(controller.state.current_dir, denied);
    assert!(controller.state.current_entries.is_empty());
    assert_eq!(
        controller.state.current_error.as_deref(),
        Some("Permission denied")
    );
    assert!(controller.state.selected.is_none());
    assert!(controller.go_parent());
    assert_eq!(controller.state.current_dir, root);
    assert!(controller.state.current_error.is_none());
}
