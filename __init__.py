from aqt import gui_hooks, mw
from typing import List, Tuple, Union
from aqt.editor import Editor
from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QPushButton,
    QLabel,          # ← MANQUANT
    QButtonGroup,
    QListWidget,
    QListView,
    QSize,
    QPixmap,
    QIcon,
    QListWidgetItem,
    Qt,
    QUrl,
)
from PyQt6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkRequest
)
from aqt.utils import showInfo
from typing import Tuple
import os
import tempfile
import pathlib
import json
import requests
import re


asset_dir = os.path.join(pathlib.Path(__file__).parent.absolute(), "assets")
user_files_dir = os.path.join(pathlib.Path(__file__).parent.absolute(), "user_files")
config = os.path.join(user_files_dir, "config.json")


def add_editor_button(buttons: List[str], editor: Editor) -> List[str]:
    editor._links["image_integration"] = on_editor_btn_click
    iconstr = os.path.join(asset_dir, "icon.png")

    tooltip_text = (
            "Images integration")

    button = editor.addButton(
        iconstr,
        "image_integration",
        on_editor_btn_click,
        keys="",
        tip=tooltip_text,
        disables = False
    )
    buttons.append(button)

    return buttons
    
def on_editor_btn_click(editor: Editor):
    deck_id = editor.card.did if editor.card is not None else editor.parentWindow.deck_chooser.selectedId()
    
    if editor.note is not None:
        note_type_id = editor.note.mid
    elif editor.card is not None:
        note_type_id = editor.card.note().mid
    else:
        note_type_id = editor.mw.col.models.current()["id"]

    input_field, output_field = get_fields_from_config(deck_id, note_type_id, editor)
    word = editor.note[input_field]
    selected_url = select_images(word)

    if selected_url:
        insert_image_into_field(selected_url, output_field, editor)


#===================== images search=====================
def select_images(word: str, max_size: int = 150):
    dialog = QDialog()
    dialog.setWindowTitle("Select an Image")
    layout = QVBoxLayout(dialog)

    list_widget = QListWidget()
    list_widget.setViewMode(QListView.ViewMode.IconMode)
    list_widget.setIconSize(QSize(max_size, max_size))
    list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)
    list_widget.setSpacing(10)
    layout.addWidget(list_widget)

    debug_label = QLabel("Loading: 0 / errors: 0")
    layout.addWidget(debug_label)

    btn_layout = QHBoxLayout()
    btn_more = QPushButton("Load more")
    btn_cancel = QPushButton("Cancel")
    btn_layout.addWidget(btn_more)
    btn_layout.addWidget(btn_cancel)
    layout.addLayout(btn_layout)

    btn_cancel.clicked.connect(dialog.reject)

    selected_url = {"value": None, "loaded": 0, "errors": 0, "last_error": "", "offset": 0}

    def on_item_clicked(item: QListWidgetItem):
        selected_url["value"] = item.data(Qt.ItemDataRole.UserRole)
        dialog.accept()

    list_widget.itemClicked.connect(on_item_clicked)

    dialog._manager = QNetworkAccessManager(dialog)

    def handle_reply(reply):
        err = reply.error()
        if err.value != 0:
            selected_url["errors"] += 1
            selected_url["last_error"] = reply.errorString()
            debug_label.setText(f"Loaded: {selected_url['loaded']} / errors: {selected_url['errors']} / last: {selected_url['last_error'][:60]}")
            reply.deleteLater()
            return

        data = reply.readAll()
        pixmap = QPixmap()
        if pixmap.loadFromData(bytes(data)):
            selected_url["loaded"] += 1
            icon = QIcon(pixmap)
            item = QListWidgetItem(icon, "")
            item.setData(Qt.ItemDataRole.UserRole, reply.url().toString())
            list_widget.addItem(item)
        else:
            selected_url["errors"] += 1
            selected_url["last_error"] = f"pixmap fail: {reply.url().toString()[-40:]}"

        debug_label.setText(f"Loaded: {selected_url['loaded']} / errors: {selected_url['errors']} / last: {selected_url['last_error'][:60]}")
        reply.deleteLater()

    dialog._manager.finished.connect(handle_reply)

    def load_images(offset: int = 0):
        btn_more.setEnabled(False)
        urls = search_images_duckduckgo(word, max_results=10, offset=offset)
        for url in urls:
            request = QNetworkRequest(QUrl(url))
            request.setRawHeader(b"User-Agent", b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
            dialog._manager.get(request)
        selected_url["offset"] += 10
        btn_more.setEnabled(True)

    def on_load_more():
        load_images(selected_url["offset"])

    btn_more.clicked.connect(on_load_more)

    dialog.show()
    load_images(0)

    dialog.exec()
    return selected_url["value"]
 
def insert_image_into_field(url: str, field_name: str, editor: Editor):
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()

        ext = os.path.splitext(url.split("?")[0])[-1]
        if ext.lower() not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            ext = ".jpg"

        fname = mw.col.media.write_data(f"image_integration_{field_name}{ext}", response.content)

        img_tag = f'<img src="{fname}">'
        editor.note[field_name] += img_tag  # append to existing content
        editor.loadNote()

    except Exception as e:
        showInfo(f"Failed to insert image: {str(e)}")
 
def search_images_duckduckgo(query: str, max_results: int = 10, offset: int = 0) -> List[str]:
    vqd = get_vqd(query)

    url = "https://duckduckgo.com/i.js"
    params = {
        "q": query,
        "vqd": vqd,
        "o": "json",
        "p": "1",
        "s": offset,   # offset parameter
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://duckduckgo.com/",
    }

    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    results = data.get("results", [])
    urls = [img["image"] for img in results[:max_results]]

    return urls
    
def get_vqd(query: str) -> str:
    url = "https://duckduckgo.com/"
    params = {"q": query}
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()

    # vqd is embedded in the page
    match = re.search(r'vqd="([^"]+)"', resp.text)
    if not match:
        raise RuntimeError("Could not extract vqd token")

    return match.group(1)
    

#=====================  fields =====================
def get_fields_from_config(deck_id: int, note_type_id: int, editor: Editor) -> Tuple[str, str]:
    with open(config, "r", encoding="utf8") as f:
        cfg = json.load(f)
        
    deck_cfg = cfg.get(str(deck_id), {})
    note_cfg = deck_cfg.get(str(note_type_id), {})
    
    input_field = note_cfg.get("input")
    output_field = note_cfg.get("output") or note_cfg.get("ouput")  # handle typo if exists
    
    
    if input_field and output_field:
        return input_field, output_field

    return ask_user_for_fields(deck_id, note_type_id, editor)

def ask_user_for_fields(deck_id: int, note_type_id: int, editor: Editor) -> Tuple[str, str]:
    """Ask the user to select input and output fields via a popup with radio buttons."""
    
    note = editor.note
    
    if note is None:
        showInfo("No note available to select fields.")
        return "", ""
    
    fields = note.keys()  # all field names in the current note

    def select_field_dialog(title: str) -> str:
        dialog = QDialog()
        dialog.setWindowTitle(title)
        layout = QVBoxLayout(dialog)

        label = QLabel(f"Select {title}:")
        layout.addWidget(label)
        
        button_group = QButtonGroup(dialog)
        button_group.setExclusive(True)

        for idx, field in enumerate(fields):
            radio = QRadioButton(field)
            button_group.addButton(radio, id=idx)
            layout.addWidget(radio)

        selected_field = {"value": None}

        def on_continue():
            checked_id = button_group.checkedId()
            if checked_id == -1:
                showInfo("Please select a field before continuing.")
                return
            selected_field["value"] = fields[checked_id]
            dialog.accept()

        btn_continue = QPushButton("Continue")
        btn_continue.clicked.connect(on_continue)
        layout.addWidget(btn_continue)

        dialog.setLayout(layout)
        dialog.exec()
        return selected_field["value"] or ""

    # Ask for input field
    input_field = select_field_dialog("Input Field")
    # Ask for output field
    output_field = select_field_dialog("Output Field")

    # Save the selection to config
    save_fields_to_config(deck_id, note_type_id, input_field, output_field)
    
    return input_field, output_field

def save_fields_to_config(deck_id: int, note_type_id: int, input_field: str, output_field: str):
    """
    Saves nested config like {deckid: {noteid: {input, output}}}
    """
    cfg = {}
    if os.path.exists(config):
        try:
            with open(config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except json.JSONDecodeError:
            cfg = {}

    if str(deck_id) not in cfg:
        cfg[str(deck_id)] = {}

    cfg[str(deck_id)][str(note_type_id)] = {"input": input_field, "output": output_field}

    os.makedirs(os.path.dirname(config), exist_ok=True)
    with open(config, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

gui_hooks.editor_did_init_buttons.append(add_editor_button)
