from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for
import yaml

app = Flask(__name__)
DATA_FILE = Path(__file__).with_name("todo-items.yaml")


def load_todo_items() -> list[dict]:
    """Load todo items from YAML file.

    Supports both the original format (list of strings) and
    the extended format (list of objects with text/done).
    """
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    items = data.get("items", [])
    if not isinstance(items, list):
        return []

    normalized_items: list[dict] = []
    for item in items:
        if isinstance(item, dict):
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            done = bool(item.get("done", False))
            normalized_items.append({"text": text, "done": done})
        else:
            text = str(item).strip()
            if not text:
                continue
            normalized_items.append({"text": text, "done": False})

    return normalized_items


def save_todo_items(items: list[dict]) -> None:
    """Persist todo items to YAML file in a stable structure."""
    data = {"items": []}
    for item in items:
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        data["items"].append({"text": text, "done": bool(item.get("done", False))})

    with DATA_FILE.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)


@app.route("/", methods=["GET", "POST"])
def index():
    items = load_todo_items()

    if request.method == "POST":
        new_text = (request.form.get("title") or "").strip()
        if new_text:
            items.append({"text": new_text, "done": False})
            save_todo_items(items)
        return redirect(url_for("index"))

    return render_template("index.html", todo_items=items)


@app.route("/complete/<int:item_id>", methods=["POST"])
def complete_item(item_id: int):
    items = load_todo_items()
    if 0 <= item_id < len(items):
        items[item_id]["done"] = True
        save_todo_items(items)
    return redirect(url_for("index"))


@app.route("/add", methods=["POST"])
def add():
    texto = request.form.get("texto", "").strip()
    if texto:
        items = load_todo_items()
        items.append({"texto": texto, "completada": False})
        save_todo_items(items)
    return redirect(url_for("index"))


@app.route("/complete/<int:index>", methods=["POST"])
def complete(index):
    items = load_todo_items()
    if 0 <= index < len(items):
        items[index]["completada"] = True
        save_todo_items(items)
    return redirect(url_for("index"))


@app.route("/undo/<int:index>", methods=["POST"])
def undo(index):
    items = load_todo_items()
    if 0 <= index < len(items):
        items[index]["completada"] = False
        save_todo_items(items)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
