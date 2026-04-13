use std::env;
use std::path::PathBuf;

use crate::filesystem::Filesystem;
use crate::models::Entry;

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct AppState {
    pub current_dir: PathBuf,
    pub parent_dir: Option<PathBuf>,
    pub current_entries: Vec<Entry>,
    pub selected: Option<Entry>,
    pub preview_target: Option<Entry>,
    pub current_error: Option<String>,
}

pub fn build_initial_state(start_path: Option<PathBuf>, filesystem: &impl Filesystem) -> AppState {
    let start_path = start_path.unwrap_or_else(|| env::current_dir().expect("current directory"));
    let listing = filesystem.list_directory(&start_path);
    let current_dir = listing.path;
    let selected = listing.entries.first().cloned();

    AppState {
        parent_dir: current_dir.parent().map(|path| path.to_path_buf()),
        current_dir,
        current_entries: listing.entries,
        selected: selected.clone(),
        preview_target: selected,
        current_error: listing.error,
    }
}
