import enclib
import os
import zlib

# todo abstract out of bread_client to here
# todo merge example_headless into here and make it a good example


def connect_system(s):
    if s.ip and s.connect():
        with open(f"app/server_ip", "wb") as f:
            f.write(str(s.ip[0]+":"+str(s.ip[1])).encode())
        print("Loading account keys...")
        if os.path.exists(f'app/key'):
            with open(f'app/key', 'rb') as f:
                key_data = f.read()
            print(" - Key data loaded")
            uid, ipk = str(key_data[:8])[2:-1], key_data[8:]
            uname, level, r_coin, d_coin = unlock(s, uid, ipk)
            return uname, level, r_coin, d_coin
        else:
            print(" - No keys found")
            login()
    else:  # connection failed, switch to ip input screen
        s.ip = input("Enter server IP: ").split(":")
        connect_system()


def unlock(s, uid, ipk):
    while True:
        if os.path.exists("app/password.txt"):  # this is for testing ONLY
            with open("app/password.txt", "r") as f:
                acc_pass = f.read()
        else:
            acc_pass = input(f"Enter account passcode for {uid}: ")
        if acc_pass == "":
            print("ERROR: Password Blank\n- Top tip, type something in the password box.")
        else:
            try:
                user_pass = enclib.pass_to_key(acc_pass, default_salt, 50000)
                ipk = enclib.dec_from_pass(ipk, user_pass[:40], user_pass[40:])
                s.send_e(f"ULK:{uid}🱫{ipk}")
                ulk_resp = s.recv_d(128)
                if ulk_resp == "SESH_T":
                    print("ERROR: This accounts session is taken.")
                elif ulk_resp == "N":
                    print("ERROR: Incorrect Password\n- How exactly did you manage to trigger this.")
                else:
                    uname, level, r_coin, d_coin = ulk_resp.split("🱫")
                    if r_coin.endswith(".0"):
                        r_coin = r_coin[:-2]
                    if d_coin.endswith(".0"):
                        d_coin = d_coin[:-2]
                    print(f"Logged in as {uname} ({level})\n - Coins: {r_coin}R {d_coin}D")
                    return uname, level, r_coin, d_coin
            except zlib.error:
                print("ERROR: Incorrect Password")


# screen to collect data for regenerate master key
def login():
    drive = None
    load_from_usb = input("Load from USB? (y/n): ")
    if load_from_usb.lower() == "y":
        print("Scanning for USB...")
        drive = enclib.drive_insert_detector()
        with open(drive+"mkey", "r", encoding="utf-8") as f:
            name_or_uid, pass_code, pin_code = f.read().split("🱫")
        print(name_or_uid, pass_code, pin_code)
        print("Loaded from USB")
    else:
        print("Enter account details")
        name_or_uid = input("Input Name or UID: ")
        pass_code = input("Input Passcode: ")
        pin_code = input("Input Pincode: ")

        if len(name_or_uid) == 8 and len(pass_code) == 15 and pin_code:
            #self.ids.start_regen_button.disabled = False
            pass
        elif 8 < len(name_or_uid) < 29 and "#" in name_or_uid and len(pass_code) == 15 and pin_code:
            pass
            #self.ids.start_regen_button.disabled = False
        else:
            pass
            #self.ids.start_regen_button.disabled = True

    input()

    # todo account login from command line


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
