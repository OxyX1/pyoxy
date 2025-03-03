import sys
import os
import shutil
import subprocess
import ctypes
import pyautogui
import requests
from bs4 import BeautifulSoup

class tools:
    class console:
        def write(string):
            print(string)

        def read(string):
            input(string)

        def exit():
            sys.exit()
    
    class system:
        class edit:
            def move(source, destionation):
                try:
                    shutil.move(source, destionation)
                except Exception as e:
                    print(f'Error: {e}')

            def open(path):
                try:
                    subprocess.Popen(path)
                except Exception as e:
                    print(f'Error {e}')

            def wallpaper(path):
                try:
                    ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
                except Exception as e:
                    print(f'Error {e}')

        class control:
            def mouse(x, y):
                pyautogui.moveTo(x=x, y=y)
                print(f'mouse relocated to {x}:{y}')

            def keyboard(text):
                pyautogui.write(text)
                print(f'written on keyboard')

        class Detection:
            @staticmethod
            def imgesp(image, confidence=0.8, action=None, *args, **kwargs):
                matches = list(pyautogui.locateAllOnScreen(image, confidence=confidence))
                if matches and action:
                    return action(*args, **kwargs)
                return matches 

            @staticmethod
            def coloresp(X, Y, R, G, B, tol=10, action=None, *args, **kwargs):
                match = pyautogui.pixelMatchesColor(x=X, y=Y, expectedRGBColor=(R, G, B), tolerance=tol)
                if match and action:
                    return action(*args, **kwargs)
                return match

    class override:
        class screen:
            def gdi32_force_pixel_color_change(X, Y, COLOR=0x0000FF):
                hdc = ctypes.windll.user32.GetDC(0)
                ctypes.windll.gdi32.SetPixel(hdc, X, Y, COLOR)
                ctypes.windll.user32.ReleaseDC(0, hdc)

    class network:
        pass

    class info:
        class web:
            @staticmethod
            def scrape(domain, Element=None, css=None, all=True):
                response = requests.get(url=domain)
                soup = BeautifulSoup(response.text, "html.parser")

                if all:
                    return soup.prettify()

                if css:
                    elements = soup.select(css)
                elif Element:
                    elements = soup.find_all(Element)
                else:
                    return None
            
                return [element.text for element in elements] if elements else None