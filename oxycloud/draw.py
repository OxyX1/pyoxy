import ctypes
import win32con
import win32gui
import win32api
import time

class Overlay:
    def __init__(self,
                 x=50, y=50,
                 width=200, height=150,
                 shape_type="rectangle",  # "rectangle", "ellipse", "rounded_rectangle"
                 line_color=(255, 0, 0),  # RGB
                 line_thickness=3,
                 line_style=win32con.PS_SOLID,
                 fill_color=None,  # RGB or None for transparent fill
                 rounded_corner_x=20, # For rounded_rectangle
                 rounded_corner_y=20, # For rounded_rectangle
                 transparency_color_key=(0, 0, 0), # Color to make transparent
                 alpha=None # Overall window alpha (0-255), overrides colorkey if set
                 ):
        self.hInstance = win32api.GetModuleHandle()
        self.className = "PythonOverlayWindow" # Unique class name

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.shape_type = shape_type
        self.line_color = line_color
        self.line_thickness = line_thickness
        self.line_style = line_style
        self.fill_color = fill_color
        self.rounded_corner_x = rounded_corner_x
        self.rounded_corner_y = rounded_corner_y
        self.transparency_color_key = transparency_color_key
        self.alpha = alpha

        # Create a brush for the background using the transparency color key
        # This is important for LWA_COLORKEY to work correctly for the window background
        self.hbrushBackground = win32gui.CreateSolidBrush(
            win32api.RGB(self.transparency_color_key[0], self.transparency_color_key[1], self.transparency_color_key[2])
        )

        wndClass = win32gui.WNDCLASS()
        wndClass.lpfnWndProc = self._wndProc
        wndClass.hInstance = self.hInstance
        wndClass.lpszClassName = self.className
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wndClass.hbrBackground = self.hbrushBackground # Use the custom brush
        wndClass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW

        try:
            win32gui.RegisterClass(wndClass)
        except win32gui.error as err:
            # Class already registered, which is fine if running script multiple times in same session
            if err.winerror != 1410: # ERROR_CLASS_ALREADY_EXISTS
                raise

        screen_w = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_h = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

        ex_style = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST

        self.hwnd = win32gui.CreateWindowEx(
            ex_style,
            self.className,
            "Python Overlay", # Window title (not visible for WS_POPUP)
            win32con.WS_POPUP, # Borderless, no title bar
            0, 0,             # Window position (covers whole screen initially)
            screen_w, screen_h, # Window size (covers whole screen)
            None, None,
            self.hInstance,
            None
        )

        if not self.hwnd:
            raise RuntimeError("Failed to create window")

        self._apply_transparency()
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd) # Force initial paint

    def _apply_transparency(self):
        if self.alpha is not None:
            win32gui.SetLayeredWindowAttributes(self.hwnd, 0, self.alpha, win32con.LWA_ALPHA)
        else:
            color_key_val = win32api.RGB(
                self.transparency_color_key[0],
                self.transparency_color_key[1],
                self.transparency_color_key[2]
            )
            win32gui.SetLayeredWindowAttributes(self.hwnd, color_key_val, 0, win32con.LWA_COLORKEY)

    def _wndProc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_PAINT:
            hdc, paintStruct = win32gui.BeginPaint(hwnd)
            self._draw(hdc)
            win32gui.EndPaint(hwnd, paintStruct)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.DeleteObject(self.hbrushBackground) # Clean up the background brush
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

    def _draw(self, hdc):
        # Create pen
        pen_color_val = win32api.RGB(self.line_color[0], self.line_color[1], self.line_color[2])
        pen = win32gui.CreatePen(self.line_style, self.line_thickness, pen_color_val)
        old_pen = win32gui.SelectObject(hdc, pen)

        # Create brush (or use null brush for no fill)
        brush = None
        old_brush = None
        if self.fill_color:
            fill_color_val = win32api.RGB(self.fill_color[0], self.fill_color[1], self.fill_color[2])
            brush = win32gui.CreateSolidBrush(fill_color_val)
        else:
            # Use a null brush for transparent fill (outline only)
            # Important: The window background itself (set by hbrBackground) is the colorkey
            brush = win32gui.GetStockObject(win32con.NULL_BRUSH)

        old_brush = win32gui.SelectObject(hdc, brush)

        # Define drawing rectangle
        left = self.x
        top = self.y
        right = self.x + self.width
        bottom = self.y + self.height

        # Draw shape
        if self.shape_type == "rectangle":
            win32gui.Rectangle(hdc, left, top, right, bottom)
        elif self.shape_type == "ellipse":
            win32gui.Ellipse(hdc, left, top, right, bottom)
        elif self.shape_type == "rounded_rectangle":
            win32gui.RoundRect(hdc, left, top, right, bottom, self.rounded_corner_x, self.rounded_corner_y)
        else:
            # Default to rectangle or raise error
            print(f"Warning: Unknown shape_type '{self.shape_type}'. Drawing rectangle.")
            win32gui.Rectangle(hdc, left, top, right, bottom)


        # Restore and delete GDI objects
        win32gui.SelectObject(hdc, old_pen)
        win32gui.DeleteObject(pen)

        if old_brush is not None:
            win32gui.SelectObject(hdc, old_brush)
        if self.fill_color: # Only delete if we created a new brush
            win32gui.DeleteObject(brush)
        # Do not delete stock objects like NULL_BRUSH

    def redraw(self):
        if self.hwnd:
            win32gui.InvalidateRect(self.hwnd, None, True) # True to erase background
            # UpdateWindow might not be strictly necessary if InvalidateRect is followed by PeekMessage
            # but it ensures the WM_PAINT is processed more immediately in some cases.
            # win32gui.UpdateWindow(self.hwnd)

    def message_loop(self):
        """Pumps messages. Call this in your main loop after updates."""
        if win32gui.PeekMessage(ctypes.byref(win32gui.MSG()), 0, 0, 0, win32con.PM_REMOVE):
            msg = win32gui.MSG()
            if win32gui.GetMessage(ctypes.byref(msg), None, 0, 0):
                win32gui.TranslateMessage(ctypes.byref(msg))
                win32gui.DispatchMessage(ctypes.byref(msg))
                if msg.message == win32con.WM_QUIT:
                    return False # Signal to exit loop
        return True # Continue loop

    def close(self):
        if self.hwnd:
            win32gui.DestroyWindow(self.hwnd)
            self.hwnd = None
        # Unregister class if no more windows of this class exist.
        # This is more complex to track, so often omitted for simple scripts.
        # For now, we don't unregister, which is fine for most use cases.

    # --- Configuration Setters ---
    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.redraw()

    def set_size(self, width, height):
        self.width = width
        self.height = height
        self.redraw()

    def set_shape_type(self, shape_type, rounded_corner_x=None, rounded_corner_y=None):
        self.shape_type = shape_type
        if rounded_corner_x is not None:
            self.rounded_corner_x = rounded_corner_x
        if rounded_corner_y is not None:
            self.rounded_corner_y = rounded_corner_y
        self.redraw()

    def set_colors(self, line_color=None, fill_color=None): # Use 'keep' or similar if you want to not change one
        if line_color is not None:
            self.line_color = line_color
        # To explicitly set no fill, pass `fill_color=None`
        # To keep current fill color, don't pass fill_color argument
        if 'fill_color' in locals() and fill_color is None and self.fill_color is not None: # If explicitly passed as None
             self.fill_color = None
        elif fill_color is not None:
            self.fill_color = fill_color
        self.redraw()


    def set_line_attributes(self, thickness=None, style=None):
        if thickness is not None:
            self.line_thickness = thickness
        if style is not None:
            self.line_style = style
        self.redraw()

    def set_rounded_corners(self, rx, ry):
        self.rounded_corner_x = rx
        self.rounded_corner_y = ry
        if self.shape_type == "rounded_rectangle":
            self.redraw()

    def set_alpha(self, alpha_value):
        """Set overall window alpha (0-255). Disables color keying."""
        self.alpha = alpha_value
        self.transparency_color_key = None # Or ensure it's not used
        self._apply_transparency()
        self.redraw()

    def set_transparency_color_key(self, color_key_rgb):
        """Set the color key for transparency. Disables alpha blending."""
        self.transparency_color_key = color_key_rgb
        self.alpha = None # Or ensure it's not used

        # Recreate background brush with the new color key
        if self.hbrushBackground:
            win32gui.DeleteObject(self.hbrushBackground)
        self.hbrushBackground = win32gui.CreateSolidBrush(
            win32api.RGB(self.transparency_color_key[0], self.transparency_color_key[1], self.transparency_color_key[2])
        )
        # Update window class if possible, or recreate window (simpler: just apply effect)
        # For simplicity here, we just update the effect. The background of existing drawings
        # won't change until they are redrawn over the new colorkey bg.
        win32gui.SetClassLong(self.hwnd, win32con.GCL_HBRBACKGROUND, self.hbrushBackground)

        self._apply_transparency()
        self.redraw()


if __name__ == "__main__":
    print("Starting overlay demo...")
    try:
        # --- Initial Configuration ---
        overlay = Overlay(
            x=100, y=100,
            width=250, height=180,
            shape_type="rectangle",
            line_color=(0, 255, 0), # Green
            line_thickness=5,
            fill_color=(0, 0, 100, 50), # Dark Blue, (alpha for fill not directly supported by GDI like this)
                                      # fill_color should be opaque for colorkeying.
                                      # For semi-transparent fill, use LWA_ALPHA on whole window.
            fill_color=(0,0,100), # Solid Dark Blue
            transparency_color_key=(1, 1, 1) # A nearly black color for transparency
                                             # Make sure this is different from any color you want to draw
                                             # if you are not using LWA_ALPHA.
        )
        print("Overlay created. Initial shape: Rectangle (Green outline, Blue fill)")
        print(f"Transparency key: {overlay.transparency_color_key}")

        # --- Example Animation/Dynamic Changes ---
        running = True
        start_time = time.time()
        cycle_duration = 15 # seconds for a full cycle of changes
        loop_count = 0

        while running:
            # Process window messages. If WM_QUIT, message_loop returns False.
            if not overlay.message_loop():
                running = False
                break

            current_time = time.time()
            elapsed = current_time - start_time
            progress = (elapsed % cycle_duration) / cycle_duration # 0.0 to 1.0

            # Change position (e.g., move in a circle)
            center_x, center_y = 300, 300
            radius = 100
            angle = progress * 2 * 3.14159 # Full circle
            new_x = int(center_x + radius * ctypes.c_double(angle).value) # Using math.cos and math.sin would be better
            new_y = int(center_y + radius * ctypes.c_double(angle).value) # Using math.sin
            # overlay.set_position(new_x, new_y) # Commented out for simpler demo

            # Change size
            base_w, base_h = 100, 80
            size_mod = (ctypes.c_double(progress * 3.14159 * 2).value + 1) / 2 # Sinusoidal 0 to 1
            # overlay.set_size(int(base_w + size_mod * 150), int(base_h + size_mod * 100))


            # Every few seconds, change properties
            if loop_count % 200 == 0: # Roughly every 10 seconds (200 * 0.05)
                print(f"Time: {elapsed:.1f}s - Changing properties...")
                current_shape = overlay.shape_type
                if current_shape == "rectangle":
                    overlay.set_shape_type("ellipse")
                    overlay.set_colors(line_color=(255, 0, 0), fill_color=(100, 0, 0)) # Red theme
                    print("Changed to Ellipse (Red)")
                elif current_shape == "ellipse":
                    overlay.set_shape_type("rounded_rectangle", rounded_corner_x=30, rounded_corner_y=15)
                    overlay.set_colors(line_color=(0, 0, 255), fill_color=None) # Blue outline, no fill
                    overlay.set_line_attributes(thickness=2, style=win32con.PS_DASH)
                    print("Changed to Rounded Rectangle (Dashed Blue outline, no fill)")
                else: # rounded_rectangle
                    overlay.set_shape_type("rectangle")
                    overlay.set_colors(line_color=(0, 255, 0), fill_color=(0,100,0)) # Green theme
                    overlay.set_line_attributes(thickness=5, style=win32con.PS_SOLID)
                    # Example: switch to alpha transparency
                    # overlay.set_alpha(180)
                    # print("Changed to Rectangle (Green), Alpha=180")
                    print("Changed to Rectangle (Green)")


            # Explicitly redraw if not done by setters or if you batch changes
            # overlay.redraw() # Usually setters call this, but if you change attributes directly.

            time.sleep(0.016) # Aim for ~60 FPS for message pumping and animation
            loop_count +=1

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'overlay' in locals() and overlay.hwnd:
            print("Closing overlay...")
            overlay.close()
        print("Demo finished.")