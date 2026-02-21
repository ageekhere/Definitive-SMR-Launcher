def truncate_string(text, max_chars=15):
        return text if len(text) <= max_chars else text[:max_chars-3] + "..."