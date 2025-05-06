import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
gdi32 = ctypes.windll.gdi32

# Win32 Constants
WS_OVERLAPPEDWINDOW = 0x00CF0000
WS_VISIBLE = 0x10000000
CW_USEDEFAULT = 0x80000000
WM_DESTROY = 0x0002

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)

# Window procedure callback
def wnd_proc(hwnd, msg, wparam, lparam):
    if msg == WM_DESTROY:
        user32.PostQuitMessage(0)
        return 0
    return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

# WNDCLASS structure
class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ('style', wintypes.UINT),
        ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', ctypes.c_int),
        ('cbWndExtra', ctypes.c_int),
        ('hInstance', wintypes.HINSTANCE),
        ('hIcon', wintypes.HICON),
        ('hCursor', wintypes.HCURSOR),
        ('hbrBackground', wintypes.HBRUSH),
        ('lpszMenuName', wintypes.LPCWSTR),
        ('lpszClassName', wintypes.LPCWSTR),
    ]

# Main GUI API
class OxyuGui:
    class Window:
        def __init__(self, title="Oxyu Window", width=800, height=600):
            self.title = title
            self.width = width
            self.height = height
            self.hInstance = kernel32.GetModuleHandleW(None)
            self.class_name = title
            self.wnd_proc = WNDPROC(wnd_proc)
            self._register_class()
            self._create_window()

        def REGISTERCLASS(self):
            wc = WNDCLASS()
            wc.style = 0
            wc.lpfnWndProc = self.wnd_proc
            wc.cbClsExtra = 0
            wc.cbWndExtra = 0
            wc.hInstance = self.hInstance
            wc.hIcon = None
            wc.hCursor = None
            wc.hbrBackground = gdi32.GetStockObject(1)  # WHITE_BRUSH
            wc.lpszMenuName = None
            wc.lpszClassName = self.class_name

            if not user32.RegisterClassW(ctypes.byref(wc)):
                raise ctypes.WinError()

        def CreateWindowWidget(self):
            self.hwnd = user32.CreateWindowExW(
                0,
                self.class_name,
                self.title,
                WS_OVERLAPPEDWINDOW | WS_VISIBLE,
                CW_USEDEFAULT, CW_USEDEFAULT,
                self.width, self.height,
                None, None,
                self.hInstance,
                None
            )
            if not self.hwnd:
                raise ctypes.WinError()

        def CreateSquare():
            pass

        def show(self):
            msg = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
