# 📝 Anki Image Addon – To-Do List

## 1. Project setup

* [ ] Create addon folder (e.g., `anki_image_addon/`)
* [ ] Create `__init__.py` and helper files (`image_selector.py`, `settings.py`)
* [ ] Setup Zed + basedpyright environment (done)
* [ ] Add README with basic description

## 2. Persistent field configuration

* [ ] Decide on a storage path: use `mw.pm.addonFolder()` or `user_files` folder
* [ ] Store settings per **deck + note type** (JSON file recommended)
* [ ] Functions to:

  * [ ] Save mapping `{deck_name: {note_type: {input_field, output_field}}}`
  * [ ] Load mapping
  * [ ] Update mapping via settings UI

## 3. Settings dialog

* [ ] Add a **menu item** in `Tools` → “Image Addon Settings”
* [ ] Dialog UI:

  * [ ] Select **deck** (dropdown)
  * [ ] Select **note type** (dropdown)
  * [ ] Select **input field**
  * [ ] Select **output field**
* [ ] Save settings to JSON

## 4. Add Card Editor integration

* [ ] Hook into `Editor` toolbar
* [ ] Add **button** “Add Image from Web”
* [ ] On button click:

  * [ ] Detect current deck + note type
  * [ ] Load stored input/output fields
  * [ ] If missing, prompt user once to configure

## 5. Image search

* [ ] Implement image search function:

  * [ ] Input: word (from input field)
  * [ ] Output: list of image URLs (Google Images / Bing API / `google_images_search`)
* [ ] Optional: limit number of results (e.g., 10–20)
* [ ] Cache downloaded images temporarily

## 6. Image selection dialog

* [ ] Display images as **thumbnails** in a Qt dialog
* [ ] Allow **single selection**
* [ ] Return selected image URL/path

## 7. Insert image into card

* [ ] Download image to `collection.media` folder (`mw.col.media.add_file()`)
* [ ] Insert `<img src="filename.ext">` into **output field**
* [ ] Refresh editor UI to display image immediately

## 8. Optional enhancements

* [ ] Allow multiple images in selection dialog
* [ ] Auto-resize or format images
* [ ] Error handling: no images found / network error
* [ ] Logging or notifications via `showInfo()`

## 9. Code quality & type safety

* [ ] Type hints for all functions
* [ ] No wildcard imports (`from aqt.qt import *`)
* [ ] `mw.col` `Optional` checks
* [ ] `basedpyright` clean (no warnings)

## 10. Testing

* [ ] Test in **different decks / note types**
* [ ] Test missing settings → prompts
* [ ] Test network errors
* [ ] Test multiple images / selection
