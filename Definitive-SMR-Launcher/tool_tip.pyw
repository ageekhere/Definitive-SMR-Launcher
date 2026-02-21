import tkinter as tk
import __main__
class ToolTip:
    def __init__(self, widget, text, delay_ms=600, max_width=300):
        try:
            """
            Creates a tooltip for the given widget.
            
            Args:
                widget:     The tkinter widget to attach the tooltip to
                text:       The text to show in the tooltip
                delay_ms:   Delay in milliseconds before showing (default: 600)
                max_width:  Maximum tooltip width in pixels (default: 300)
            """
            self.widget    = widget
            self.text      = text
            self.delay_ms  = delay_ms
            self.max_width = max_width
            
            self.tip_window = None
            self.after_id   = None
            
            widget.bind("<Enter>", self.schedule_show)
            widget.bind("<Leave>", self.unschedule_and_hide)
            # Optional: hide on any mouse click / drag start
            widget.bind("<ButtonPress>", self.unschedule_and_hide)
        except Exception as e:
            __main__.error_logs("[ToolTip] error " + str(e), "error")


    def schedule_show(self, event=None):
        """Schedule tooltip appearance after delay"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
        
        self.after_id = self.widget.after(self.delay_ms, self._show_tip, event)

    def unschedule_and_hide(self, event=None):
        """Cancel pending show and hide existing tooltip"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        
        self.hide_tip()

    def _show_tip(self, event=None):
        """Create and display the tooltip"""
        self.after_id = None
        
        # Safety: don't show if widget is no longer visible/mapped
        if not self.widget.winfo_ismapped():
            return
            
        if self.tip_window is not None:
            return

        # Try to follow current mouse position (more natural)
        try:
            x = self.widget.winfo_pointerx() + 14
            y = self.widget.winfo_pointery() + 20
        except:
            # Fallback
            x = event.x_root + 14 if event else self.widget.winfo_rootx() + 50
            y = event.y_root + 20 if event else self.widget.winfo_rooty() + 50

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        # The label with wrapping
        
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            wraplength=self.max_width - 16,   # leave padding
            background="#333333",             # light yellow (classic tooltip)
            foreground="white",
            relief="solid",
            borderwidth=1,
            padx=8,
            pady=5,
            font=("Segoe UI", 9),             # or "tahoma", "helvetica", etc.
        )
        label.pack()

    def hide_tip(self):
        """Destroy the tooltip window if it exists"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None