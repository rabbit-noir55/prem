from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import MDList, OneLineListItem
import json
import requests
import threading

# JSON fayllar
LOGIN_FILE = "logins.json"
SETTINGS_FILE = "settings.json"

# Default login va parollar
default_logins = [
    {"login": "dimamatdinov", "password": "imamatdinov11"},
    {"login": "azamat_xudaybergenov", "password": "azamat2b"},
    {"login": "yangabayevna", "password": "yangabayevna2b"}
]

# JSON fayldan loginlarni yuklash
def load_logins():
    try:
        with open(LOGIN_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default_logins

def save_logins(logins):
    with open(LOGIN_FILE, "w") as file:
        json.dump(logins, file, indent=4)

# Login qilish funksiyasi
def login_to_emaktab(login, password):
    url = "https://login.emaktab.uz/login"
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"login": login, "password": password}
    session = requests.Session()
    response = session.post(url, data=data, headers=headers)
    return "userfeed" in response.url

class MainScreen(Screen):
    def start_login_process(self):
        logins = load_logins()
        self.ids.status_label.text = "Login jarayoni boshlandi..."
        threading.Thread(target=self.process_logins, args=(logins,), daemon=True).start()
    
    def process_logins(self, logins):
        success_count = 0
        for item in logins:
            login, password = item["login"], item["password"]
            if login_to_emaktab(login, password):
                success_count += 1
                self.ids.status_label.text += f"\n✅ {login} - Muvaffaqiyatli"
            else:
                self.ids.status_label.text += f"\n❌ {login} - Xato"
        self.ids.status_label.text += "\nVazifa bajarildi!"

class EditScreen(Screen):
    def on_pre_enter(self):
        self.load_login_list()

    def load_login_list(self):
        self.ids.login_list.clear_widgets()
        logins = load_logins()
        for item in logins:
            list_item = OneLineListItem(text=f"{item['login']}", on_release=self.edit_login)
            self.ids.login_list.add_widget(list_item)

    def edit_login(self, instance):
        pass  # Bu yerda tahrirlash funksiyasini qo'shamiz

class SettingScreen(Screen):
    pass  # Til sozlamalarini bu ekranga joylaymiz

class EmaktabApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(EditScreen(name="edit"))
        sm.add_widget(SettingScreen(name="settings"))
        return sm

if __name__ == "__main__":
    EmaktabApp().run()
