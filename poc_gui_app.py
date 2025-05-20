# poc_gui_app.py
import dearpygui.dearpygui as dpg
import numpy as np
import poc_generative_art as art_engine # Our generative art script

# --- Configuration ---
ART_WIDTH_PX = 600
ART_HEIGHT_PX = 400
CONTROL_PANEL_WIDTH = 250

# --- Initial Parameters for the Artwork ---
current_art_params = {
    'width': ART_WIDTH_PX, # Width of the art generation canvas
    'height': ART_HEIGHT_PX, # Height of the art generation canvas
    'rows': 5,
    'cols': 5,
    'bg_color_rgb': (0.1, 0.1, 0.2),                   # Dark blue (R,G,B floats 0-1)
    'rect_base_color_rgb': (0.9, 0.1, 0.1),            # Bright red (R,G,B floats 0-1)
    'rect_color_vary_factor': 0.5
}

# --- Dear PyGui Setup ---
dpg.create_context()
# Viewport for the entire application
dpg.create_viewport(
    title='Interactive Generative Art PoC',
    width=ART_WIDTH_PX + CONTROL_PANEL_WIDTH + 30, # Adjusted for some padding
    height=ART_HEIGHT_PX + 60 # Adjusted for some padding
)
dpg.setup_dearpygui()

# --- Texture for Artwork ---
# Initialize with dummy data (e.g., all black)
# The array must be 1D, float32, RGBA (0.0-1.0 range)
initial_texture_data = np.zeros(ART_WIDTH_PX * ART_HEIGHT_PX * 4, dtype=np.float32)

with dpg.texture_registry(show=False): # show=True for debugging textures
    dpg.add_raw_texture(
        width=ART_WIDTH_PX,
        height=ART_HEIGHT_PX,
        default_value=initial_texture_data,
        format=dpg.mvFormat_Float_rgba, # RGBA float format
        tag="art_texture_tag"
    )

# --- Core Interaction Logic ---
def update_art_display_callback(sender, app_data, user_data):
    # Update current_art_params from all UI controls
    # The user_data for callbacks is set to the key in current_art_params (or a descriptive string)
    
    # Fetch all values fresh when any control changes or button is pressed,
    # to ensure params are consistent.
    current_art_params['rows'] = dpg.get_value("slider_rows")
    current_art_params['cols'] = dpg.get_value("slider_cols")
    
    # DPG color pickers return a list of 4 floats (0-255 originally, but dpg gives them as floats 0-1 if not modified, or ints 0-255 if from default_value)
    # Let's ensure they are scaled 0-1 for our art engine.
    bg_color_picker_val = dpg.get_value("colorpicker_bg") # Expected: list of 4 floats/ints [R,G,B,A]
    current_art_params['bg_color_rgb'] = (bg_color_picker_val[0]/255.0, bg_color_picker_val[1]/255.0, bg_color_picker_val[2]/255.0)
    
    rect_color_picker_val = dpg.get_value("colorpicker_rect_base") # Expected: list of 4 floats/ints [R,G,B,A]
    current_art_params['rect_base_color_rgb'] = (rect_color_picker_val[0]/255.0, rect_color_picker_val[1]/255.0, rect_color_picker_val[2]/255.0)
    
    current_art_params['rect_color_vary_factor'] = dpg.get_value("slider_color_vary")

    # The 'width' and 'height' for art generation are fixed by ART_WIDTH_PX and ART_HEIGHT_PX for this PoC.
    # They are already in current_art_params but we ensure they reflect the texture size.
    current_art_params['width'] = ART_WIDTH_PX
    current_art_params['height'] = ART_HEIGHT_PX

    print(f"DEBUG: Callback triggered by '{user_data}'. Generating art with params: {current_art_params}")

    # Generate new artwork data
    # This function should return a 1D float32 RGBA NumPy array
    new_art_data_numpy = art_engine.generate_pattern_numpy(
        ART_WIDTH_PX, # Use fixed pixel dimensions for generation
        ART_HEIGHT_PX,
        current_art_params # Pass the whole dictionary
    )
    
    # Update the texture in Dear PyGui
    if new_art_data_numpy is not None and new_art_data_numpy.size == ART_WIDTH_PX * ART_HEIGHT_PX * 4:
        dpg.set_value("art_texture_tag", new_art_data_numpy)
        print(f"DEBUG: Texture 'art_texture_tag' updated. Array length: {len(new_art_data_numpy)}")
    else:
        print(f"ERROR: Failed to generate valid new_art_data_numpy. Size: {new_art_data_numpy.size if new_art_data_numpy is not None else 'None'}")


# --- UI Layout ---
with dpg.window(label="Artwork Display", tag="artwork_window",
                width=ART_WIDTH_PX, height=ART_HEIGHT_PX,
                pos=(10, 10), # Added some padding from viewport edge
                no_resize=True, no_move=True, no_close=True, no_collapse=True,
                no_title_bar=True, no_scrollbar=True):
    dpg.add_image("art_texture_tag")

with dpg.window(label="Controls", tag="control_window",
                width=CONTROL_PANEL_WIDTH, height=ART_HEIGHT_PX, 
                pos=(ART_WIDTH_PX + 20, 10)): # Position it next to the artwork window

    dpg.add_text("Pattern Controls")
    dpg.add_slider_int(label="Rows", tag="slider_rows",
                       default_value=current_art_params['rows'], min_value=1, max_value=20,
                       callback=update_art_display_callback, user_data="slider_rows_changed")
    dpg.add_slider_int(label="Columns", tag="slider_cols",
                       default_value=current_art_params['cols'], min_value=1, max_value=20,
                       callback=update_art_display_callback, user_data="slider_cols_changed")

    dpg.add_separator()
    dpg.add_text("Color Controls")
    
    # DPG color pickers default_value expects list/tuple of 3 or 4 floats (0-1) or ints (0-255).
    # For consistency, we provide initial values as floats 0-1 scaled to 0-255 for display.
    bg_default_color_dpg = [int(c*255) for c in current_art_params['bg_color_rgb']] + [255] # RGBA ints for picker
    dpg.add_color_picker(label="Background Color", tag="colorpicker_bg",
                         default_value=bg_default_color_dpg, no_alpha=True, # For RGB
                         callback=update_art_display_callback, user_data="colorpicker_bg_changed")

    rect_default_color_dpg = [int(c*255) for c in current_art_params['rect_base_color_rgb']] + [255] # RGBA ints for picker
    dpg.add_color_picker(label="Rectangle Base Color", tag="colorpicker_rect_base",
                         default_value=rect_default_color_dpg, no_alpha=True, # For RGB
                         callback=update_art_display_callback, user_data="colorpicker_rect_base_changed")

    dpg.add_slider_float(label="Color Variation", tag="slider_color_vary", 
                         default_value=current_art_params['rect_color_vary_factor'],
                         min_value=0.0, max_value=1.0, format="%.2f",
                         callback=update_art_display_callback, user_data="slider_color_vary_changed")
    
    dpg.add_separator()
    # The "Regenerate" button will also call the same callback.
    dpg.add_button(label="Regenerate Artwork", callback=update_art_display_callback, user_data="manual_regenerate_button", width=-1)


# --- Initial Artwork Generation ---
def trigger_initial_draw():
    print("INFO: Triggering initial artwork generation...")
    # Call the main update callback. Sender and app_data are not strictly needed here
    # as the callback reads all values directly from controls and current_art_params.
    # We use the current_art_params which are already set to defaults.
    update_art_display_callback(sender="initial_draw_trigger", app_data=None, user_data="initial_draw")

# Call it once the UI is set up and before the main loop starts.
trigger_initial_draw() 

# --- Start GUI ---
dpg.show_viewport()
dpg.start_dearpygui() # Main loop for Dear PyGui
dpg.destroy_context()
