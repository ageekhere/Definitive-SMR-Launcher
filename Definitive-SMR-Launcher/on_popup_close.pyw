import __main__
from tkinter import messagebox
def on_popup_close():
    if __main__.gDownloadingMapStatus == True:
        __main__.error_logs("[on_popup_close] Cannot close due to pop up window being open", "warning")
        return

    #for w in gApp.winfo_children():
        #if isinstance(w, ctk.CTkToplevel) and w.winfo_exists():
            #error_logs("[on_popup_close] Cannot close due to pop up window being open", "warning")
            #return

    status = "y" if __main__.is_map_manager_running() else "n"
    if status =="y": 
        __main__.messagebox.showinfo(__main__.get_text("AppIsBusy"), __main__.get_text("WaitTaskFinish"))
        return
    #if gEncoding_label == None:
    __main__.gApp.destroy()  # close the window