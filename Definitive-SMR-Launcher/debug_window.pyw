import __main__

def debug_window():
    """
    Opens or updates the log window displaying all logs stored in __main__.gLogs.
    """
    # If a log window already exists and is still open
    if __main__.gLogWindow is not None and __main__.gLogWindow.winfo_exists():
        __main__.gLogWindowTextbox.configure(state="normal")
        __main__.gLogWindowTextbox.delete("1.0", "end")

        for i, (msg, color) in enumerate(__main__.gLogs, start=1):
            __main__.gLogWindowTextbox.insert("end", msg + "\n")
            __main__.gLogWindowTextbox.tag_add(color, f"{i}.0", f"{i}.end")

        __main__.gLogWindowTextbox.see("end")  # scroll to bottom
        __main__.gLogWindowTextbox.configure(state="disabled")
        return

    # Otherwise create new window
    __main__.error_logs("[debug_window] Opening Log window", "info")
    __main__.gLogWindow = __main__.ctk.CTkToplevel(__main__.gApp)
    __main__.gLogWindow.title("Logs")

    width, height = 800, 600

    # Get screen dimensions
    screen_width = __main__.gLogWindow.winfo_screenwidth()
    screen_height = __main__.gLogWindow.winfo_screenheight()

    # Calculate center position
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    # Apply geometry with center position
    __main__.gLogWindow.geometry(f"{width}x{height}+{x}+{y}")

    #__main__.create_icon(__main__.sys, __main__.gLogWindow)

    __main__.gLogWindow.attributes("-topmost", True)



    # Reset gLogWindow when closed
    def on_close():
        __main__.gLogWindow.destroy()
        __main__.gLogWindow = None
        __main__.gLogWindowTextbox = None

    __main__.gLogWindow.protocol("WM_DELETE_WINDOW", on_close)

    # Textbox
    __main__.gLogWindowTextbox = __main__.ctk.CTkTextbox(
        __main__.gLogWindow, width=780, height=580, wrap="word"
    )
    __main__.gLogWindowTextbox.pack(padx=10, pady=10)

    # Tags
    __main__.gLogWindowTextbox.tag_config("green", foreground="green")
    __main__.gLogWindowTextbox.tag_config("yellow", foreground="yellow")
    __main__.gLogWindowTextbox.tag_config("red", foreground="red")

    # Insert logs
    for i, (msg, color) in enumerate(__main__.gLogs, start=1):
        __main__.gLogWindowTextbox.insert("end", msg + "\n")
        __main__.gLogWindowTextbox.tag_add(color, f"{i}.0", f"{i}.end")

    __main__.gLogWindowTextbox.see("end")  # ensure starts scrolled to bottom
    __main__.gLogWindowTextbox.configure(state="disabled")