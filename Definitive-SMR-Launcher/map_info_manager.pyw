"""
map_info_manager.py

Provides a popup window to display map information.
Uses globals and imports from main.py.
"""

import __main__  # Access main's globals and imports
import webbrowser

def map_info_manager(mapId: str):
    """
    Display the content of a mapInfo.txt file in a popup CTk window.

    Parameters:
        mapId (str): The folder name of the map.
    
    Uses:
        __main__.ctk: CustomTkinter for GUI elements.
        __main__.os: For building paths.
    """
    status = "y" if __main__.is_map_manager_running() else "n"
    if status =="y": 
        __main__.messagebox.showinfo(__main__.get_text("LoadingMaps"), __main__.get_text("PleaseWait"))
        return

    def on_popup_close():
        if __main__.gEncoding_label.cget("text") == "":
            popup.destroy()  # close the window
            __main__.stop_button_pressed()

    try:
        __main__.error_logs("[map_info_manager] Loading map info", "info")
        target_path = __main__.os.path.join(str(__main__.os.getcwd()), "maps", mapId, "mapInfo.txt")
        
        with open(target_path, "r", encoding="utf-8") as f:
            map_info_text = f.read()

        map_info_text = __main__.translate_text(map_info_text,__main__.gSelected_translation,"auto")

        # Create a top-level popup window
        popup = __main__.ctk.CTkToplevel(__main__.gApp)
        popup.protocol("WM_DELETE_WINDOW", on_popup_close)

        if __main__.get_map_data(mapId, __main__.gMap_rating_matrix,"is_stable") == "n":
            popup.title(__main__.get_text("MapInformation") + str(mapId +" "+ __main__.get_text("UnstableMap") ))
        else:
            popup.title(__main__.get_text("MapInformation") + str(mapId))
        popup.resizable(0, 0)

        # Set size
        width, height = 800, 640 
        popup.geometry(f"{width}x{height}")

        # Keep popup always on top
        popup.attributes("-topmost", True)

        # Center relative to main window
        master = popup.master
        master.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2 - width // 2)
        y = master.winfo_y() + (master.winfo_height() // 2 - height // 2)
        popup.geometry(f"{width}x{height}+{x}+{y}")

        __main__.create_icon(__main__.sys, popup)

        def rate_map(map:str):
            if map == "":
                return
            url = "https://github.com/ageekhere/Definitive-SMR-Launcher/discussions/" + str(map)
            webbrowser.open(url)

        def text_to_speech(map_info_text):
            bg_color = __main__.gSpeech_btn.cget("fg_color")
            if bg_color == "#1F6AA5":
                __main__.gSpeech_btn.configure(fg_color="green", hover_color="#66cc66") 
                lines = map_info_text.splitlines()
                for i, line in enumerate(lines):
                    if line.startswith("Type:"):
                        start_index = i + 1  # +1 to remove the "Type:" line as well
                        break
                else:
                    start_index = 0  # If no line starts with Type:, keep everything

                # Keep only lines after "Type:"
                map_info_text = "\n".join(lines[start_index:])

                __main__.text_audio(map_info_text,mapId)
            else:
                __main__.stop_button_pressed()
                __main__.gSpeech_btn.configure(fg_color="#1F6AA5", hover_color="#1F6AA5") 

        
        btn_text = str(__main__.rating_check(mapId))

        map_url = __main__.get_map_data(mapId, __main__.gMap_rating_matrix,"url")
        btn_font = __main__.ctk.CTkFont(size=16)
        audio_font = __main__.ctk.CTkFont(size=25)
        info_btn = __main__.ctk.CTkButton(
            popup,
            width=100,
            height=20,
            corner_radius=0,
            text= btn_text + __main__.get_text("rate_map"),
            font=btn_font,
            command=__main__.partial(rate_map, map_url))
        info_btn.grid(row=1, column=0, padx=5, pady=0,sticky="nw")

        if(btn_text == "Rating Unavailable"):
            
            info_btn.configure(text=btn_text)
            info_btn.configure(state="disabled")

        btn_text = str(__main__.rating_check(mapId))

        map_url = __main__.get_map_data(mapId, __main__.gMap_rating_matrix,"url")
        btn_font = __main__.ctk.CTkFont(size=16)
        info_btn = __main__.ctk.CTkButton(
            popup,
            width=100,
            height=20,
            corner_radius=0,
            text= btn_text + __main__.get_text("rate_map"),
            font=btn_font,
            command=__main__.partial(rate_map, map_url))
        info_btn.grid(row=1, column=0, padx=5, pady=0,sticky="nw")

        # Create textbox
        textbox = __main__.ctk.CTkTextbox(
            popup,
            width=780,
            height=550,
            wrap="word"
        )
        #textbox.pack(pady=20, padx=20)
        textbox.grid(row=2, column=0, padx=10, pady=5,sticky="n")

        # Insert text and make read-only
        textbox.insert("1.0", map_info_text)
        textbox.configure(state="disabled")

        # translate
        def set_lang_translation(choice: str):

            textbox.configure(state="normal")
            lang_code = choice.split("(")[1].strip(")")
            __main__.set_config_value("option5", str(lang_code))
            __main__.gSelected_translation = lang_code
            text = __main__.translate_text(map_info_text,lang_code,"auto")
            textbox.delete("0.0", "end")          # clear everything
            textbox.insert("0.0", text)    # insert from the very beginning
            # Optional: scroll to top
            textbox.see("0.0")
            textbox.configure(state="disabled")

        # Popular language codes + names (2026 – most used ones)
        LANGUAGES = {
            "af": "Afrikaans",
            "sq": "Albanian",
            "am": "Amharic",
            "ar": "Arabic",
            "hy": "Armenian",
            "az": "Azerbaijani",
            "eu": "Basque",
            "be": "Belarusian",
            "bn": "Bengali",
            "bs": "Bosnian",
            "bg": "Bulgarian",
            "ca": "Catalan",
            "ceb": "Cebuano",
            "ny": "Chichewa",
            "zh-cn": "Chinese (Simplified)",
            "zh-tw": "Chinese (Traditional)",
            "co": "Corsican",
            "hr": "Croatian",
            "cs": "Czech",
            "da": "Danish",
            "nl": "Dutch",
            "en": "English",
            "eo": "Esperanto",
            "et": "Estonian",
            "tl": "Filipino",
            "fi": "Finnish",
            "fr": "French",
            "fy": "Frisian",
            "gl": "Galician",
            "ka": "Georgian",
            "de": "German",
            "el": "Greek",
            "gu": "Gujarati",
            "ht": "Haitian Creole",
            "ha": "Hausa",
            "haw": "Hawaiian",
            "he": "Hebrew",
            "hi": "Hindi",
            "hmn": "Hmong",
            "hu": "Hungarian",
            "is": "Icelandic",
            "ig": "Igbo",
            "id": "Indonesian",
            "ga": "Irish",
            "it": "Italian",
            "ja": "Japanese",
            "jw": "Javanese",
            "kn": "Kannada",
            "kk": "Kazakh",
            "km": "Khmer",
            "ko": "Korean",
            "ku": "Kurdish (Kurmanji)",
            "ky": "Kyrgyz",
            "lo": "Lao",
            "la": "Latin",
            "lv": "Latvian",
            "lt": "Lithuanian",
            "lb": "Luxembourgish",
            "mk": "Macedonian",
            "mg": "Malagasy",
            "ms": "Malay",
            "ml": "Malayalam",
            "mt": "Maltese",
            "mi": "Maori",
            "mr": "Marathi",
            "mn": "Mongolian",
            "my": "Myanmar (Burmese)",
            "ne": "Nepali",
            "no": "Norwegian",
            "or": "Odia",
            "ps": "Pashto",
            "fa": "Persian",
            "pl": "Polish",
            "pt": "Portuguese",
            "pa": "Punjabi",
            "ro": "Romanian",
            "ru": "Russian",
            "sm": "Samoan",
            "gd": "Scots Gaelic",
            "sr": "Serbian",
            "st": "Sesotho",
            "sn": "Shona",
            "sd": "Sindhi",
            "si": "Sinhala",
            "sk": "Slovak",
            "sl": "Slovenian",
            "so": "Somali",
            "es": "Spanish",
            "su": "Sundanese",
            "sw": "Swahili",
            "sv": "Swedish",
            "tg": "Tajik",
            "ta": "Tamil",
            "te": "Telugu",
            "th": "Thai",
            "tr": "Turkish",
            "tk": "Turkmen",
            "uk": "Ukrainian",
            "ur": "Urdu",
            "ug": "Uyghur",
            "uz": "Uzbek",
            "vi": "Vietnamese",
            "cy": "Welsh",
            "xh": "Xhosa",
            "yi": "Yiddish",
            "yo": "Yoruba",
            "zu": "Zulu",
            # Bonus popular recent additions (post-2022)
            "yue": "Cantonese",          # Often used as yue
            "bho": "Bhojpuri",
            "mai": "Maithili",
        }

        # Prepare values for dropdown
        translate_values = [f"{name} ({code})" for code, name in sorted(LANGUAGES.items(), key=lambda x: x[1])]

        # Now your option menu
        translate_drop = __main__.ctk.CTkOptionMenu(
            popup,
            values=translate_values,
            command=set_lang_translation,
            corner_radius=0
        )

        # Default to English
        
        lang_name = LANGUAGES.get(__main__.gSelected_translation)
        if lang_name:
            translate_drop.set(f"{lang_name} ({__main__.gSelected_translation})")
        else:
            translate_drop.set(f"Unknown ({__main__.gSelected_translation})")
              
        #translate_drop.set("English (en)") #
        translate_drop.grid(row=1, column=0, padx=0, pady=0,sticky="ne")
        __main__.gSpeech_btn = __main__.ctk.CTkButton(
            popup,
            width=50,
            height=20,
            corner_radius=0,
            text= "🔊",
            font=audio_font,
            fg_color = "#1F6AA5",
            command=__main__.partial(text_to_speech, map_info_text))
        __main__.gSpeech_btn.grid(row=3, column=0, padx=0, pady=6,sticky="n")
        __main__.gEncoding_label = __main__.ctk.CTkLabel(popup,text="",font=("Segoe UI", 14))
        __main__.gEncoding_label.grid(row=3,column=0,padx=10,pady=10,sticky="ne")


        if __main__.glanguageAudioDrop.get() == "Install Voice":
            __main__.gSpeech_btn.configure(state="disabled")
        else:
            __main__.gSpeech_btn.configure(state="normal")
            
    except FileNotFoundError:
        __main__.error_logs(f"[map_info_manager] Map info file not found for {mapId}", "error")
    except Exception as e:
        __main__.error_logs(f"[map_info_manager] Error displaying map info for {mapId}: {e}", "error")