from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.clock import Clock
import json
import requests
import threading

LOGIN_FILE = "logins.json"
SETTINGS_FILE = "settings.json"
DEFAULT_PASSWORD = "bukashka"  # Asosiy parol

def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"first_time": True}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

def load_logins():
    try:
        with open(LOGIN_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_logins(logins):
    with open(LOGIN_FILE, "w") as file:
        json.dump(logins, file, indent=4)

def login_to_emaktab(login, password):
    url = "https://login.emaktab.uz/login"
    headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"login": login, "password": password}
    session = requests.Session()
    response = session.post(url, data=data, headers=headers)
    return "userfeed" in response.url

class PasswordScreen(Screen):
    def on_enter(self):
        settings = load_settings()
        if not settings.get("first_time", True):
            Clock.schedule_once(lambda dt: self.switch_to_main(), 0.1)
        else:
            self.show_password_dialog()
    
    def switch_to_main(self):
        if "main" in [screen.name for screen in self.manager.screens]:
            self.manager.current = "main"
    
    def show_password_dialog(self):
        self.dialog = MDDialog(
            title="Kirish uchun parolni kiriting",
            type="custom",
            content_cls=MDTextField(hint_text="Parol", password=True),
            buttons=[
                MDRaisedButton(text="OK", on_release=self.check_password)
            ]
        )
        self.dialog.open()

    def check_password(self, instance):
        entered_password = self.dialog.content_cls.text
        if entered_password == DEFAULT_PASSWORD:
            settings = load_settings()
            settings["first_time"] = False
            save_settings(settings)
            self.dialog.dismiss()
            Clock.schedule_once(lambda dt: self.switch_to_main(), 0.1)
        else:
            self.dialog.title = "Noto‘g‘ri parol!"

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

class EmaktabApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PasswordScreen(name="password"))
        sm.add_widget(MainScreen(name="main"))
        return sm

if __name__ == "__main__":
    EmaktabApp().run()
