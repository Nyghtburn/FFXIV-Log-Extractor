# FFXIV Log Extractor

A specialized Python utility designed to extract, clean, and organize roleplay chat logs from **Native FFXIV Binary Logs** (`.log` files).

Unlike ACT logs (which are plain text), FFXIV's native logs are binary-encrypted and filled with combat data, hex codes, packet headers, and system garbage. This tool uses a sophisticated heuristic approach to burn away the noise and retrieve human-readable dialogue.

**Primary Use Cases:**
* 🤖 **AI Training:** Creating clean datasets to train LLMs or Gems on your specific character's voice and personality.
* 📚 **Archiving:** Saving years of RP history without the massive file bloat of combat logs.
* 🕵️ **Recovery:** recovering chat history from sessions where ACT was not running.

## 🚀 Key Features

* **Native Support:** Parses the raw `00000000.log` files found in your `My Games` folder.
* **Multi-Character Sorting:** Automatically detects specific characters and sorts their dialogue into individual `.txt` files, while dumping general chatter into a `World_Context.txt`.
* **The "Server Shield":** Smartly differentiates between a player named "Malboro" and the server "Malboro," preventing combat logs like `Malboro uses Bad Breath` from being flagged as dialogue.
* **Aggressive Hygiene Filters:**
    * **Combat Incinerator:** Removes combat spam, status effects, and "You gain experience" system messages.
    * **Binary Scrubbing:** Strips out FFXIV specific binary artifacts (e.g., `)i9`, `h3: C5`, ``) and hex codes.
    * **Structure Validation:** Rejects lines that lack vowels or valid sentence structure to ensure high-quality output.
* **Cross-World Support:** Correctly handles `Name@Server` formats to ensure attribution is preserved.

## ⚙️ Installation & Configuration

### Prerequisites
* Python 3.x installed on your machine.

### Setup
1. **Clone or Download** this repository.
2. **Edit the Configuration:**
   Open `ffxiv_log_extractor.py` in any text editor (VS Code, Notepad++, IDLE).
   Modify the top section to point to your folders and characters:

   ```python
   # ================= CONFIGURATION =================
   
   # 1. Path to your FFXIV Logs folder
   # Typical path: C:\Users\YOUR_NAME\Documents\My Games\FINAL FANTASY XIV - A Realm Reborn
   BASE_FOLDER = r"C:\Path\To\Your\FFXIV_Logs"

   # 2. Where to save the clean text files
   OUTPUT_FOLDER = r"./Cleaned_
