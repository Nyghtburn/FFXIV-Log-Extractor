# FFXIV Native Log Cleaner

A Python utility designed to extract, clean, and organize roleplay chat logs from **Native FFXIV Binary Logs** (`.log` files).

Unlike ACT logs (which are plain text), FFXIV's native logs are binary-encrypted and filled with combat data, hex codes, and system garbage. This script uses a heuristic "sieve" approach to burn away the noise and retrieve human-readable dialogue.

**Perfect for:**
* Creating datasets for AI training (LLMs/Gems) based on your character's voice.
* Archiving old RP logs without the file bloat of combat data.
* Recovering chat history when you didn't have ACT running.

## 🚀 Features

* **Native File Support:** Works directly with the `00000000.log` files found in `My Games`.
* **Multi-Character Sorter:** Extracts your specific characters into their own text files, while dumping everyone else into a general `World_Context.txt`.
* **Aggressive Hygiene:** Filters out:
    * Combat spam ("You cast...", "Direct Hit!", "Taking damage")
    * System messages (Market board, Retainers, Crafting)
    * PvP artifacts (Frontline/Crystalline Conflict binary noise)
    * Venue/Shout spam (Twitch links, DJ promotes)
* **Server Shield Fix:** Correctly handles cross-world chat (e.g., `Name@Server`) which often breaks standard log parsers.

## ⚙️ Setup & Usage

1.  **Install Python:** Ensure you have Python 3.x installed.
2.  **Download the Script:** Clone this repo or download `ffxiv_log_cleaner.py`.
3.  **Configure the Variables:**
    Open the script in a text editor (VS Code, Notepad++, IDLE) and edit the top section:
    
    ```python
    1. Path to your FFXIV Logs folder
(Windows Default: "C:\Users\YOUR_USER\Documents\My Games\FINAL FANTASY XIV - A Realm Reborn")
BASE_FOLDER = r"C:\Path\To\Your\FFXIV_Logs"

# 2. Where to save the clean text files
OUTPUT_FOLDER = r"./Cleaned_Logs"

# 3. List of Character Names to extract into their own files
# Exact spelling required. Spaces are allowed.
TARGET_CHARACTERS = [
    "Character Name One",
    "Character Name Two"
]

    ```

4.  **Run the Script:**
    ```bash
    python ffxiv_log_cleaner.py
    ```

## 📂 Output

The script will create a `Cleaned_Logs` folder containing:
* `Cloud_Strife.txt` (Only dialogue spoken by Cloud)
* `Tifa_Lockhart.txt` (Only dialogue spoken by Tifa)
* `World_Context.txt` (Dialogue from everyone else—useful for teaching AI about world lore/tone)

## ⚠️ Limitations

* **Heuristic Extraction:** This does not fully decode the FFXIV packet structure. It extracts text strings and validates them based on sentence structure. It is ~99% accurate for chat, but may occasionally miss a line or catch a system message that looks remarkably like a human sentence.
* **Timestamps:** Native logs store timestamps as binary integers. This script currently discards them to focus on pure dialogue extraction.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
