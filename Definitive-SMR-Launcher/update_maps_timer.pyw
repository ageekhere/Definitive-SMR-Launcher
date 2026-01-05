import __main__

def update_maps_timer():
        count = len(__main__.gNewDownloadMaps) if __main__.gNewDownloadMaps else ""
        __main__.gUpdate_maps_button.configure(text=f"Maps Available {count}")
        __main__.gApp.after(60_000, __main__.map_checker)