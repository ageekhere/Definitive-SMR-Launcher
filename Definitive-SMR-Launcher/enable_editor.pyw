import __main__

def get_editor_enabled():
    shell = __main__.win32com.client.Dispatch("WScript.Shell")
    path = __main__.Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "Settings.ini"

    if not path.exists():
        __main__.error_logs("[enable_editor] Cannot find Settings.ini", "warning")
        return 0

    in_user_settings = False

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()

        if stripped.startswith("[") and stripped.endswith("]"):
            in_user_settings = stripped == "[User Settings]"
            continue

        if in_user_settings and stripped.startswith("EditorEnabled"):
            try:
                return int(stripped.split("=")[1].strip())
            except (IndexError, ValueError):
                __main__.error_logs("[enable_editor] Cannot read Settings.ini", "error")
                return 0
    return 0

def set_editor_enabled(value: int):
    if value not in (0, 1):
        __main__.error_logs("[enable_editor] EditorEnabled must be 0 or 1", "error")
        raise ValueError("EditorEnabled must be 0 or 1")

    shell = __main__.win32com.client.Dispatch("WScript.Shell")
    path = __main__.Path(shell.SpecialFolders("MyDocuments")) / "My Games" / "Sid Meier's Railroads" / "Settings.ini"

    if not path.exists():
        __main__.error_logs("[enable_editor] Cannot find Settings.ini", "error")
        raise FileNotFoundError(path)

    lines = path.read_text(encoding="utf-8").splitlines()
    new_lines = []

    in_user_settings = False
    editor_written = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("[") and stripped.endswith("]"):
            if in_user_settings and not editor_written:
                new_lines.append(f"EditorEnabled = {value}")
                editor_written = True

            in_user_settings = stripped == "[User Settings]"
            new_lines.append(line)
            continue

        if in_user_settings and stripped.startswith("EditorEnabled"):
            new_lines.append(f"EditorEnabled = {value}")
            editor_written = True
            continue

        new_lines.append(line)

    # If file ended while inside [User Settings]
    if in_user_settings and not editor_written:
        new_lines.append(f"EditorEnabled = {value}")

    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    __main__.error_logs("[enable_editor] Setting map editor to " + str(value) + " (0 off 1 on)", "info")

def toggle_editor_enabled():
    current = __main__.gEditor.get()
    if current == 0:
        set_editor_enabled(0)
    elif current == 1:
        set_editor_enabled(1)
    else:
        set_editor_enabled(0)

def map_editor(option:str):
    if(option == "read"):
        return get_editor_enabled()

    if(option == "toggle"):
        toggle_editor_enabled()
