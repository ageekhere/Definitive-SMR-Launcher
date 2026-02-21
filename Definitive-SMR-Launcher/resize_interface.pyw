

import __main__

previous_size = None
resize_job = None
DEBOUNCE_DELAY = 100  # milliseconds
gIsRebuildingUI = False

def resize_interface(event):
    global resize_job
    global previous_size
    # FIX: Ignore events from child widgets (buttons, frames, etc.)
    if event.widget != __main__.gApp:
        return

    # Cancel previous scheduled call
    if resize_job is not None: 
        __main__.gApp.after_cancel(resize_job)

    if previous_size is None:
        previous_size = (1280, 720)

    current_size = (event.width, event.height)

    # If size hasn't changed, skip
    if current_size == previous_size:
        return

    # Schedule new call
    __main__.gApp.unbind("<Configure>")

    resize_job = __main__.gApp.after(DEBOUNCE_DELAY, resize_interface_start, current_size,event)

def resize_interface_start(size,event):
    global previous_size
    global gIsRebuildingUI
    if __main__.gMapMangerTheadRunning == True:
        __main__.gApp.bind("<Configure>",lambda event: resize_interface(event))
        __main__.gApp.after(DEBOUNCE_DELAY, resize_interface_start, size,event)
        return

    if gIsRebuildingUI:
        return

    gIsRebuildingUI = True

    try:
        # your rebuild logic here
        resize_interface(event)

    finally:
        gIsRebuildingUI = False

    current_size = size

    # Throttle: skip if less than 1s has passed or size didn't change
    if current_size == previous_size:
        return

    canvas_width = current_size[0]
    canvas_height = current_size[1]

    if canvas_width < __main__.gAppWidth or canvas_height < __main__.gAppHeight:
        return

    img_width, img_height = __main__.original_bg_image.size

    # Calculate scale ratio
    ratio = min(canvas_width / img_width, canvas_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)

    resized = __main__.original_bg_image.resize((new_width, new_height), __main__.Image.LANCZOS)
    __main__.bg_photo = __main__.ImageTk.PhotoImage(resized)

    # Center image
    x = (canvas_width - new_width) // 2
    y = (canvas_height - new_height) // 2
    __main__.gInterface_canvas.coords(__main__.bg_canvas_id, 0, 0)
    __main__.gInterface_canvas.itemconfig(__main__.bg_canvas_id, image=__main__.bg_photo)

    position = canvas_width * 0.211  # 21.1%
    new_frame_width = canvas_width - position - 15
    

    if new_frame_width > 100:
        __main__.gScrollable_frame.configure(width=new_frame_width, height=canvas_height)
        __main__.gScrollable_frame.place_forget()
        __main__.gScrollable_frame.place(x=position, y=0)
        __main__.gScrollable_frame_width = new_frame_width
        
    __main__.gScrollable_frame.update_idletasks()

    for widget in __main__.gScrollable_frame.winfo_children():
        try:
            if widget.winfo_exists():
                widget.destroy()
        except Exception as e:
            print("Destroy error:", e)


    canvas_width = __main__.gInterface_canvas.winfo_width()
    canvas_height = __main__.gInterface_canvas.winfo_height()

    # Original design was based on 720 height
    scale_factor = canvas_height / 720

    x_margin = 0.01
    default_x = int(canvas_width * x_margin)

    # Shifted Y positions (+29 applied)
    shifted_y_positions = [
        209, 249, 289, 329, 369, 409, 449,
        489, 529, 569, 569, 650, 690
    ]

    buttons_ids = [
        __main__.gUpdate_maps_button_id,
        __main__.gGameTypeDrop_id,
        __main__.gCustom_exe_button_id,
        __main__.gCustom_levels_button_id,
        __main__.gEditor_button_id,
        __main__.gGamePath_button_id,
        __main__.gGameLocation_label_id,
        __main__.gRemoveSymlink_id,
        __main__.glanguageDrop_id,
        __main__.glanguageAudioDrop_id,
        __main__.downnload_audio_lang_id,   # special X
        __main__.gLog_button_id,
        __main__.gStart_button_id
    ]

    for button_id, y in zip(buttons_ids, shifted_y_positions):
        y_pos = int(y * scale_factor)
        # Special X for download_audio_lang
        if button_id == __main__.downnload_audio_lang_id:
            x_pos = int(170 * (canvas_width / 1280))  # assuming original width was 1280
        else:
            x_pos = default_x

        __main__.gInterface_canvas.coords(button_id, x_pos, y_pos)
    
    __main__.gInterface_canvas.update_idletasks()
    
    if current_size != previous_size:
        __main__.map_manager()

    previous_size = current_size
    __main__.gApp.bind("<Configure>",lambda event: resize_interface(event))
    __main__.gResizing = False