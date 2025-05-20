# poc_generative_art.py
import numpy as np

def generate_pattern_numpy(width, height, params):
    # Simplified docstring to avoid syntax errors in prompt
    # Args: width, height, params (dict with rows, cols, bg_color_rgb, etc.)
    # Returns: 1D float32 RGBA NumPy array
    
    rows = params.get('rows', 5)
    cols = params.get('cols', 5)
    bg_r, bg_g, bg_b = params.get('bg_color_rgb', (0.1, 0.1, 0.1)) 
    rect_base_r, rect_base_g, rect_base_b = params.get('rect_base_color_rgb', (0.2, 0.5, 0.8))
    rect_color_vary_factor = params.get('rect_color_vary_factor', 0.3)

    image = np.zeros((height, width, 4), dtype=np.float32)

    image[:, :, 0] = bg_r
    image[:, :, 1] = bg_g
    image[:, :, 2] = bg_b
    image[:, :, 3] = 1.0

    cell_width = float(width) / cols
    cell_height = float(height) / rows
    padding_w = cell_width * 0.1
    padding_h = cell_height * 0.1

    for r_idx in range(rows):
        for c_idx in range(cols):
            vary_r = max(0.0, min(1.0, rect_base_r + (r_idx / max(1,rows-1) - 0.5) * rect_color_vary_factor if rows > 1 else rect_base_r))
            vary_g = max(0.0, min(1.0, rect_base_g + (c_idx / max(1,cols-1) - 0.5) * rect_color_vary_factor if cols > 1 else rect_base_g))
            vary_b = max(0.0, min(1.0, rect_base_b + ((r_idx+c_idx) / max(1,rows+cols-2) - 0.5) * rect_color_vary_factor if (rows+cols)>2 else rect_base_b))
            
            rect_y_start = int(r_idx * cell_height + padding_h)
            rect_y_end = int((r_idx + 1) * cell_height - padding_h)
            rect_x_start = int(c_idx * cell_width + padding_w)
            rect_x_end = int((c_idx + 1) * cell_width - padding_w)

            final_y_start = np.clip(rect_y_start, 0, height)
            final_y_end = np.clip(rect_y_end, 0, height)
            final_x_start = np.clip(rect_x_start, 0, width)
            final_x_end = np.clip(rect_x_end, 0, width)
            
            if final_x_start < final_x_end and final_y_start < final_y_end:
                image[final_y_start:final_y_end, final_x_start:final_x_end, 0] = vary_r
                image[final_y_start:final_y_end, final_x_start:final_x_end, 1] = vary_g
                image[final_y_start:final_y_end, final_x_start:final_x_end, 2] = vary_b
                image[final_y_start:final_y_end, final_x_start:final_x_end, 3] = 1.0
            
    return image.flatten()

if __name__ == '__main__':
    IMG_WIDTH_PX = 200 
    IMG_HEIGHT_PX = 150
    test_params = {
        'rows': 3, 
        'cols': 4,
        'bg_color_rgb': (0.1, 0.1, 0.1), 
        'rect_base_color_rgb': (0.7, 0.2, 0.2), 
        'rect_color_vary_factor': 0.7
    }

    print("Testing NumPy-only array generation...")
    numpy_output = generate_pattern_numpy(IMG_WIDTH_PX, IMG_HEIGHT_PX, test_params) 
    print(f"Generated NumPy array with shape: {numpy_output.shape}, dtype: {numpy_output.dtype}")
    expected_len = IMG_WIDTH_PX * IMG_HEIGHT_PX * 4
    print(f"Expected length: {expected_len}, Actual length: {len(numpy_output)}")
    if len(numpy_output) == expected_len:
        print("NumPy array length is correct.")
    else:
        print("WARNING: NumPy array length is INCORRECT.")

    try:
        from PIL import Image
        image_to_save_data = (numpy_output.reshape((IMG_HEIGHT_PX, IMG_WIDTH_PX, 4)) * 255).astype(np.uint8)
        img = Image.fromarray(image_to_save_data, 'RGBA')
        img.save("test_pattern_numpy_only.png")
        print("Saved test_pattern_numpy_only.png for visual verification.")
    except ImportError:
        print("Pillow not installed. Skipping save of numpy array as image.")
    except Exception as e:
        print(f"Error saving numpy array as image: {e}")
