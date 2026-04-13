mod common;

use std::fs;

use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

use atrium::{AtriumApp, DisplayRenderer, NavigationController};

use common::TempDir;

const VIEWPORT_HEIGHT: usize = 4;

fn center_column_rows(rendered: &str) -> Vec<String> {
    rendered
        .lines()
        .skip(4)
        .map(|line| {
            line.split('│')
                .nth(2)
                .expect("center column")
                .trim()
                .to_string()
        })
        .collect()
}

#[test]
fn renderer_clips_body_to_viewport_height() {
    let temp = TempDir::new();
    let root = temp.path();
    for index in 0..10 {
        fs::create_dir(root.join(format!("dir-{index:02}"))).expect("create dir");
    }

    let mut renderer = DisplayRenderer::new(18);
    let controller = NavigationController::new(Some(root.to_path_buf()));
    let rendered = renderer.render_to_string(
        &controller.build_display_state(18, VIEWPORT_HEIGHT),
        VIEWPORT_HEIGHT,
    );

    assert_eq!(rendered.lines().count(), VIEWPORT_HEIGHT + 4);
}

#[test]
fn moving_down_scrolls_only_when_selection_leaves_viewport() {
    let temp = TempDir::new();
    let root = temp.path();
    for index in 0..8 {
        fs::create_dir(root.join(format!("dir-{index:02}"))).expect("create dir");
    }

    let mut renderer = DisplayRenderer::new(18);
    let mut controller = NavigationController::new(Some(root.to_path_buf()));

    let initial = renderer.render_to_string(
        &controller.build_display_state(18, VIEWPORT_HEIGHT),
        VIEWPORT_HEIGHT,
    );
    let initial_rows = center_column_rows(&initial);
    assert!(initial_rows[0].contains("▶ 📁 dir-00"));
    assert!(initial_rows[3].contains("dir-03"));

    for _ in 0..3 {
        controller.move_down();
    }
    let still_visible = renderer.render_to_string(
        &controller.build_display_state(18, VIEWPORT_HEIGHT),
        VIEWPORT_HEIGHT,
    );
    let still_visible_rows = center_column_rows(&still_visible);
    assert!(still_visible_rows[0].contains("dir-00"));
    assert!(still_visible_rows[3].contains("▶ 📁 dir-03"));

    controller.move_down();
    let scrolled = renderer.render_to_string(
        &controller.build_display_state(18, VIEWPORT_HEIGHT),
        VIEWPORT_HEIGHT,
    );
    let scrolled_rows = center_column_rows(&scrolled);
    assert!(scrolled_rows[0].contains("dir-01"));
    assert!(scrolled_rows[3].contains("▶ 📁 dir-04"));

    controller.move_up();
    let no_recentering = renderer.render_to_string(
        &controller.build_display_state(18, VIEWPORT_HEIGHT),
        VIEWPORT_HEIGHT,
    );
    let no_recentering_rows = center_column_rows(&no_recentering);
    assert!(no_recentering_rows[0].contains("dir-01"));
    assert!(no_recentering_rows[2].contains("▶ 📁 dir-03"));
}

#[test]
fn left_column_computes_visibility_from_highlighted_path_each_render() {
    let temp = TempDir::new();
    let parent = temp.path();
    for index in 0..8 {
        fs::create_dir(parent.join(format!("dir-{index:02}"))).expect("create dir");
    }
    let current = parent.join("dir-06");

    let mut renderer = DisplayRenderer::new(18);
    let controller = NavigationController::new(Some(current));
    let rendered = renderer.render_to_string(
        &controller.build_display_state(18, VIEWPORT_HEIGHT),
        VIEWPORT_HEIGHT,
    );
    let left_rows = rendered
        .lines()
        .skip(4)
        .map(|line| {
            line.split('│')
                .nth(1)
                .expect("left column")
                .trim()
                .to_string()
        })
        .collect::<Vec<_>>();

    assert!(left_rows.iter().any(|row| row.contains("▶ 📁 dir-06")));
}

#[test]
fn entering_and_leaving_directory_resets_center_scroll() {
    let temp = TempDir::new();
    let root = temp.path();
    let child = root.join("child");
    fs::create_dir(&child).expect("create child");
    for index in 0..8 {
        fs::create_dir(root.join(format!("dir-{index:02}"))).expect("create dir");
        fs::write(child.join(format!("file-{index:02}.txt")), "payload").expect("write file");
    }

    let mut app = AtriumApp::new(Some(root.to_path_buf()));
    for _ in 0..4 {
        assert!(app.handle_key_event(KeyEvent::new(
            KeyCode::Down,
            KeyModifiers::NONE,
        )));
    }

    let scrolled = app.renderer.render_to_string(
        &app.controller.build_display_state(18, VIEWPORT_HEIGHT),
        VIEWPORT_HEIGHT,
    );
    assert!(center_column_rows(&scrolled)[0].contains("dir-00"));

    while app.controller.state.selected.as_ref().map(|entry| entry.name.as_str()) != Some("child") {
        assert!(app.handle_key_event(KeyEvent::new(
            KeyCode::Up,
            KeyModifiers::NONE,
        )));
    }

    assert!(app.handle_key_event(KeyEvent::new(
        KeyCode::Enter,
        KeyModifiers::NONE,
    )));
    let entered = app
        .renderer
        .render_to_string(&app.controller.build_display_state(18, VIEWPORT_HEIGHT), VIEWPORT_HEIGHT);
    assert!(center_column_rows(&entered)[0].contains("▶ 📄 file-00.txt"));

    assert!(app.handle_key_event(KeyEvent::new(
        KeyCode::Left,
        KeyModifiers::NONE,
    )));
    let returned = app
        .renderer
        .render_to_string(&app.controller.build_display_state(18, VIEWPORT_HEIGHT), VIEWPORT_HEIGHT);
    assert!(center_column_rows(&returned)[0].contains("▶ 📁 child"));
}
