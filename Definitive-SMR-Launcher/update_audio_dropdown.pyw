import sys
from pathlib import Path
from config_manager import get_config_value
from truncate_string import truncate_string
import __main__

def update_audio_dropdown():

    # Get current config value
    if getattr(sys, 'frozen', False):
        APP_DIR = Path(sys.executable).parent
    APP_DIR = Path(__file__).parent

    VOICES_DIR = APP_DIR / "voices_data" / "voices"

    audio_language = get_config_value("option4")

    # Get all .onnx filenames
    onnx_files = [f.name for f in VOICES_DIR.rglob("*.onnx")]

    # Decide what the selected text should be
    if not onnx_files:
        new_value = "Install Voice"
    else:
        if not audio_language or audio_language.strip() == "":
            new_value = "Select Voice"
        elif audio_language in onnx_files:
            new_value = audio_language
        else:
            new_value = "Select Voice"

    new_value = truncate_string(new_value)

    # Update dropdown values
    __main__.glanguageAudioDrop.configure(values=onnx_files if onnx_files else ["Install Voice"])

    # Set selected value safely
    __main__.glanguageAudioDrop.set(new_value)