from aqt import gui_hooks, mw
from typing import List, Tuple, Union
from aqt.editor import Editor
from aqt.qt import QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton, QLabel, QButtonGroup
from aqt.utils import showInfo
from typing import Tuple
import os
import pathlib
import json

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
