# FFXIV Log Extractor

A specialized Python utility designed to extract, clean, and organize roleplay chat logs from **Native FFXIV Binary Logs** (`.log` files).

Unlike ACT logs (which are plain text), FFXIV's native logs are binary-encrypted and filled with combat data, hex codes, packet headers, and system garbage. This tool uses a sophisticated heuristic approach to burn away the noise and retrieve human-readable dialogue.

**Primary Use Cases:**
* 🤖 **AI Training:** Creating clean datasets to train LLMs or Gems on your specific character's voice and personality.
* 📚 **Archiving:** Saving years of RP history without the massive file bloat of combat logs.
* 🕵️ **Recovery:** Recovering chat history from sessions where ACT was not running.

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
   OUTPUT_FOLDER = r"./Cleaned_Logs"

   # 3. List of Character Names to extract
   # Use the exact spelling found in-game.
   TARGET_CHARACTERS = [
       "Cloud Strife",
       "Tifa Lockhart"
   ]
   ```

##  ▶️ Usage

Open your terminal or command prompt in the script's folder and run:

```bash
python ffxiv_log_extractor.py
```

The script will scan all subdirectories, process every log file found, and output the results to your defined `Cleaned_Logs` folder.

## 📂 Understanding the Output

The script generates two types of files:

1.  **`[Character_Name].txt`**
    * Contains *only* the dialogue lines spoken by that specific character.
    * Format: `Character Name: Message content`
    * *Ideal for:* Training AI on a specific persona.

2.  **`World_Context.txt`**
    * Contains dialogue from all other players, NPCs, and retainers.
    * *Ideal for:* Providing an AI with context about the world, lore, and general speaking styles of the community.

## 🤝 Contributing

The FFXIV log format is undocumented and messy. If you find a new type of "garbage" line that is slipping through the filters (e.g., specific PvP messages or new system alerts), feel free to open a Pull Request or Issue!

Key areas to look at in the code:
* `NOISE_PHRASES`: List of strings to ban.
* `is_valid_actor()`: Logic for determining if a string is a name or a hex code.
