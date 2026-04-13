use std::io::{self, Write};

use crossterm::{
    cursor::MoveTo,
    queue,
    style::{Attribute, Color, Print, ResetColor, SetAttribute, SetForegroundColor},
    terminal::{self, Clear, ClearType},
};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum DisplayRowKind {
    Directory,
    Empty,
    Error,
    File,
    Info,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DisplayRow {
    pub text: String,
    pub kind: DisplayRowKind,
    pub highlighted: bool,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DisplayColumn {
    pub title: String,
    pub rows: Vec<DisplayRow>,
    pub emphasized: bool,
    pub selected_index: Option<usize>,
    pub scroll_offset: usize,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct DisplayState {
    pub current_path: String,
    pub column_width: usize,
    pub left: DisplayColumn,
    pub center: DisplayColumn,
    pub right: DisplayColumn,
}

#[derive(Clone, Debug)]
pub struct DisplayRenderer {
    column_width: usize,
    unicode: bool,
    color: bool,
    center_scroll_offset: usize,
}

impl Default for DisplayRenderer {
    fn default() -> Self {
        Self {
            column_width: 28,
            unicode: unicode_supported(),
            color: color_supported(),
            center_scroll_offset: 0,
        }
    }
}

impl DisplayRenderer {
    pub fn new(column_width: usize) -> Self {
        Self {
            column_width,
            ..Self::default()
        }
    }

    pub fn column_width(&self) -> usize {
        self.column_width
    }

    pub fn reset_center_scroll(&mut self) {
        self.center_scroll_offset = 0;
    }

    pub fn render_to_string(&mut self, state: &DisplayState, viewport_height: usize) -> String {
        let layout = RenderLayout::from_state(
            state,
            self.unicode,
            viewport_height,
            &mut self.center_scroll_offset,
        );
        layout.to_plain_string()
    }

    pub fn render<W, B>(&mut self, writer: &mut W, build_state: B) -> io::Result<()>
    where
        W: Write,
        B: FnOnce(usize) -> DisplayState,
    {
        let viewport_height = terminal::size()
            .map(|(_, rows)| viewport_height(rows))
            .unwrap_or(DEFAULT_VIEWPORT_HEIGHT);
        let state = build_state(viewport_height);
        let layout = RenderLayout::from_state(
            &state,
            self.unicode,
            viewport_height,
            &mut self.center_scroll_offset,
        );
        queue!(writer, MoveTo(0, 0), Clear(ClearType::All))?;
        queue!(
            writer,
            Print(format!("Path: {}\r\n\r\n", state.current_path))
        )?;
        self.write_row(writer, &layout.header)?;
        queue!(writer, Print("\r\n"))?;
        queue!(writer, Print(layout.separator.clone()), Print("\r\n"))?;

        for row in &layout.body {
            self.write_row(writer, row)?;
            queue!(writer, Print("\r\n"))?;
        }

        writer.flush()
    }

    fn write_row<W: Write>(&self, writer: &mut W, row: &RenderedRow) -> io::Result<()> {
        let vertical = if self.unicode { "│" } else { "|" };
        queue!(writer, Print(vertical), Print(" "))?;

        for (index, cell) in row.cells.iter().enumerate() {
            if self.color {
                if cell.emphasized {
                    queue!(
                        writer,
                        SetForegroundColor(Color::Cyan),
                        SetAttribute(Attribute::Bold)
                    )?;
                } else if cell.highlighted {
                    queue!(
                        writer,
                        SetForegroundColor(Color::Yellow),
                        SetAttribute(Attribute::Bold)
                    )?;
                } else {
                    let color = match cell.kind {
                        DisplayRowKind::Directory => Color::Blue,
                        DisplayRowKind::Error => Color::Red,
                        DisplayRowKind::Empty | DisplayRowKind::Info => Color::DarkGrey,
                        DisplayRowKind::File => Color::White,
                    };
                    queue!(
                        writer,
                        SetForegroundColor(color),
                        SetAttribute(Attribute::Reset)
                    )?;
                }
            }

            queue!(writer, Print(&cell.text))?;

            if self.color {
                queue!(writer, ResetColor, SetAttribute(Attribute::Reset))?;
            }

            queue!(writer, Print(" "))?;
            queue!(writer, Print(vertical))?;
            if index + 1 != row.cells.len() {
                queue!(writer, Print(" "))?;
            }
        }

        Ok(())
    }
}

pub fn render_display(state: &DisplayState, viewport_height: usize) -> String {
    DisplayRenderer::default().render_to_string(state, viewport_height)
}

#[derive(Clone, Debug)]
struct RenderedCell {
    text: String,
    kind: DisplayRowKind,
    highlighted: bool,
    emphasized: bool,
}

#[derive(Clone, Debug)]
struct RenderedRow {
    cells: Vec<RenderedCell>,
}

#[derive(Clone, Debug)]
struct RenderLayout {
    current_path: String,
    header: RenderedRow,
    separator: String,
    body: Vec<RenderedRow>,
    vertical: &'static str,
}

impl RenderLayout {
    fn from_state(
        state: &DisplayState,
        unicode: bool,
        viewport_height: usize,
        center_scroll_offset: &mut usize,
    ) -> Self {
        let columns = [&state.left, &state.center, &state.right];
        let header = RenderedRow {
            cells: columns
                .iter()
                .map(|column| RenderedCell {
                    text: fit(&title_text(column), state.column_width),
                    kind: DisplayRowKind::Info,
                    highlighted: false,
                    emphasized: column.emphasized,
                })
                .collect(),
        };
        let separator_char = if unicode { "─" } else { "-" };
        let vertical = if unicode { "│" } else { "|" };
        let separator_segment = separator_char.repeat(state.column_width + 2);
        let separator = format!(
            "{vertical}{}{vertical}",
            vec![separator_segment; columns.len()].join(vertical)
        );
        let visible_columns = [
            visible_rows(&state.left, viewport_height, None),
            visible_rows(
                &state.center,
                viewport_height,
                Some(center_scroll_offset),
            ),
            visible_rows(&state.right, viewport_height, None),
        ];

        let mut body = Vec::with_capacity(viewport_height);
        for index in 0..viewport_height {
            body.push(RenderedRow {
                cells: visible_columns
                    .iter()
                    .map(|column| {
                        let row = column.get(index).and_then(|row| row.as_ref().copied());
                        let kind = row.map(|row| row.kind).unwrap_or(DisplayRowKind::Info);
                        RenderedCell {
                            text: fit(&row_text(row, unicode), state.column_width),
                            kind,
                            highlighted: row.is_some_and(|row| row.highlighted),
                            emphasized: false,
                        }
                    })
                    .collect(),
            });
        }

        Self {
            current_path: state.current_path.clone(),
            header,
            separator,
            body,
            vertical,
        }
    }

    fn to_plain_string(&self) -> String {
        let mut lines = Vec::with_capacity(4 + self.body.len());
        lines.push(format!("Path: {}", self.current_path));
        lines.push(String::new());
        lines.push(framed_row(&self.header, self.vertical));
        lines.push(self.separator.clone());
        lines.extend(self.body.iter().map(|row| framed_row(row, self.vertical)));
        lines.join("\n")
    }
}

fn title_text(column: &DisplayColumn) -> String {
    if column.emphasized {
        format!("[* {} *]", column.title)
    } else {
        column.title.clone()
    }
}

fn row_text(row: Option<&DisplayRow>, unicode: bool) -> String {
    let Some(row) = row else {
        return String::new();
    };

    let marker = if row.highlighted {
        if unicode { "▶" } else { ">" }
    } else {
        " "
    };
    let icon = match row.kind {
        DisplayRowKind::Directory => {
            if unicode {
                "📁"
            } else {
                "[D]"
            }
        }
        DisplayRowKind::File => {
            if unicode {
                "📄"
            } else {
                "[F]"
            }
        }
        DisplayRowKind::Error => {
            if unicode {
                "!"
            } else {
                "[!]"
            }
        }
        DisplayRowKind::Empty => {
            if unicode {
                " "
            } else {
                "[ ]"
            }
        }
        DisplayRowKind::Info => " ",
    };

    if matches!(row.kind, DisplayRowKind::Info | DisplayRowKind::Empty) {
        format!("{marker} {}", row.text)
    } else {
        format!("{marker} {icon} {}", row.text)
    }
}

fn fit(text: &str, width: usize) -> String {
    let text_width = display_width(text);
    if text_width <= width {
        return pad_to_width(text, width);
    }

    let mut truncated = String::new();
    let mut current_width = 0;
    let limit = width.saturating_sub(1);
    for ch in text.chars() {
        let ch_width = char_width(ch);
        if current_width + ch_width > limit {
            break;
        }
        truncated.push(ch);
        current_width += ch_width;
    }
    truncated.push('…');
    pad_to_width(&truncated, width)
}

fn pad_to_width(text: &str, width: usize) -> String {
    let pad = width.saturating_sub(display_width(text));
    format!("{text}{}", " ".repeat(pad))
}

fn display_width(text: &str) -> usize {
    text.chars().map(char_width).sum()
}

fn char_width(ch: char) -> usize {
    match ch {
        '📁' | '📄' => 2,
        _ => 1,
    }
}

fn unicode_supported() -> bool {
    std::env::var("LC_ALL")
        .or_else(|_| std::env::var("LANG"))
        .map(|value| value.to_uppercase().contains("UTF-8"))
        .unwrap_or(true)
}

fn color_supported() -> bool {
    std::env::var("NO_COLOR").is_err()
}

fn framed_row(row: &RenderedRow, vertical: &str) -> String {
    let contents = row
        .cells
        .iter()
        .map(|cell| cell.text.clone())
        .collect::<Vec<_>>()
        .join(&format!(" {vertical} "));
    format!("{vertical} {contents} {vertical}")
}

const DEFAULT_VIEWPORT_HEIGHT: usize = 10;

pub fn viewport_height(rows: u16) -> usize {
    usize::from(rows).saturating_sub(4)
}

fn visible_rows<'a>(
    column: &'a DisplayColumn,
    viewport_height: usize,
    persisted_offset: Option<&mut usize>,
) -> Vec<Option<&'a DisplayRow>> {
    if viewport_height == 0 {
        if let Some(offset) = persisted_offset {
            *offset = 0;
        }
        return Vec::new();
    }

    let starting_offset = persisted_offset.as_ref().map_or(0, |offset| **offset);
    let resolved_offset = resolve_scroll_offset(
        column.rows.len(),
        column.selected_index,
        starting_offset,
        viewport_height,
    );

    if let Some(offset) = persisted_offset {
        *offset = resolved_offset;
    }

    (0..viewport_height)
        .map(|index| column.rows.get(resolved_offset + index))
        .collect()
}

fn resolve_scroll_offset(
    item_count: usize,
    selected_index: Option<usize>,
    scroll_offset: usize,
    viewport_height: usize,
) -> usize {
    if viewport_height == 0 {
        return 0;
    }

    let max_offset = item_count.saturating_sub(viewport_height);
    let mut offset = scroll_offset.min(max_offset);

    if let Some(selected_index) = selected_index {
        if selected_index < offset {
            offset = selected_index;
        }
        if selected_index >= offset + viewport_height {
            offset = selected_index + 1 - viewport_height;
        }
    }

    offset.min(max_offset)
}
