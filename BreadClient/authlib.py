import enclib
import os
import zlib


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
            return unlock(s, uid, ipk)
        else:
            print(" - No keys found")
            return login(s)

    else:  # connection failed, switch to ip input screen
        s.ip = input("Enter server IP: ").split(":")
        connect_system(s)


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
                user_pass = enclib.pass_to_key(acc_pass, enclib.default_salt, 50000)
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
def login(s):
    print("Insert Auth USB...")
    drive = enclib.drive_insert_detector()
    with open(drive+"mkey", "r", encoding="utf-8") as f:
        name_or_uid, pass_code, pin_code = f.read().split("🱫")
    print("Loaded keys from USB")
    print(name_or_uid, pass_code, pin_code)
    uid, uname = None, None
    if len(name_or_uid) == 8:
        uid = name_or_uid
    elif 8 < len(name_or_uid) < 29 and "#" in name_or_uid:
        uname = name_or_uid

    mkey = enclib.regenerate_master_key(pass_code[:6].encode(), pass_code[6:].encode(),
                                        int(enclib.to_base(36, 10, pin_code)))
    if uname:
        s.send_e(f"LOG:{mkey}🱫u🱫{name_or_uid}")
    elif uid:
        s.send_e(f"LOG:{mkey}🱫i🱫{name_or_uid}")

    log_resp = s.recv_d()
    if log_resp == "IMK":
        print("ERROR: Invalid Master Key")
        login(s)
    elif log_resp == "NU":
        print("ERROR: Username/UID does not exist")
        login(s)
    else:
        if uname:
            uid = s.recv_d()
        while True:
            acc_pass = input(f"Enter account passcode for {uid}: ")
            if acc_pass == "":
                print("ERROR: Password Blank\n- Top tip, type something in the password box.")
            acc_pass = enclib.pass_to_key(acc_pass, enclib.default_salt, 50000)
            s.send_e(acc_pass)
            ipk = s.recv_d()
            if ipk == "N":
                print("ERROR: Incorrect Password")
            else:
                break
        while True:
            two_fac_code = input("Enter 2FA Code: ")
            if two_fac_code == "":
                print("ERROR: 2FA Code Blank - Please enter a 2FA code")
            elif len(two_fac_code) != 6:
                print("Invalid 2FA Code")
            else:
                s.send_e(two_fac_code.replace(" ", ""))
                two_fa_valid = s.recv_d()
                if two_fa_valid == "N":
                    print("2FA Failed - Please Try Again")
                else:
                    with open("app/key", "wb") as f:
                        f.write(uid.encode()+ipk)
                    uname, level, r_coin, d_coin = two_fa_valid.split("🱫")
                    if r_coin.endswith(".0"):
                        r_coin = r_coin[:-2]
                    if d_coin.endswith(".0"):
                        d_coin = d_coin[:-2]
                    print(f"Logged in as {uname} ({level})\n - Coins: {r_coin}R {d_coin}D")
                    return uname, level, r_coin, d_coin
