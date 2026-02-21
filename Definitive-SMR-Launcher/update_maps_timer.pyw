import __main__

def update_maps_timer():
        count = len(__main__.gNewDownloadMaps) if __main__.gNewDownloadMaps else ""
        __main__.gUpdate_maps_button.configure(text=__main__.get_text("gUpdate_maps_button") + " " + str(count) + " ") # Lang key: gUpdate_maps_button
        __main__.gApp.after(1_800_000, __main__.map_checker)