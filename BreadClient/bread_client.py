import base64
import os
import random
import threading
import time
import subprocess
import zlib

import bread_kv
import enclib
from datetime import datetime
from kivy.app import App as KivyApp
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.graphics import Line, Color, RoundedRectangle
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.image import AsyncImage
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.utils import platform, get_color_from_hex as rgb


# hashes client file
app_hash = enclib.hash_a_file("bread_client.py")

# updates sha.txt with new app_hash
version = None
if os.path.exists("sha.txt"):
    bread_kv.kv()
    with open("sha.txt", "r", encoding="utf-8") as f:
        latest_sha_, version, tme_, bld_num_, run_num_ = f.readlines()[-1].split("§")
    print("prev", version, tme_, bld_num_, run_num_)
    release_major, major, build, run = version.replace("V", "").split(".")
    if latest_sha_ != app_hash:
        run = int(run)+1
        with open("sha.txt", "a+", encoding="utf-8") as f:
            f.write(f"\n{app_hash}§V{release_major}.{major}.{build}.{run}"
                    f"§TME-{str(datetime.now())[:-4].replace(' ', '_')}"
                    f"§BLD_NM-{bld_num_[7:]}§RUN_NM-{int(run_num_[7:])+1}")
            print(f"crnt V{release_major}.{major}.{build}.{run} "
                  f"TME-{str(datetime.now())[:-4].replace(' ', '_')} "
                  f"BLD_NM-{bld_num_[7:]} RUN_NM-{int(run_num_[7:])+1}")


# creates a popup
def popup(popup_type, reason):
    App.popup_text = reason
    if popup_type == "error":
        App.popup = Factory.ErrorPopup()
    if popup_type == "success":
        App.popup = Factory.SuccessPopup()
    App.popup.open()
    

# connects to sever with ip and port from file or user input
def connect_system():
    if s.ip and s.connect(b"CLI"):
        s.send_e(app_hash)
        version_info = s.recv_d()
        App.get_running_app().title = f"BreadClient-{version_info}"
        print(f"Running BreadClient {version_info}")
        with open(f"app/server_ip", "wb") as f:
            f.write(str(s.ip[0]+":"+str(s.ip[1])).encode())
        print("Loading account keys...")
        if os.path.exists(f'app/key'):
            with open(f'app/key', 'rb') as f:
                key_data = f.read()
            print(" - Key data loaded")
            App.uid, App.ipk = str(key_data[:8])[2:-1], key_data[8:]
            App.sm.switch_to(KeyUnlock(), direction="left")
        else:
            print(" - No keys found")
            App.sm.switch_to(LogInOrSignUp(), direction="left")
    else:  # connection failed, switch to ip input screen
        App.sm.switch_to(IpSet(), direction="left")


# screen to run connect_system()
class AttemptConnection(Screen):
    def on_enter(self, *args):
        App.get_running_app().title = f"BreadClient-VX.X.X.X"
        Clock.schedule_once(lambda dt: connect_system(), 1)  # todo make this retry


# screen to set a new ip and port
class IpSet(Screen):
    @staticmethod
    def try_connect(ip_address):
        if ip_address == "":
            popup("error", "IP Blank\n- Type an IP into the IP box")
        else:
            try:
                server_ip, server_port = ip_address.split(":")
                server_port = int(server_port)
            except ValueError or NameError:
                popup("error", "Invalid IP address\n- Please type a valid IP")
            else:
                if server_port < 1 or server_port > 65535:
                    popup("error", "IP Port Invalid\n- Port must be between 1 and 65535")
                else:
                    try:
                        ip_1, ip_2, ip_3, ip_4 = server_ip.split(".")
                        if all(i.isdigit() and 0 <= int(i) <= 255 for i in [ip_1, ip_2, ip_3, ip_4]):
                            s.ip = [server_ip, server_port]
                            App.sm.switch_to(AttemptConnection(), direction="left")
                        else:
                            popup("error", "IP Address Invalid\n- Address must have integers between 0 and 255")
                    except ValueError or NameError:
                        popup("error", "IP Address Invalid\n- Address must be in the format 'xxx.xxx.xxx.xxx")


# default screen to show after connection if no keys are found
class LogInOrSignUp(Screen):
    pass


# screen to unlock ip key
class KeyUnlock(Screen):
    passcode_prompt_text = StringProperty()
    pwd = ObjectProperty(None)
    counter = 0

    def on_pre_enter(self, *args):
        self.passcode_prompt_text = f"Enter passcode for account {App.uid}"
        if os.path.exists("app/password.txt"):  # this is for testing ONLY
            with open("app/password.txt", "r") as f:
                self.pwd.text = f.read()
                self.login()

    def login(self):
        if self.pwd.text == "":
            self.counter += 1
            if self.counter != 3:
                popup("error", "Password Blank\n- Top tip, type something in the password box.")
            else:
                popup("error", "Password Blank\n- WHY IS THE BOX BLANK?")
        else:
            try:
                user_pass = enclib.pass_to_key(self.pwd.text, enclib.default_salt)
                ipk = enclib.dec_from_pass(App.ipk, user_pass[:40], user_pass[40:])
                s.send_e(f"ULK:{App.uid}🱫{ipk}")
                ulk_resp = s.recv_d(128)
                if ulk_resp == "SESH_T":
                    popup("error", "This accounts session is taken.")
                elif ulk_resp == "N":
                    popup("error", "Incorrect Password")
                    self.pwd.text = ""
                else:
                    App.uname, App.level, App.r_coin, App.d_coin = ulk_resp.split("🱫")
                    if App.r_coin.endswith(".0"):
                        App.r_coin = App.r_coin[:-2]
                    if App.d_coin.endswith(".0"):
                        App.d_coin = App.d_coin[:-2]
                    print(f"Logged in as {App.uname} ({App.level})\n - Coins: {App.r_coin}R {App.d_coin}D")
                    App.sm.switch_to(Home(), direction="left")
            except zlib.error:
                popup("error", "Incorrect Password")
                self.pwd.text = ""


# screen to create a new account master key
class CreateKey(Screen):
    pass_code_text = StringProperty()
    pin_code_text = StringProperty()
    rand_confirm_text = StringProperty()
    rand_confirmation = None

    def generate_master_key(self, master_key, salt, depth_time, current_depth=0):
        App.mkey, App.pin_code = enclib.generate_master_key(master_key, salt, depth_time, current_depth, self)

    def on_pre_enter(self, *args):
        App.path = "make"
        acc_key = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=int(15)))
        time_depth = random.uniform(3, 5)
        threading.Thread(target=self.generate_master_key, args=(acc_key[:6].encode(),
                         acc_key[6:].encode(), time_depth,), daemon=True).start()
        self.pin_code_text = f"Generating Key and Pin ({time_depth}s left)"
        acc_key_print = f"{acc_key[:5]}-{acc_key[5:10]}-{acc_key[10:15]}"
        self.pass_code_text = f"Your Account Key is: {acc_key_print}"
        App.acc_key = acc_key

    def continue_confirmation(self, confirmation_code):
        if self.rand_confirmation:
            if confirmation_code == "":
                popup("error", "Confirmation Empty")
            elif confirmation_code == self.rand_confirmation:
                if platform in ["win", "linux"]:
                    App.sm.switch_to(UsbSetup(), direction="left")
                else:
                    App.sm.switch_to(Captcha(), direction="left")
            else:
                popup("error", "Incorrect Confirmation Number")


# screen to set up a USB to write the master key to
class UsbSetup(Screen):
    usb_text = StringProperty()
    skip_text = StringProperty()

    def detect_usb(self):  # todo linux version
        App.new_drive = enclib.drive_insert_detector()
        self.usb_text = f"USB detected at {App.new_drive}\n" \
                        f"Do not unplug USB until your account is created and you are on the home screen"
        self.skip_text = "Continue"

    def on_pre_enter(self, *args):
        self.usb_text = "Detecting USB drive....\nPlease connect your USB drive\n" \
                        "(If it is already connected please disconnect and reconnect it)"
        self.skip_text = "Skip USB setup"
        threading.Thread(target=self.detect_usb, daemon=True).start()


# screen to collect data for regenerate master key
class ReCreateKey(Screen):
    load_text = StringProperty()
    name_or_uid = ObjectProperty()
    pass_code = ObjectProperty()
    pin_code = ObjectProperty()
    drive = None

    def on_pre_enter(self, *args):
        self.load_text = "Load from USB"

    def load_data(self):
        with open(self.drive+"mkey", "r", encoding="utf-8") as f:
            self.name_or_uid.text, self.pass_code.text, self.pin_code.text = f.read().split("🱫")

    def detect_usb(self):
        new_drive = enclib.drive_insert_detector()
        self.load_text = "USB loaded"
        self.drive = new_drive
        Clock.schedule_once(lambda dt: self.load_data())

    def load_from_usb(self):
        self.load_text = "Detecting USB"
        self.ids.load_from_usb_button.disabled = True
        threading.Thread(target=self.detect_usb, daemon=True).start()

    def toggle_button(self):
        if len(self.name_or_uid.text) == 8 and len(self.pass_code.text) == 15 and self.pin_code.text:
            self.ids.start_regen_button.disabled = False
        elif 8 < len(self.name_or_uid.text) < 29 and "#" in self.name_or_uid.text and \
                len(self.pass_code.text) == 15 and self.pin_code.text:
            self.ids.start_regen_button.disabled = False
        else:
            self.ids.start_regen_button.disabled = True

    def start_regeneration(self):
        if len(self.name_or_uid.text) == 8 and len(self.pass_code.text) == 15 and self.pin_code.text:
            App.path, App.uid = "login", self.name_or_uid.text
            App.pass_code, App.pin_code = self.pass_code.text, self.pin_code.text
            App.sm.switch_to(ReCreateGen(), direction="left")
        if 8 < len(self.name_or_uid.text) < 29 and "#" in self.name_or_uid.text and \
                len(self.pass_code.text) == 15 and self.pin_code.text:
            App.path, App.uname = "login", self.name_or_uid.text
            App.pass_code, App.pin_code = self.pass_code.text, self.pin_code.text
            App.sm.switch_to(ReCreateGen(), direction="left")


# screen to regenerate master key
class ReCreateGen(Screen):
    gen_left_text = StringProperty()

    def regenerate_master_key(self, master_key, salt, depth_to, current_depth=0):
        App.mkey = enclib.regenerate_master_key(master_key, salt, depth_to, current_depth, self)
        Clock.schedule_once(lambda dt: App.sm.switch_to(Captcha(), direction="left"))

    def on_enter(self, *args):
        self.gen_left_text = f"Generating master key"
        threading.Thread(target=self.regenerate_master_key, args=(App.pass_code[:6].encode(),
                         App.pass_code[6:].encode(), int(enclib.to_base(36, 10, App.pin_code)),),
                         daemon=True).start()


# screen to verify a captcha
class Captcha(Screen):
    captcha_prompt_text = StringProperty()
    captcha_inp = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.captcha_prompt_text = "Waiting for captcha..."

    def on_enter(self, *args):
        s.send_e("CAP")
        self.get_captcha()

    def get_captcha(self):
        image = s.recv_d(32768)  # todo remove the need for a file
        with open('resources/captcha.jpg', 'wb') as f:
            f.write(image)
        self.captcha_prompt_text = f"Enter the text below"
        self.ids.captcha_image.source = 'resources/captcha.jpg'

    def try_captcha(self):
        if len(self.captcha_inp.text) == 10:
            s.send_e(self.captcha_inp.text.replace(" ", "").replace("1", "I").replace("0", "O").upper())
            if s.recv_d() != "V":
                popup("error", "Captcha Failed")
            elif App.path == "make":
                App.sm.switch_to(NacPass(), direction="left")
            elif App.path == "login":
                if App.uname:
                    s.send_e(f"LOG:{App.mkey}🱫u🱫{App.uname}")
                else:
                    s.send_e(f"LOG:{App.mkey}🱫i🱫{App.uid}")
                log_resp = s.recv_d()
                if log_resp == "IMK":
                    popup("error", "Invalid Master Key")
                    App.sm.switch_to(ReCreateKey(), direction="left")
                elif log_resp == "NU":
                    popup("error", "Username/UID does not exist")
                    App.sm.switch_to(ReCreateKey(), direction="right")
                else:
                    if App.uname:
                        App.uid = s.recv_d()
                    App.sm.switch_to(LogUnlock(), direction="left")


# screen to create a new password
class NacPass(Screen):
    nac_password_1 = ObjectProperty(None)
    nac_password_2 = ObjectProperty(None)

    def set_nac_password(self):
        if self.nac_password_1.text == "":
            popup("error", "Password 1 Blank")
        elif self.nac_password_2.text == "":
            popup("error", "Password 2 Blank")
        elif len(self.nac_password_1.text) < 9:
            popup("error", "Password Invalid\n- Password must be at least 9 characters")
        elif self.nac_password_1.text != self.nac_password_2.text:
            popup("error", "Password Mismatch\n- Passwords must be the same")
        else:
            pass_send = enclib.pass_to_key(self.nac_password_1.text, enclib.default_salt)
            if App.path == "CHANGE_PASS":
                s.send_e(pass_send)
                App.sm.switch_to(TwoFacLog(), direction="left")
            else:
                s.send_e(f"NAC:{App.mkey}🱫{pass_send}")
                App.sm.switch_to(TwoFacSetup(), direction="left")


# screen to log in to an account
class LogUnlock(Screen):
    pwd = ObjectProperty(None)
    passcode_prompt_text = StringProperty()

    def on_pre_enter(self, *args):
        self.passcode_prompt_text = f"Enter passcode for account {App.uid}"

    def login(self):
        if self.pwd.text == "":
            popup("error", "Password Blank\n- The question is, why is it blank?")
        else:
            try:
                user_pass = enclib.pass_to_key(self.pwd.text, enclib.default_salt)
                s.send_e(user_pass)
                ipk = s.recv_d()
                if ipk == "N":
                    popup("error", "Incorrect Password")
                    self.pwd.text = ""
                else:
                    App.ipk = ipk
                    App.sm.switch_to(TwoFacLog(), direction="left")
            except zlib.error:
                popup("error", "Incorrect Password")
                self.pwd.text = ""


# screen to set up 2fa
class TwoFacSetup(Screen):
    two_fac_wait_text = StringProperty()
    two_fac_code = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.two_fac_wait_text = "Waiting for 2fa QR code..."

    def on_enter(self, *args):
        App.uid, secret_code = s.recv_d().split("🱫")
        secret_code = base64.b32encode(secret_code.encode()).decode().replace('=', '')
        print(secret_code)  # todo mention in UI text
        self.ids.two_fac_qr.source = "https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl=otpauth%3A%2" \
                                     f"F%2Ftotp%2F{App.uid}%3Fsecret%3D{secret_code}%26issuer%3DBreadClient"
        self.two_fac_wait_text = "Scan this QR with your authenticator, then enter code to confirm.\n" \
                                 f"Your User ID (UID) is {App.uid}"

    def confirm_2fa(self):
        if self.two_fac_code.text == "":
            popup("error", "2FA Code Blank\n- Please enter a 2FA code")
        elif len(self.two_fac_code.text) != 6:
            popup("error", "Invalid 2FA Code")
        else:
            s.send_e(self.two_fac_code.text.replace(" ", ""))
            ipk = s.recv_d()
            if ipk == "N":
                popup("error", "2FA Failed\n- Please Try Again")
            else:
                with open("app/key", "wb") as f:
                    f.write(App.uid.encode()+ipk)
                App.uname, App.level, App.r_coin, App.d_coin = s.recv_d().split("🱫")
                if App.r_coin.endswith(".0"):
                    App.r_coin = App.r_coin[:-2]
                if App.d_coin.endswith(".0"):
                    App.d_coin = App.d_coin[:-2]
                if App.new_drive:
                    with open(f"{App.new_drive}mkey", "w", encoding="utf-8") as f:
                        f.write(f"{App.uid}🱫{App.acc_key}🱫{App.pin_code}")
                print(f"Logged in as {App.uname} ({App.level})\n - Coins: {App.r_coin}R {App.d_coin}D")
                App.sm.switch_to(Home(), direction="left")


# screen to verify 2fa code on login
class TwoFacLog(Screen):
    two_fac_code = ObjectProperty(None)

    def confirm_2fa(self):
        if self.two_fac_code.text == "":
            popup("error", "2FA Code Blank\n- Please enter a 2FA code")
        elif len(self.two_fac_code.text) != 6:
            popup("error", "Invalid 2FA Code")
        else:
            s.send_e(self.two_fac_code.text.replace(" ", ""))
            two_fa_valid = s.recv_d()
            if two_fa_valid == "N":
                popup("error", "2FA Failed\n- Please Try Again")
            elif App.path == "CHANGE_PASS":
                with open("app/key", "wb") as f:
                    f.write(App.uid.encode()+two_fa_valid)
                App.sm.switch_to(Settings(), direction="left")
                popup("success", "Password Changed")
            else:
                with open("app/key", "wb") as f:
                    f.write(App.uid.encode()+App.ipk)
                App.uname, App.level, App.r_coin, App.d_coin = two_fa_valid.split("🱫")
                if App.r_coin.endswith(".0"):
                    App.r_coin = App.r_coin[:-2]
                if App.d_coin.endswith(".0"):
                    App.d_coin = App.d_coin[:-2]
                print(f"Logged in as {App.uname} ({App.level})\n - Coins: {App.r_coin}R {App.d_coin}D")
                App.sm.switch_to(Home(), direction="left")


class DefaultScreen(Screen):
    r_coins = StringProperty()
    d_coins = StringProperty()

    def set_coins(self):
        self.r_coins = App.r_coin + " R"
        self.d_coins = App.d_coin + " D"


# the home screen
class Home(DefaultScreen):
    welcome_text = StringProperty()
    request_hist_counter = 0

    def on_enter(self, *args):
        self.ids.level_bar_text.text = f"Auth level {App.level}"
        [self.add_transaction(transaction) for transaction in App.request_hist]
        App.request_hist = []

    def add_transaction(self, transaction):
        self.ids.request_hist.add_widget(Label(text=transaction, font_size=16, color=(1, 1, 1, 1), size_hint_y=None,
                                               height=40+transaction.count("\n")*20, halign="left", markup=True))
        self.request_hist_counter += 1
        if self.ids.request_hist_scroll.scroll_y == 0:
            scroll_down = True
        else:
            scroll_down = False
        if self.request_hist_counter > 101:
            self.ids.request_hist.remove_widget(self.ids.public_chat.children[-1])
            self.ids.request_hist.children[-1].text = "ONLY SHOWING LATEST 100 request_hist"
            self.request_hist_counter -= 1
        message_height = 0
        for i in reversed(range(self.request_hist_counter)):
            self.ids.request_hist.children[i].y = message_height
            self.ids.request_hist.children[i].x = 0
            message_height += self.ids.request_hist.children[i].height
        self.ids.request_hist.height = message_height
        if scroll_down:
            self.ids.request_hist_scroll.scroll_y = 0
        else:
            pass  # todo make stay still

    def on_pre_enter(self, *args):
        self.set_coins()
        self.welcome_text = f"Welcome back {App.uname}"


# screen for public chat room
class Console(DefaultScreen):
    public_room_msg_counter = 0
    public_room_inp = ObjectProperty(None)

    def msg_watch(self):  # look for new messages
        while True:
            msg_author, msg_content = s.recv_d().split("🱫")
            Clock.schedule_once(lambda dt: self.add_msg(msg_author, msg_content))

    def on_pre_enter(self, *args):
        self.set_coins()
        self.ids.public_room_inp.focus = True
        threading.Thread(target=self.msg_watch, daemon=True).start()

    def add_msg(self, name, text):
        if "https://" in text or "http://" in text:
            self.ids.public_chat.add_widget(AsyncImage(source=text, size_hint_y=None, height=300, anim_delay=0.05))
        else:
            if name == "SERVER":
                self.ids.public_chat.add_widget(Label(text=f"[color=#f46f0eff]{name}[/color] [color=#858d8fff] "
                                                           f"{str(datetime.now())[:-7]}[/color] {text}", font_size=16,
                                                      color=(1, 1, 1, 1), size_hint_y=None, height=40, markup=True))
                App.request_hist.append(f"REQUEST: [color=#f46f0eff]1 R [/color]"
                                        f"[color=#14e42aff] GPU0-phi2 [/color]")
                App.r_coin = str(int(App.r_coin)+1)
                self.r_coins = App.r_coin+" R"
            else:
                self.ids.public_chat.add_widget(Label(text=f"[color=#14e42bff]{name}[/color] [color=#858d8fff] "
                                                           f"{str(datetime.now())[:-7]}[/color] {text}", font_size=16,
                                                      color=(1, 1, 1, 1), size_hint_y=None, height=40, markup=True))
        self.public_room_msg_counter += 1
        if self.ids.public_room_scroll.scroll_y == 0:
            scroll_down = True
        else:
            scroll_down = False
        if self.public_room_msg_counter > 101:
            self.ids.public_chat.remove_widget(self.ids.public_chat.children[-1])
            self.ids.public_chat.children[-1].text = "MESSAGES ABOVE DELETED DUE 100 MESSAGE LIMIT"
            self.public_room_msg_counter -= 1
        message_height = 0
        for i in range(self.public_room_msg_counter):
            self.ids.public_chat.children[i].y = message_height
            self.ids.public_chat.children[i].x = 0
            message_height += self.ids.public_chat.children[i].height
        self.ids.public_chat.height = message_height
        if scroll_down:
            self.ids.public_room_scroll.scroll_y = 0
        else:
            pass  # todo make stay still

    # todo add these as buttons to
    def send_public_message(self):
        if self.public_room_inp.text != "":
            self.add_msg(App.uname[:-4], self.public_room_inp.text)
            s.send_e(f"{self.public_room_inp.text}")
            if self.public_room_inp.text in ["LOGOUT_ALL", "LOGOUT"]:
                os.remove("app/key")
                os.remove("app/password.txt")
                os.remove("app/server_ip")
                os.remove("app")
                reload("reload")
            self.public_room_inp.text = ""


# screen for the store
class Store(DefaultScreen):
    def on_pre_enter(self, *args):
        self.set_coins()


# screen for viewing mesh network
class Mesh(DefaultScreen):
    GPU = {}
    tool = False
    configs = False

    def on_pre_enter(self, *args):
        self.set_coins()
        try:
            import IlluminationSDK.Tools.DebugTool as DebugTool
            self.tool = True
        except ModuleNotFoundError:
            s.send_e("GET:IlluminationSDK")
            if s.recv_file():
                pass
                #os.system("start IlluminationSDK.zip")
                #import IlluminationSDK.Tools.DebugTool as DebugTool
                #self.tool = True
            else:
                popup("error", "You do not have permission to use this feature")
                App.sm.switch_to(Home(), direction="left")

        if self.tool:
            try:
                subprocess.check_output(['ffmpeg'], text=True)
            except FileNotFoundError:
                print("FFmpeg not found - installing in another window")
                os.system("start winget install FFmpeg -e")
            except subprocess.CalledProcessError:
                pass

            # todo get GPU info, install CUDA/ROCKm if not installed
            if not self.GPU:
                self.GPU = DebugTool.get_best_accelerator()

            if self.GPU['manufacturer'] == "NVIDIA":
                if not DebugTool.check_cuda_toolkit():
                    print("CUDA Toolkit not found")
                    App.sm.switch_to(MeshConsent(), direction="left")
                try:
                    import torch
                    import pycuda.driver as cuda
                except ModuleNotFoundError:
                    print("PyTorch not found")
                    App.sm.switch_to(MeshConsent(), direction="left")

            #elif self.GPU['manufacturer'] == "AMD":
            #    if not DebugTool._check_rocm():
            #        print("ROCKm not found")
            #        App.sm.switch_to(MeshConsent(), direction="left")
            #    else:
            #        print("ROCKm found")

        if self.configs:
            print("Running config detection")

    def loaded_models(self):
        pass  # todo load AITools/LLMServer/model_config.py


# screen for consenting to mesh network and then downloading CUDA/ROCKm
class MeshConsent(Screen):
    mesh_consent_text = StringProperty()

    def on_pre_enter(self, *args):
        import DebugTool
        gpu = DebugTool.get_best_accelerator()
        self.mesh_consent_text = (f"GPU {gpu['name']} ({gpu['vram']}MB) Detected\nClick the consent button to "
                                  f"download the {gpu['manufacturer']}packages required to run AI models on your GPU "
                                  f"and connect to the mesh network\nBreadClient will close during the update")

    @staticmethod
    def on_consent():
        import DebugTool
        if not DebugTool.check_cuda_toolkit():
            print("CUDA Toolkit not found")

        #os.system("start nvidia.bat")
        App.stop(App.get_running_app())


# screen for changing account details and other settings
class Settings(DefaultScreen):
    uname = StringProperty()
    uid = StringProperty()
    uname_to = ObjectProperty(None)
    n_pass = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.set_coins()
        self.uname = App.uname
        self.uid = App.uid

    def change_name(self):
        if 4 < len(self.uname_to.text) < 25:
            s.send_e(f"CUN:{self.uname_to.text}")
            new_uname = s.recv_d()
            if new_uname != "N":
                App.uname = new_uname
                self.uname = App.uname
                popup("success", f"Username changed to {self.uname}")
                App.request_hist.append(f"Changed username to [color=#14e42aff]{self.uname}[/color]")
        else:
            popup("error", "Invalid Username\n- Username must be between 5 and 24 characters")

    def change_pass(self):
        if len(self.n_pass.text) < 9:
            popup("error", "Password Invalid\n- Password must be at least 9 characters")
        else:
            s.send_e(f"CUP:{enclib.pass_to_key(self.n_pass.text, enclib.default_salt)}")
            if s.recv_d() == "V":
                App.path = "CHANGE_PASS"
                App.sm.switch_to(NacPass(), direction="left")
            else:
                popup("error", "Incorrect Password\n- Please try again")


# screen for changing the colour scheme
class ColorSettings(DefaultScreen):
    selected_color = None
    color_list_old = None

    def on_pre_enter(self, *args):
        self.set_coins()
        self.color_list_old = App.col.copy()

    def select_color(self, color_name):
        self.selected_color = color_name
        self.ids.color_picker.color = App.col[color_name]

    def change_color(self, color=None):
        if not color:
            color = [round(col, 5) for col in self.ids.color_picker.color]
        if self.selected_color is not None:
            App.col[self.selected_color] = color
            with self.ids[self.selected_color+"_btn"].canvas:
                Color(*color)
                RoundedRectangle(size=self.ids[self.selected_color+"_btn"].size,
                                 pos=self.ids[self.selected_color+"_btn"].pos, radius=[10])

    def reset_colors(self, color=None):
        if self.selected_color:
            if color:
                self.change_color(self.color_list_old[self.selected_color])
            else:
                for color in App.col:
                    self.selected_color = color
                    self.change_color(self.color_list_old[color])

    @staticmethod  # call reload from KV file
    def reload():
        reload("reload")

    @staticmethod
    def save_colors():
        with open("resources/color_scheme.txt", "w", encoding="utf-8") as f:
            f.write(f"# CUSTOM COLOR SCHEME #\n")
            for color in App.col:
                hex_color = " #"
                for rgb1 in App.col[color]:
                    hex_color += hex(int(rgb1*255))[2:].zfill(2)
                f.write(f"{color}:{hex_color}\n")

    def default_theme(self, theme):  # set default theme
        if theme in ["purple", "pink", "green", "lime"]:
            App.col = App.theme[theme]
            for color in App.col:
                self.selected_color = color
                self.change_color(App.theme[theme][color])


# draw a circle with segments and a rotation
def draw_circle(self, segments, rotation=0):
    seg = [seg*0.36 for seg in segments]
    with self.canvas:
        seg_count = 0
        total = 0
        cols = [App.col['green'], App.col['red'], App.col['link_blue'], App.col['yellow'], App.col['orange']]
        for i in range(len(segments)):
            Color(*cols[i], mode="rgb")
            Line(circle=[self.center[0], self.center[1]+(self.center[1]/7), 150, total+rotation,
                         seg[i]+rotation+total], width=18, cap="none")
            total += seg[i]
            seg_count += 1


# draw a coloured triangle
def draw_triangle(self, color):
    with self.canvas:
        Color(*App.col[color])
        Line(points=[self.center[0], self.center[1]-(self.center[1]/2.5), self.center[0]-15,
                     self.center[1]-(self.center[1]/2.5)-30, self.center[0]+15, self.center[1]-(self.center[1]/2.5)-30,
                     self.center[0], self.center[1]-(self.center[1]/2.5)], width=2, cap="none")


# update a canvas with a color
def canvas_update(canvas, color):
    with canvas.canvas:
        Color(*color)
        RoundedRectangle(size=canvas.size, pos=canvas.pos, radius=[10])


# screen that is shown when the app is reloading
class Reloading(Screen):
    reload_text = StringProperty()

    def on_pre_enter(self, *args):
        self.reload_text = App.reload_text


# app class
class App(KivyApp):
    col = {"bread_purple": rgb("#6753fcff"), "bread_purple_dark": rgb("#6748a0ff"), "bread_cyan": rgb("#25be96ff"),
           "rcoin_orange": rgb("#f56f0eff"), "dcoin_blue": rgb("#16c2e1ff"), "link_blue": rgb("#509ae4ff"),
           "green": rgb("#14e42bff"), "yellow": rgb("#f3ef32ff"), "orange": rgb("#f38401ff"), "red": rgb("#fb1e05ff"),
           "grey": rgb("#3c3c32ff"), "bk_grey_1": rgb("#323232ff"), "bk_grey_2": rgb("#373737ff"),
           "bk_grey_3": rgb("#3c3c3cff")}
    theme = {"purple": col.copy()}
    theme.update({"pink": {"bread_purple": rgb("#ff4772ff"), "bread_purple_dark": rgb("#ff6d71ff"),
                           "bread_cyan": rgb("#c467b2ff"), "rcoin_orange": rgb("#f56f0eff"),
                           "dcoin_blue": rgb("#16c2e1ff"), "link_blue": rgb("#509ae4ff"), "green": rgb("#14e42bff"),
                           "yellow": rgb("#f3ef32ff"), "orange": rgb("#f38401ff"), "red": rgb("#fb1e05ff"),
                           "grey": rgb("#3c3c32ff"), "bk_grey_1": rgb("#323232ff"), "bk_grey_2": rgb("#373737ff"),
                           "bk_grey_3": rgb("#3c3c3cff")}})
    theme.update({"green": {"bread_purple": rgb("#009f70ff"), "bread_purple_dark": rgb("#658e37ff"),
                            "bread_cyan": rgb("#25be42ff"), "rcoin_orange": rgb("#f56f0eff"),
                            "dcoin_blue": rgb("#16c2e1ff"), "link_blue": rgb("#509ae4ff"), "green": rgb("#14e42bff"),
                            "yellow": rgb("#f3ef32ff"), "orange": rgb("#f38401ff"), "red": rgb("#fb1e05ff"),
                            "grey": rgb("#3c3c32ff"), "bk_grey_1": rgb("#323232ff"), "bk_grey_2": rgb("#373737ff"),
                            "bk_grey_3": rgb("#3c3c3cff")}})
    theme.update({"lime": {"bread_purple": rgb("#99bf38ff"), "bread_purple_dark": rgb("#998739ff"),
                           "bread_cyan": rgb("#dfbb38ff"), "rcoin_orange": rgb("#f56f0eff"),
                           "dcoin_blue": rgb("#16c2e1ff"), "link_blue": rgb("#509ae4ff"), "green": rgb("#14e42bff"),
                           "yellow": rgb("#f3ef32ff"), "orange": rgb("#f38401ff"), "red": rgb("#fb1e05ff"),
                           "grey": rgb("#3c3c32ff"), "bk_grey_1": rgb("#323232ff"), "bk_grey_2": rgb("#373737ff"),
                           "bk_grey_3": rgb("#3c3c3cff")}})

    if os.path.exists("resources/color_scheme.txt"):  # load color scheme
        with open("resources/color_scheme.txt", encoding="utf-8") as f:
            for color in f.readlines()[1:]:
                color_name, color = color.replace("\n", "").split(": ")
                col[color_name] = rgb(color)

    t_and_c = bread_kv.t_and_c()
    request_hist = []
    sm, mkey, ipk, pass_code, pin_code, acc_key = None, None, None, None, None, None
    path, reload_text, popup, popup_text, new_drive = None, "", None, "Popup Error", None
    uname, level, r_coin, d_coin = None, 99, None, None

    if platform in ["win", "linux"]:
        Window.size = (1264, 681)

    def build(self):
        self.icon = "bread_icon.jpg"

        # app defaults and window manager
        Builder.load_file("resources/bread.kv")
        App.sm = ScreenManager()
        [App.sm.add_widget(screen) for screen in [AttemptConnection(name="AttemptConnection"),
         IpSet(name="IpSet"), LogInOrSignUp(name="LogInOrSignUp"), KeyUnlock(name="KeyUnlock"),
         CreateKey(name="CreateKey"), UsbSetup(name="UsbSetup"), ReCreateKey(name="ReCreateKey"),
         ReCreateGen(name="ReCreateGen"), Captcha(name="Captcha"), NacPass(name="NacPass"),
         LogUnlock(name="LogUnlock"), TwoFacSetup(name="TwoFacSetup"), TwoFacLog(name="TwoFacLog"),
         Home(name="Home"), Console(name="Console"), Store(name="Store"), Mesh(name="Mesh"),
         MeshConsent(name="MeshConsent"), Settings(name="Settings"), ColorSettings(name="ColorSettings"),
         Reloading(name="Reloading")]]

        Window.bind(on_keyboard=on_keyboard)
        Config.set('input', 'mouse', 'mouse,disable_multitouch')
        Config.set('kivy', 'exit_on_escape', '0')
        return App.sm


# runs code on the detection of key presses
def on_keyboard(window, key, scancode, text, modifiers):
    if 'ctrl' in modifiers and text == 'r':
        reload("reload")
    if 'ctrl' in modifiers and text == 'x':
        App.get_running_app().stop()
    if 'ctrl' in modifiers and text == 'c':
        App.stop(App.get_running_app())  # Forces a crash
    if App.popup and key == 8:
        App.popup.dismiss()
        App.popup = None
    if App.r_coin:  # if logged in
        if 'alt' in modifiers and text == 'h':
            App.sm.switch_to(Home(), direction="up")
        if 'alt' in modifiers and text == 'c':
            App.sm.switch_to(Console(), direction="up")
        if 'alt' in modifiers and text == 'm':
            App.sm.switch_to(Mesh(), direction="up")


# reload function for the app
def reload(reason):
    current_screen = App.sm.current
    if reason == "reload":
        App.reload_text = "Reloading..."
    if reason == "crash":
        App.reload_text = "Rdisc crashed, reloading..."
        if s.ip:
            s.s.close()
    App.sm.current = "Reloading"
    Builder.unload_file("resources/bread.kv")
    while len(App.sm.screens) > 2:
        [App.sm.remove_widget(screen) for screen in App.sm.screens if screen.name not in ["Reloading", ""]]
    if reason == "reload":
        Builder.load_file("resources/bread.kv")
    [App.sm.add_widget(screen) for screen in [AttemptConnection(name="AttemptConnection"),
     IpSet(name="IpSet"), LogInOrSignUp(name="LogInOrSignUp"), KeyUnlock(name="KeyUnlock"),
     CreateKey(name="CreateKey"), UsbSetup(name="UsbSetup"), ReCreateKey(name="ReCreateKey"),
     ReCreateGen(name="ReCreateGen"), Captcha(name="Captcha"), NacPass(name="NacPass"),
     LogUnlock(name="LogUnlock"), TwoFacSetup(name="TwoFacSetup"), TwoFacLog(name="TwoFacLog"),
     Home(name="Home"), Console(name="Console"), Store(name="Store"), Mesh(name="Mesh"),
     MeshConsent(name="MeshConsent"), Settings(name="Settings"), ColorSettings(name="ColorSettings"),
     Reloading(name="Reloading")]]
    if reason == "reload":
        if current_screen == "_screen0":
            current_screen = "Home"
        App.sm.current = current_screen


# app entry point
if __name__ == "__main__":
    if not os.path.exists("app"):
        os.mkdir("app")

    if not os.path.exists("resources"):
        os.mkdir("resources")

    if not os.path.exists("resources/blank_captcha.png") or not os.path.exists("resources/blank_qr.png"):
        bread_kv.w_images()

    bread_kv.kv()
    crash_num = 0
    while True:
        try:
            s = enclib.ClientSocket()
            App().run()
            break
        except Exception as e:
            if "App.stop() missing 1 required positional argument: 'self'" in str(e):
                print("Crash forced by user.")
            else:
                crash_num += 1
                print(f"Error {crash_num} caught: {e}")
            if crash_num == 5:
                print("Crash loop detected, exiting app in 3 seconds...")
                time.sleep(3)
                break
            else:
                reload("crash")
