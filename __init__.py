from aqt import gui_hooks
# from aqt.utils import showInfo
# from aqt.qt import QAction, qconnect
from typing import List, Tuple, Union
from aqt.editor import Editor
import os
import pathlib

asset_dir = os.path.join(pathlib.Path(__file__).parent.absolute(), "assets")

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
    
def on_editor_btn_click(editor: Editor, mode: Union[None, str] = None):
    # editor.saveNow(lambda: add_pronunciation(editor, mode))
    pass
    
gui_hooks.editor_did_init_buttons.append(add_editor_button)
