import __main__
def set_lang_type_selection(choice: str):
        try:
            # Persist the new value in config.ini and update globals
            __main__.set_config_value("option3", choice)
            __main__.messagebox.showinfo(__main__.get_text("LanguageSetTo") + " " + choice, __main__.get_text("ApplyLanguage"))
            __main__.error_logs(f"[set_lang_type_selection] Language set to: {__main__.gConfigUserInfo['option3']}", "info")
        except Exception as e:
            __main__.error_logs(f"[set_lang_type_selection] Failed to update Language: {e}", "error")
