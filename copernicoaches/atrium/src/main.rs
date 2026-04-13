use std::io;

use atrium::AtriumApp;

fn main() -> io::Result<()> {
    let mut app = AtriumApp::new(None);
    app.run()
}
