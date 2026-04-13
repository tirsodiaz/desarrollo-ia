mod common;

use std::fs;

use atrium::{DisplayRenderer, NavigationController, render_display};

use common::TempDir;

const VIEWPORT_HEIGHT: usize = 8;

fn separator_positions(line: &str) -> Vec<usize> {
    let mut positions = Vec::new();
    let mut width = 0;
    for ch in line.chars() {
        if ch == '│' {
            positions.push(width);
        }
        width += match ch {
            '📁' | '📄' => 2,
            _ => 1,
        };
    }
    positions
}

#[test]
fn display_state_contains_parent_current_and_directory_preview() {
    let temp = TempDir::new();
    let parent = temp.path().canonicalize().expect("resolved parent");
    let current = parent.join("current");
    let sibling = parent.join("sibling.txt");
    let child = current.join("child");
    fs::create_dir(&current).expect("create current");
    fs::create_dir(&child).expect("create child");
    fs::write(&sibling, "other").expect("write sibling");
    fs::write(child.join("nested.txt"), "nested").expect("write nested");

    let controller = NavigationController::new(Some(current.clone()));
    let display = controller.build_display_state(28, VIEWPORT_HEIGHT);

    assert_eq!(display.current_path, current.display().to_string());
    assert!(display.center.emphasized);
    assert_eq!(display.left.selected_index, Some(0));
    assert_eq!(
        display
            .left
            .rows
            .iter()
            .map(|row| row.text.as_str())
            .collect::<Vec<_>>(),
        vec!["current", "sibling.txt"]
    );
    assert!(display.left.rows[0].highlighted);
    assert_eq!(
        display
            .center
            .rows
            .iter()
            .map(|row| row.text.as_str())
            .collect::<Vec<_>>(),
        vec!["child"]
    );
    assert!(display.center.rows[0].highlighted);
    assert_eq!(display.center.selected_index, Some(0));
    assert_eq!(
        display
            .right
            .rows
            .iter()
            .map(|row| row.text.as_str())
            .collect::<Vec<_>>(),
        vec!["nested.txt"]
    );
}

#[test]
fn file_selection_shows_metadata_and_text_excerpt() {
    let temp = TempDir::new();
    let root = temp.path();
    fs::write(root.join("note.txt"), "line one\nline two\nline three\n").expect("write note");

    let controller = NavigationController::new(Some(root.to_path_buf()));
    let display = controller.build_display_state(28, VIEWPORT_HEIGHT);

    assert_eq!(
        display.right.rows[..3]
            .iter()
            .map(|row| row.text.as_str())
            .collect::<Vec<_>>(),
        vec!["Name: note.txt", "Type: txt", "Size: 29 B"]
    );
    assert_eq!(
        display.right.rows[3..]
            .iter()
            .map(|row| row.text.as_str())
            .collect::<Vec<_>>(),
        vec!["line one", "line two", "line three"]
    );
}

#[test]
fn none_selection_keeps_preview_blank() {
    let temp = TempDir::new();
    let controller = NavigationController::new(Some(temp.path().to_path_buf()));
    let display = controller.build_display_state(28, VIEWPORT_HEIGHT);

    assert!(display.right.rows.is_empty());
}

#[test]
fn rendered_output_exposes_current_path_and_fixed_width_columns() {
    let temp = TempDir::new();
    let root = temp.path();
    fs::create_dir(root.join("alpha")).expect("create alpha");
    let resolved_root = root.to_path_buf();

    let controller = NavigationController::new(Some(resolved_root.clone()));
    let rendered = render_display(&controller.build_display_state(18, VIEWPORT_HEIGHT), VIEWPORT_HEIGHT);
    let lines = rendered.lines().collect::<Vec<_>>();

    assert!(lines[0].contains(&resolved_root.display().to_string()));
    assert_eq!(lines[1], "");
    assert_eq!(separator_positions(lines[2]), separator_positions(lines[4]));
    assert_eq!(separator_positions(lines[2]), separator_positions(lines[3]));
    assert!(lines[2].contains("[* Current *]"));
    assert!(lines[4].contains("📁 alpha"));
}

#[test]
fn renderer_truncates_long_filenames_with_ellipsis() {
    let mut renderer = DisplayRenderer::new(12);
    let temp = TempDir::new();
    let root = temp.path();
    fs::write(root.join("this-is-a-very-long-file-name.txt"), "payload").expect("write file");

    let controller = NavigationController::new(Some(root.to_path_buf()));
    let rendered = renderer.render_to_string(&controller.build_display_state(12, VIEWPORT_HEIGHT), VIEWPORT_HEIGHT);

    assert!(rendered.contains('…'));
}
