mod common;

use std::fs;

use atrium::FilesystemAdapter;
use atrium::build_initial_state;

use common::TempDir;

#[test]
fn initial_state_defaults_to_working_directory() {
    let initial = build_initial_state(None, &FilesystemAdapter);

    assert_eq!(
        initial.current_dir,
        std::env::current_dir()
            .expect("cwd")
            .canonicalize()
            .expect("resolved cwd")
    );
    assert_eq!(
        initial.parent_dir,
        std::env::current_dir()
            .expect("cwd")
            .canonicalize()
            .expect("resolved cwd")
            .parent()
            .map(|path| path.to_path_buf())
    );
}

#[test]
fn first_entry_is_selected_automatically() {
    let temp = TempDir::new();
    let root = temp.path();
    fs::write(root.join("b-file.txt"), "payload").expect("write file");
    fs::create_dir(root.join("a-dir")).expect("create dir");

    let initial = build_initial_state(Some(root.to_path_buf()), &FilesystemAdapter);

    assert_eq!(
        initial
            .current_entries
            .iter()
            .map(|entry| entry.name.as_str())
            .collect::<Vec<_>>(),
        vec!["a-dir", "b-file.txt"]
    );
    assert_eq!(
        initial.selected.as_ref().map(|entry| entry.name.as_str()),
        Some("a-dir")
    );
    assert_eq!(initial.preview_target, initial.selected);
}

#[test]
fn empty_directory_has_no_selection() {
    let temp = TempDir::new();

    let initial = build_initial_state(Some(temp.path().to_path_buf()), &FilesystemAdapter);

    assert!(initial.current_entries.is_empty());
    assert!(initial.selected.is_none());
    assert!(initial.preview_target.is_none());
}
