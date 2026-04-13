use std::ffi::OsStr;
use std::path::{Path, PathBuf};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct Entry {
    pub name: String,
    pub path: PathBuf,
    pub is_dir: bool,
}

impl Entry {
    pub fn from_path(path: &Path) -> Self {
        let resolved = path.canonicalize().unwrap_or_else(|_| path.to_path_buf());
        let name = resolved
            .file_name()
            .unwrap_or_else(|| OsStr::new("/"))
            .to_string_lossy()
            .into_owned();

        Self {
            name,
            is_dir: resolved.is_dir(),
            path: resolved,
        }
    }
}
