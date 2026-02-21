import __main__
def get_text(key):
        try:
            # Safely get the "text" value for the given key
            my_val = __main__.gLanguage_file.get(key, {}).get("text")
            return my_val
        except Exception as e:
            __main__.error_logs(f"[get_text] {e}", "error")