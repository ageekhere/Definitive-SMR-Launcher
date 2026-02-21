import wave
from pathlib import Path
from piper import PiperVoice
import threading
import os
import winsound  # Windows WAV playback
import __main__
import sys
import time

def get_bundle_dir():
    """Where bundled read-only files live"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent


def get_app_dir():
    """Where the exe lives (writable location)"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def stop_button_pressed():
    """Stops playback immediately"""
    winsound.PlaySound(None, winsound.SND_PURGE)
    __main__.error_logs("[stop_button_pressed] Stopping playback", "info")


def text_audio(mission_text: str, mission_name: str):
    """
    Runs audio in a background thread.
    """
    __main__.error_logs("[text_audio] Creating encoding thread", "info")
    tts_thread = threading.Thread(target=audio, args=(mission_text, mission_name))
    tts_thread.start()
    return tts_thread  # optional: caller can join if needed


def audio(mission_text: str, mission_name: str):
    """
    Generates a WAV file for a mission using Piper TTS.
    Saves WAV and text in a voice-specific subfolder.
    Plays the WAV automatically after creation.
    """
    # ─────────── Paths ───────────
    BUNDLE_DIR = get_bundle_dir()
    APP_DIR = get_app_dir()
    VOICES_DIR = APP_DIR / "voices_data" / "voices"
    # ─────────── Model selection with config preference ───────────
    preferred_voice = __main__.get_config_value("option4")  # e.g. "en_US-lessac-medium"

    # Search recursively in all subfolders
    onnx_files = list(VOICES_DIR.rglob("*.onnx"))

    if not onnx_files:
        __main__.error_logs("[audio] No .onnx model found in " + str(VOICES_DIR) + " or any subfolder","warning")
        raise FileNotFoundError(f"No .onnx model found in {VOICES_DIR} (recursive search)")

    MODEL_PATH = None

    # Try to find a model matching the config value
    if preferred_voice and isinstance(preferred_voice, str) and preferred_voice.strip():
        pref = preferred_voice.strip().lower()
        __main__.error_logs(f"[audio] Config 'option4' specifies: '{preferred_voice}'", "info")

        for candidate in onnx_files:
            name_lower   = candidate.name.lower()
            parent_lower = candidate.parent.name.lower()

            # Matching logic: folder name exact > filename contains > normalized variants
            if (parent_lower == pref or
                pref in name_lower or
                pref.replace(" ", "_") in name_lower or
                pref.replace(" ", "-") in name_lower or
                pref in parent_lower):
                MODEL_PATH = candidate
                __main__.error_logs(f"[audio] Using preferred model matching '{preferred_voice}':\n"f" {MODEL_PATH}","info")
                break

    # Fallback to first found model
    if MODEL_PATH is None:
        MODEL_PATH = onnx_files[0]
        used_name = (preferred_voice.strip()
                     if preferred_voice and isinstance(preferred_voice, str)
                     else "[no value in option4]")
        __main__.error_logs(f"[audio] No match for 'option4' = '{used_name}' -> using first found:\n" f" {MODEL_PATH}","info")

    # Log how many models were discovered
    if len(onnx_files) > 1:
        __main__.error_logs(f"[audio] Found {len(onnx_files)} .onnx files - selected: {MODEL_PATH.name}","debug")

    # ─────────── Mission-specific paths (with voice subfolder) ───────────
    MISSION_DIR = APP_DIR / "voices_data" / "mission_audio" / mission_name

    # Use the actual parent folder name of the chosen model (most reliable)
    voice_folder_name = MODEL_PATH.parent.name

    OUTPUT_SUBDIR = MISSION_DIR / voice_folder_name
    OUTPUT_WAV = OUTPUT_SUBDIR / f"{mission_name}.wav"
    SAVED_MISSION_TEXT = OUTPUT_SUBDIR / f"{mission_name}.txt"

    # Create folders (mission dir + voice-specific subdir)
    MISSION_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUBDIR.mkdir(exist_ok=True)

    # ─────────── Load previously saved text (if any) ───────────
    saved_text = ""
    if SAVED_MISSION_TEXT.exists():
        with open(SAVED_MISSION_TEXT, "r", encoding="utf-8") as f:
            saved_text = f.read().strip()

    # ─────────── Decide whether we need to generate new audio ───────────
    text_has_changed = mission_text.strip() != saved_text

    if text_has_changed:
        __main__.gEncoding_label.configure(text="Encoding Please Wait...")
        time.sleep(0.3)  # give UI time to update
        __main__.error_logs(f"[audio] [{mission_name}] Text changed/new generating WAV...","info")

        # Remove old WAV if exists
        if OUTPUT_WAV.exists():
            OUTPUT_WAV.unlink()

        # Save current mission text
        with open(SAVED_MISSION_TEXT, "w", encoding="utf-8") as f:
            f.write(mission_text)

        # Synthesize
        try:
            voice = PiperVoice.load(str(MODEL_PATH))
            with wave.open(str(OUTPUT_WAV), "wb") as wav_file:
                voice.synthesize_wav(mission_text, wav_file)
            __main__.error_logs(f"[audio] [{mission_name}] New WAV created: {OUTPUT_WAV}","info")
        except Exception as e:
            __main__.error_logs(f"[audio] Synthesis failed with model {MODEL_PATH.name}: {e}","error")
            raise

    else:
        if OUTPUT_WAV.exists():
            __main__.error_logs(f"[audio] [{mission_name}] Text unchanged & WAV exists skipping synthesis","info")
        else:
            __main__.error_logs(f"[audio] [{mission_name}] Text matches but WAV missing generating...","warning")
            __main__.gEncoding_label.configure(text="Encoding Please Wait...")
            try:
                voice = PiperVoice.load(str(MODEL_PATH))
                with wave.open(str(OUTPUT_WAV), "wb") as wav_file:
                    voice.synthesize_wav(mission_text, wav_file)
                __main__.error_logs(f"[audio] [{mission_name}] WAV recovered: {OUTPUT_WAV}","info")
            except Exception as e:
                __main__.error_logs(f"[audio] Recovery synthesis failed: {e}","error")
                raise

    # ─────────── Play the audio (async) ───────────
    if OUTPUT_WAV.exists():
        __main__.error_logs(f"[audio] [{mission_name}] Playing: {OUTPUT_WAV}", "info")
        winsound.PlaySound(str(OUTPUT_WAV), winsound.SND_FILENAME | winsound.SND_ASYNC)
    else:
        __main__.error_logs(f"[audio] [{mission_name}] WAV missing after synthesis attempt", "warning")

    __main__.gEncoding_label.configure(text="")


# For testing / standalone run (uncomment if needed)
# if __name__ == "__main__":
#     text_audio("Hello world, this is a test.", "test_mission_001")