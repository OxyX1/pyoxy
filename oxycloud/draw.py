import ctypes
import win32con
import win32gui
import win32api
import time

class Overlay:
    def __init__(self):
        self.hInstance = win32api.GetModuleHandle()
        self.className = "OverlayClass"
        self.rect_width = 200
        self.rect_height = 150
        self.draw_circle = False  # Toggle between box and circle
        self.rect_x = 50
        self.rect_y = 50

        wndClass = win32gui.WNDCLASS()
        wndClass.lpfnWndProc = self.wndProc
        wndClass.hInstance = self.hInstance
        wndClass.lpszClassName = self.className
        wndClass.hCursor = win32gui.LoadCursor(None, win32con.IDC_ARROW)
        wndClass.hbrBackground = win32con.COLOR_WINDOW
        wndClass.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW

        win32gui.RegisterClass(wndClass)

        screen_w = win32api.GetSystemMetrics(0)
        screen_h = win32api.GetSystemMetrics(1)

        self.hwnd = win32gui.CreateWindowEx(
            win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST,
            self.className,
            None,
            win32con.WS_POPUP,
            0, 0,
            screen_w, screen_h,
            None, None,
            self.hInstance,
            None
        )

        win32gui.SetLayeredWindowAttributes(self.hwnd, 0x000000, 0, win32con.LWA_COLORKEY)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

    def wndProc(self, hwnd, msg, wParam, lParam):
        if msg == win32con.WM_PAINT:
            hdc, paintStruct = win32gui.BeginPaint(hwnd)
            self.draw(hdc)
            win32gui.EndPaint(hwnd, paintStruct)
            return 0
        elif msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
        return win32gui.DefWindowProc(hwnd, msg, wParam, lParam)

    def draw(self, hdc):
        pen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(255, 0, 0))
        old_pen = win32gui.SelectObject(hdc, pen)

        center_x = win32api.GetSystemMetrics(0) // 2
        center_y = win32api.GetSystemMetrics(1) // 2

        left = center_x - self.rect_width // 2
        top = center_y - self.rect_height // 2
        right = center_x + self.rect_width // 2
        bottom = center_y + self.rect_height // 2

        if (self.rect_x | self.rect_y):
            right = self.rect_x
            bottom = self.rect_y

        if self.draw_circle:
            win32gui.Ellipse(hdc, left, top, right, bottom)
        else:
            win32gui.Rectangle(hdc, left, top, right, bottom)

        win32gui.SelectObject(hdc, old_pen)
        win32gui.DeleteObject(pen)

    def redraw(self):
        win32gui.InvalidateRect(self.hwnd, None, True)
        win32gui.UpdateWindow(self.hwnd)

    def message_loop(self):
        while True:
            # Simple example: resize box over time
            self.rect_width = (self.rect_width + 1) % 400 + 50
            self.rect_height = (self.rect_height + 2) % 300 + 50

            # Toggle shape every few seconds (for demo)
            if int(time.time()) % 5 == 0:
                self.draw_circle = not self.draw_circle

            self.redraw()
            win32gui.PumpWaitingMessages()
            time.sleep(0.05)