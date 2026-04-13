mod common;

use std::fs;

use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

use atrium::{AtriumApp, DisplayRenderer};

use common::TempDir;

#[test]
fn display_renderer_is_pure_projection() {
    let mut renderer = DisplayRenderer::new(16);
    let state = AtriumApp::new(Some("/".into()))
        .controller
        .build_display_state(16, 8);

    let first = renderer.render_to_string(&state, 8);
    let second = renderer.render_to_string(&state, 8);

    assert_eq!(first, second);
}

#[test]
fn app_updates_from_controller_actions() {
    let temp = TempDir::new();
    let root = temp.path();
    fs::create_dir(root.join("alpha")).expect("create alpha");
    fs::create_dir(root.join("beta")).expect("create beta");

    let mut app = AtriumApp::new(Some(root.to_path_buf()));
    app.refresh_display();
    assert!(app.last_rendered.contains("▶ 📁 alpha"));

    assert!(app.handle_key_event(KeyEvent::new(KeyCode::Down, KeyModifiers::NONE)));
    assert!(app.last_rendered.contains("▶ 📁 beta"));
}

#[test]
fn app_enters_directory_and_returns_to_parent() {
    let temp = TempDir::new();
    let root = temp.path().canonicalize().expect("resolved root");
    let child = root.join("child");
    fs::create_dir(&child).expect("create child");
    fs::write(child.join("inside.txt"), "payload").expect("write inside");

    let mut app = AtriumApp::new(Some(root.clone()));
    app.refresh_display();

    assert!(app.handle_key_event(KeyEvent::new(KeyCode::Enter, KeyModifiers::NONE)));
    assert!(app.last_rendered.contains(&child.display().to_string()));
    assert!(app.last_rendered.contains("▶ 📄 inside.txt"));

    assert!(app.handle_key_event(KeyEvent::new(KeyCode::Left, KeyModifiers::NONE)));
    assert!(app.last_rendered.contains(&root.display().to_string()));
    assert!(app.last_rendered.contains("▶ 📁 child"));
}

#[test]
fn app_quits_on_q_and_ctrl_c() {
    let mut app = AtriumApp::new(Some("/".into()));

    assert!(!app.handle_key_event(KeyEvent::new(KeyCode::Char('q'), KeyModifiers::NONE)));
    assert!(!app.handle_key_event(KeyEvent::new(KeyCode::Char('c'), KeyModifiers::CONTROL)));
}
