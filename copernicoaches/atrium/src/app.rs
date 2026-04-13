use std::io::{self, Write, stdout};
use std::panic;
use std::path::PathBuf;
use std::sync::Once;

use crossterm::{
    cursor::{Hide, Show},
    event::{self, Event, KeyCode, KeyEvent, KeyModifiers},
    execute,
    terminal::{
        self, EnterAlternateScreen, LeaveAlternateScreen, disable_raw_mode, enable_raw_mode,
    },
};

use crate::controller::NavigationController;
use crate::display::DisplayRenderer;
use crate::filesystem::{Filesystem, FilesystemAdapter};

static PANIC_HOOK: Once = Once::new();

pub struct AtriumApp<F: Filesystem = FilesystemAdapter> {
    pub controller: NavigationController<F>,
    pub renderer: DisplayRenderer,
    pub last_rendered: String,
}

impl AtriumApp<FilesystemAdapter> {
    pub fn new(start_path: Option<PathBuf>) -> Self {
        Self::with_filesystem(start_path, FilesystemAdapter)
    }
}

impl<F: Filesystem> AtriumApp<F> {
    pub fn with_filesystem(start_path: Option<PathBuf>, filesystem: F) -> Self {
        let controller = NavigationController::with_filesystem(start_path, filesystem);
        let mut renderer = DisplayRenderer::default();
        let viewport_height = current_viewport_height().unwrap_or(DEFAULT_VIEWPORT_HEIGHT);
        let last_rendered = renderer.render_to_string(
            &controller.build_display_state(renderer.column_width(), viewport_height),
            viewport_height,
        );

        Self {
            controller,
            renderer,
            last_rendered,
        }
    }

    pub fn refresh_display(&mut self) {
        let viewport_height = current_viewport_height().unwrap_or(DEFAULT_VIEWPORT_HEIGHT);
        self.last_rendered = self.renderer.render_to_string(
            &self
                .controller
                .build_display_state(self.renderer.column_width(), viewport_height),
            viewport_height,
        );
    }

    pub fn handle_key_event(&mut self, key: KeyEvent) -> bool {
        match key.code {
            KeyCode::Up => self.controller.move_up(),
            KeyCode::Down => self.controller.move_down(),
            KeyCode::Left | KeyCode::Backspace => {
                if self.controller.go_parent() {
                    self.renderer.reset_center_scroll();
                }
            }
            KeyCode::Right | KeyCode::Enter => {
                if self.controller.enter_selection() {
                    self.renderer.reset_center_scroll();
                }
            }
            KeyCode::Char('q') => return false,
            KeyCode::Char('c') if key.modifiers.contains(KeyModifiers::CONTROL) => return false,
            _ => return true,
        }

        self.refresh_display();
        true
    }

    pub fn run(&mut self) -> io::Result<()> {
        install_panic_hook();
        let _terminal = TerminalSession::enter()?;
        let mut stdout = stdout();
        self.refresh_display();
        let column_width = self.renderer.column_width();
        self.renderer
            .render(&mut stdout, |viewport_height| {
                self.controller
                    .build_display_state(column_width, viewport_height)
            })?;
        stdout.flush()?;

        loop {
            match event::read()? {
                Event::Key(key) => {
                    if !self.handle_key_event(key) {
                        break;
                    }
                    let column_width = self.renderer.column_width();
                    self.renderer.render(&mut stdout, |viewport_height| {
                        self.controller
                            .build_display_state(column_width, viewport_height)
                    })?;
                    stdout.flush()?;
                }
                Event::Resize(_, _) => {
                    self.refresh_display();
                    let column_width = self.renderer.column_width();
                    self.renderer.render(&mut stdout, |viewport_height| {
                        self.controller
                            .build_display_state(column_width, viewport_height)
                    })?;
                    stdout.flush()?;
                }
                _ => {}
            }
        }

        Ok(())
    }
}

struct TerminalSession;

impl TerminalSession {
    fn enter() -> io::Result<Self> {
        enable_raw_mode()?;
        execute!(stdout(), EnterAlternateScreen, Hide)?;
        Ok(Self)
    }
}

impl Drop for TerminalSession {
    fn drop(&mut self) {
        let _ = disable_raw_mode();
        let _ = execute!(stdout(), Show, LeaveAlternateScreen);
    }
}

fn install_panic_hook() {
    PANIC_HOOK.call_once(|| {
        let previous_hook = panic::take_hook();
        panic::set_hook(Box::new(move |panic_info| {
            let _ = disable_raw_mode();
            let _ = execute!(stdout(), Show, LeaveAlternateScreen);
            previous_hook(panic_info);
        }));
    });
}

const DEFAULT_VIEWPORT_HEIGHT: usize = 10;

fn current_viewport_height() -> io::Result<usize> {
    terminal::size().map(|(_, rows)| usize::from(rows).saturating_sub(4))
}
