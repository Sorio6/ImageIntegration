# Anki Image Addon

## Overview

The Anki Image Addon allows you to automatically fetch images from the web and insert them into your Anki cards. When adding a card, you can click a button to select an input field (a word) and an output field (where the image will appear). The addon searches for images online, lets you select one, and inserts it into your card automatically.

---

## Features

* Add a button in the card editor to fetch images from the web.
* Automatic insertion of selected images into the output field.
* Persistent configuration of input and output fields per deck and note type.
* Settings dialog to modify field mappings.

---

## Installation

1. Place the addon folder in Anki's `addons21` directory.
2. Restart Anki.
3. The addon adds a button in the card editor and a menu item under `Tools` → "Image Addon Settings".

---

## Usage

1. Open the Add Card editor.
2. Click the **"Add Image from Web"** button.
3. If this is the first time for the deck/note type, select the input (word) and output (image) fields.
5. Select an image from the dialog.
6. The selected image is inserted into the output field.

---

## Configuration

* Settings are saved per deck and note type.
* You can update the input/output field mapping via the **Setings** button in the dialog.
* Settings are stored in a JSON file inside Anki's user folder.

---

## Requirements

* Anki 2.1+
* Python environment compatible with Anki
* Internet connection for image search

---

## License

MIT License
