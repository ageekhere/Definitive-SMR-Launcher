from error_logs import error_logs
import customtkinter as ctk
"""
Check for window popups
"""
def check_for_popup_window(app):
    error_logs("[check_for_popup_window] Check to see if there is a popup window","info")
    for w in app.winfo_children():
        if isinstance(w, ctk.CTkToplevel) and w.winfo_viewable():
            error_logs("[check_for_popup_window] popup window found","info")
            return True
    return False