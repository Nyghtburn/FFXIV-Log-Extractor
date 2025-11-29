"""
FFXIV Native Log Extractor & Cleaner
------------------------------------
Copyright (c) 2025 Corey "Esher" R.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Description: 
    Parses native FFXIV binary log files (.log), extracts human dialogue, 
    and aggressively filters out combat spam, system messages, and binary artifacts.
    Designed to prepare Roleplay (RP) logs for AI training or archiving.
"""

import os
import re

# ================= CONFIGURATION (USER MUST EDIT) =================

# 1. Path to your FFXIV Logs folder
# Windows Default: r"C:\Users\YOUR_USER\Documents\My Games\FINAL FANTASY XIV - A Realm Reborn"
BASE_FOLDER = r"C:\Path\To\Your\FFXIV_Logs"

# 2. Where to save the clean text files
OUTPUT_FOLDER = r"./Cleaned_Logs"

# 3. List of Character Names to extract into their own files
# Exact spelling required. Spaces are allowed.
TARGET_CHARACTERS = [
    "Character Name One",
    "Character Name Two"
]

# ==================================================================

# GLOBAL LISTS & FILTERS
# ----------------------

# List of known FFXIV Servers (NA/EU/JP/OC)
# Used to prevent the script from mistaking "ServerName" for a "CharacterName"
# or to detect "ServerName used Ability" patterns.
SERVER_NAMES = [
    "Balmung", "Brynhildr", "Coeurl", "Diabolos", "Goblin", "Malboro", "Mateus", "Zalera",
    "Adamantoise", "Cactuar", "Faerie", "Gilgamesh", "Jenova", "Midgardsormr", "Sargatanas", "Siren",
    "Behemoth", "Excalibur", "Hyperion", "Lamia", "Leviathan", "Ultros", "Famfrit", "Lich", "Odin",
    "Phoenix", "Shiva", "Zodiark", "Cerberus", "Louisoix", "Moogle", "Ragnarok", "Omega", "Phantom",
    "Alpha", "Raiden", "Sagittarius", "Halicarnassus", "Maduin", "Marilith", "Seraph", "Dynamis",
    "Aegis", "Atomos", "Carbuncle", "Garuda", "Gungnir", "Kujata", "Ramuh", "Tonberry", "Typhon", "Unicorn",
    "Alexander", "Bahamut", "Durandal", "Fenrir", "Ifrit", "Ridill", "Tiamat", "Ultima", "Valefor", "Yojimbo", "Zeromus",
    "Anima", "Asura", "Chocobo", "Hades", "Ixion", "Mandragora", "Masamune", "Pandaemonium", "Shinryu", "Titan",
    "Bismark", "Ravana", "Sephirot", "Sophia", "Zurvan"
]

# Phrases that indicate a line is Game Data, not Dialogue.
# Includes Combat terms, System messages, Crafting logs, and PvP spam.
NOISE_PHRASES = [
    "You gain", "You obtain", "experience points", "Market Board", "Retainer", 
    "You synthesize", "Quality changed", "Durability", "Teleport", "queue", 
    "engages", "defeated", "standard time", "Server time", "http", "fc", "ls",
    "Direct hit", "Critical hit", "misses", "recovers", "HP", "MP", "TP", 
    "dodge", "parry", "block", "resists", "invulnerable", "No target", 
    "location", "instance", "sealed", "commenced", "ended", "search", 
    "gathered", "landed", "Bonus", "effect of", "wears off", "damage",
    "mounts the", "You mount", "sanctuary", "ovoo", "PvP area", "soul crystal",
    "traits and hotbars", "Registration Language", "orchestrion", "Invincibility",
    "Stun", "Heavy", "Bind", "Sleep", "Slow", "Silence", "Blind", "Paralysis",
    "War-chief", "Drill Primed", "Welcome to", "Duty pop", "Duty Roulette",
    "plugin", "Dalamud", "Updates:", "Open plugin", "Portrait set", "unaffected",
    "Lv.", "Level", "Bishop Active", "Orogeny", "Paradox", "Biolysis", "Biolytic",
    "Aquaveil", "Stoneskin", "Blast Arrow", "Frontliner", "Cure III", "Sacred Sight",
    "Protect", "Analysis", "Sprint", "Umbral Ice", "Onslaught", "Miracle of Nature",
    # Specific Skills often mistaken for names in PvP/High-End Content
    "Diabrosis", "Lethargy", "Overheated", "Macrocosmos", "Retrograde", "Resilience",
    "Shield Smite", "Repertoire", "Starfall Dance", "Fan Dance", "Immortal Flames",
    "Aether Mortar", "Honing Dance", "Guard", "Acclaim", "Lady of Crowns", "Honing Ovation",
    "Sacred Claim", "Pandora Lioness", "Chain Stratagem", "Slipping", "Frontline March",
    "Soul Resonance", "Monomachy", "Radiant Aegis", "Further Ruin", "Cuchulainn",
    "Eukrasia", "Epicycle", "Diurnal Benefic", "Astral Warmth", "Crest of Time",
    "Bioblaster", "Mortared", "Expedience", "Desperate Measures", "Fire Resonance",
    "Toxikon", "Haima", "Hysteria", "Thunderclap", "Recuperate",
    "selling items", "Crystarium markets", "equipped", "unequipped"
]

# Words that, if they start a sentence, guarantee it is combat data.
COMBAT_VERBS = [
    "casts", "uses", "readies", "begins", "hits", "takes", "scores", 
    "misses", "recovers", "suffers", "evades", "interrupts",
    "loses", "gains", "drains", "restores", "reflects", "prepares", "defeats", 
    "equipped", "unequipped"
]

def clean_trailing_garbage(text):
    """
    Removes binary suffixes common in PvP/Instance logs.
    Example: 'Hello World!)i9' becomes 'Hello World!'
    """
    return re.sub(r'[\)\.]i[\+\=\-\:\d\w]{0,2}$', '', text).strip()

def is_noise(line):
    """Checks if a line contains banned phrases or illegal characters."""
    for phrase in NOISE_PHRASES:
        if phrase.lower() in line.lower(): return True
    # Check for specific FFXIV binary arrows and artifacts
    if re.search(r'[ٜڜܜݜޜۜ$]', line): return True
    # Check if line is purely numeric
    if re.match(r'^[\d\s\W]+$', line): return True 
    return False

def is_combat_spam(text):
    """
    Analyzes sentence structure to detect combat logs masquerading as text.
    Handles 'Casts Fire' and 'Malboro uses Bad Breath'.
    """
    text = text.strip()
    if not text: return True
    parts = text.split(' ')
    if not parts: return True
    
    # Check 1: Does it start with a combat verb?
    first_word = parts[0].replace(':', '').strip().lower()
    if first_word in COMBAT_VERBS: return True
    if first_word.isdigit(): return True

    # Check 2: The "Server Shield" (e.g. "Balmung uses...")
    # If the first word is a Server Name, check if the SECOND word is a verb.
    is_server_start = False
    for s in SERVER_NAMES:
        if s.lower() == first_word:
            is_server_start = True
            break   
    if is_server_start and len(parts) > 1:
        second_word = parts[1].lower()
        if second_word in COMBAT_VERBS: return True

    return False

def is_server_junk(text):
    """
    Detects corrupted server strings like 'Zalera.)i)1' or 'Coeurl.on'
    """
    # Remove non-alphanumeric chars to see if the core word is a server
    clean = re.sub(r'[^\w]', '', text)
    for s in SERVER_NAMES:
        if clean.startswith(s):
            return True
    return False

def is_valid_actor(actor):
    """
    Determines if a string is a valid Character Name.
    """
    # 1. Length Check (FFXIV names are min 2 parts, unlikely to be < 4 chars)
    if len(actor) < 4: return False
    
    # 2. Punctuation Start Check (Binary artifacts often start with . [ ) ! )
    if re.match(r'^[\.\[\)\!]', actor): return False
    
    # 3. Double Colon Check (Hexdump artifact)
    if "::" in actor: return False
    
    # 4. Standard Noise Filters
    if is_noise(actor): return False
    if is_combat_spam(actor): return False
    if is_server_junk(actor): return False
    
    return True

def sanitize_filename(name):
    """Makes a string safe for use as a Windows filename."""
    return re.sub(r'[^\w\-_\. ]', '_', name).replace(' ', '_')

def process_logs():
    if not os.path.exists(BASE_FOLDER):
        print(f"Error: Base folder not found at {BASE_FOLDER}")
        print("Please edit the configuration at the top of the script.")
        return

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    print("Initializing FFXIV Log Extraction...")
    print(f"Target Characters: {TARGET_CHARACTERS}")
    
    # Create file handles
    file_handles = {}
    for char_name in TARGET_CHARACTERS:
        fname = sanitize_filename(char_name) + ".txt"
        file_handles[char_name] = open(os.path.join(OUTPUT_FOLDER, fname), 'w', encoding='utf-8')

    # The catch-all context file
    file_handles["__CONTEXT__"] = open(os.path.join(OUTPUT_FOLDER, "World_Context.txt"), 'w', encoding='utf-8')

    found_count = 0

    # Walk through the directory tree
    for root, dirs, files in os.walk(BASE_FOLDER):
        # Only process folders named "log" inside "FFXIV_CHR..." folders
        if os.path.basename(root) == "log":
            parent = os.path.basename(os.path.dirname(root))
            if parent.startswith("FFXIV_CHR"):
                
                print(f"Scanning: {parent}...")

                for filename in files:
                    if filename.endswith(".log"):
                        source_path = os.path.join(root, filename)
                        try:
                            with open(source_path, 'rb') as f:
                                content = f.read()

                            # Decode binary, ignoring errors
                            text_blob = content.decode('utf-8', errors='ignore')
                            
                            # SPLIT STRATEGY: 
                            # Split by control characters (0x00-0x1F) AND the '@' symbol.
                            # Splitting by '@' fixes "Name@Server" appearing as one chunk.
                            chunks = re.split(r'[\x00-\x1f\x7f-\x9f@]+', text_blob)
                            
                            # Clean garbage off chunks immediately
                            clean_chunks = [clean_trailing_garbage(c.strip()) for c in chunks if c.strip()]
                            
                            # Iterate through chunks using a lookahead
                            skip_counter = 0

                            for i in range(len(clean_chunks) - 1):
                                if skip_counter > 0:
                                    skip_counter -= 1
                                    continue

                                actor = clean_chunks[i]

                                # === ACTOR VALIDATION ===
                                if not is_valid_actor(actor): continue

                                found_message = None
                                
                                # LOOKAHEAD: Check the next 3 chunks for the message.
                                # Binary logs often insert garbage between Actor and Message.
                                for offset in range(1, 4):
                                    if i + offset >= len(clean_chunks): break
                                    candidate = clean_chunks[i + offset]
                                    
                                    # === MESSAGE VALIDATION ===
                                    if is_server_junk(candidate): continue
                                    if re.match(r'^[\.\[\)\!]', candidate): continue
                                    if is_combat_spam(candidate): continue
                                    
                                    # Specific Phrases to Ban manually
                                    if "You use" in candidate or "You cast" in candidate: continue
                                    if "autoturret" in candidate: continue

                                    if not is_noise(candidate):
                                        # Safety: If we hit a new capitalized name, we probably missed the message.
                                        if len(candidate) < 20 and candidate[0].isupper() and " " in candidate:
                                             break
                                        
                                        # Echo Check: Actor cannot say their own name
                                        if actor == candidate: break
                                        
                                        # Message must be more than 1 char (filters stray "Y", "v", ".")
                                        if len(candidate) > 1:
                                            found_message = candidate
                                            skip_counter = offset
                                            break
                                
                                if found_message:
                                    found_count += 1
                                    if actor in TARGET_CHARACTERS:
                                        file_handles[actor].write(f"{actor}: {found_message}\n")
                                    else:
                                        file_handles["__CONTEXT__"].write(f"{actor}: {found_message}\n")

                        except Exception as e:
                            print(f"Error reading {filename}: {e}")
                            continue 

    # Cleanup
    for handle in file_handles.values():
        handle.close()

    print(f"\nExtraction Complete.")
    print(f"Total lines extracted: {found_count}")
    print(f"Files saved to: {OUTPUT_FOLDER}")

if __name__ == "__main__":
    process_logs()