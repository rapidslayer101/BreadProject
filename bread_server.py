import sqlite3
import enclib
import time
import rsa
import zlib
import socket
import random
import requests
import threading
import csv
from datetime import datetime, timedelta
from captcha.image import ImageCaptcha


# custom exception for invalid data from a client
class InvalidClientData(Exception):
    pass


# class containing data for logged in clients
class Clients:
    logged_in_clients = []
    uid_keys = {}

    def __init__(self):
        self.db = sqlite3.connect('cnc_server.db', check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY NOT NULL UNIQUE,"
                        "creation_time DATE NOT NULL, master_key TEXT NOT NULL, secret TEXT NOT NULL,"
                        "user_pass TEXT NOT NULL, ipk1 TEXT, ipk2 TEXT, ipk3 TEXT, username TEXT NOT NULL, "
                        "last_online DATE NOT NULL, level FLOAT NOT NULL, r_coin FLOAT NOT NULL, d_coin FLOAT NOT NULL)")

    def login(self, u_id, ip, enc_key):
        self.logged_in_clients.append(u_id)
        self.logged_in_clients.append(ip)
        self.uid_keys.update({u_id: enc_key})

    def logout(self, u_id, ip):
        try:
            self.logged_in_clients.pop(self.logged_in_clients.index(u_id))
            self.logged_in_clients.pop(self.logged_in_clients.index(ip))
            self.uid_keys.pop(u_id)
            self.db.execute("UPDATE users SET last_online = ? WHERE user_id = ?", (str(datetime.now())[:-7], u_id))
            self.db.commit()
        except ValueError:
            pass

    def add_user(self, uid, master_key, secret, u_pass, ipk, username):
        now = str(datetime.now())[:-7]
        expiry_time = str(datetime.now()+timedelta(days=14))[:-7]
        self.db.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (uid, now,
                        enclib.pass_to_key(master_key, uid), enclib.enc_from_key(secret, u_pass),
                        enclib.pass_to_key(u_pass, uid), ipk+"🱫"+expiry_time, None,
                        None, username, now, 99, 0, 0))
        self.db.commit()

    def check_logged_in(self, uid, ip):
        if uid in self.logged_in_clients:
            return True
        elif ip in self.logged_in_clients:
            return True
        else:
            return False


clients = Clients()


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionResetError:  # client disconnection exception handler
            print(f"{args[0].uid}-{args[0].ip}:{args[0].port} DC")
            if args[0].ip in clients.logged_in_clients:
                clients.logout(args[0].uid, args[0].ip)
        except InvalidClientData:  # invalid client data exception handler  # todo log invalid requests
            print(f"{args[0].uid}-{args[0].ip}:{args[0].port} DC - modified/invalid client request")
            if args[0].ip in clients.logged_in_clients:
                clients.logout(args[0].uid, args[0].ip)
    return wrapper


class ClientLogin:
    cs, ip, port, enc_key, client_type, captcha_complete, version = None, None, None, None, None, False, None
    uid, ipk, master_key, u_pass, u_secret = None, None, None, None, None
    u_name, level, r_coin, d_coin = None, None, None, None

    @catch_exception
    def __init__(self, cs):
        self.cs = cs
        self.ip, self.port = str(cs).split("raddr=")[1][2:-2].split("', ")
        self.client_type = str(cs.recv(32))[2:-1]
        print(f"NEW CLIENT --- IP-{self.ip}:{self.port}")
        self.uid = None
        try:
            pub_key_cli = rsa.PublicKey.load_pkcs1(cs.recv(256))
        except ValueError:
            raise InvalidClientData
        enc_seed = enclib.rand_b96_str(36)
        cs.send(rsa.encrypt(enc_seed.encode(), pub_key_cli))
        self.enc_key = enclib.pass_to_key(enc_seed[:18], enc_seed[18:], 100000)
        self.login_loop()

    def send_e(self, text):  # encrypt and send to client
        try:
            self.cs.send(enclib.enc_from_key(text, self.enc_key))
        except zlib.error:
            raise ConnectionResetError

    def recv_d(self, buf_lim=1024):  # decrypt data from client
        try:
            return enclib.dec_from_key(self.cs.recv(buf_lim), self.enc_key)
        except zlib.error:
            raise ConnectionResetError

    @catch_exception
    def login_loop(self):
        if self.client_type == "CLI":
            cli_hash = self.recv_d()
            valid_version = False
            with open("BreadClient/sha.txt", "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.startswith(cli_hash):
                        latest_sha_, self.version, tme_, bld_num_, run_num_ = line.split("§")
                        valid_version = self.version
            if valid_version:
                self.send_e(valid_version)
                print("Client Connection --- Version:", self.version, tme_, bld_num_, run_num_)
            elif self.ip == "127.0.0.1":  # allows local testing
                self.send_e("VX.X.X.X")
                print("Headless Connection")
            else:
                print("Client Connection --- Invalid Version")
                raise InvalidClientData
        elif self.client_type == "HDL":
            print("Headless Connection")
        else:
            raise InvalidClientData
        login_request = self.recv_d()
        print(login_request)  # temp debug for dev
        if login_request.startswith("ULK:"):
            self.unlock_account(login_request)
        elif login_request == "CAP":
            self.login_captcha()
        elif login_request.startswith("LOG:") and self.client_type == "HDL":
            self.login(login_request)
        else:
            raise InvalidClientData

    @catch_exception
    def login_captcha(self):
        img = ImageCaptcha(width=280, height=90)
        captcha_text = "".join(random.choices("23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=int(10)))
        print(captcha_text)
        img.generate(captcha_text)  # todo remove the need for a file
        img.write(captcha_text, 'captcha.jpg')
        with open("captcha.jpg", "rb") as f:
            self.send_e(f.read())
        counter = 0
        while True:
            counter += 1
            captcha_attempt = self.recv_d()
            if captcha_attempt != captcha_text:
                self.send_e("N")
                if counter > 3:
                    time.sleep(10)  # rate limit
            else:
                self.send_e("V")
                self.captcha_complete = True
                break

        login_request = self.recv_d()
        print(login_request)
        if login_request.startswith("NAC:"):
            self.new_account(login_request)
        elif login_request.startswith("LOG:"):
            self.login(login_request)
        else:
            raise InvalidClientData

    @catch_exception
    def new_account(self, login_request):
        self.master_key, self.u_pass = login_request[4:].split("🱫")
        while True:  # create random unique user id
            self.uid = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=8))
            self.u_name = self.uid + "#" + str(random.randint(111, 999))
            if clients.db.execute("SELECT user_id FROM users WHERE user_id = ?", (self.uid,)).fetchone() is None:
                break
        self.u_secret = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXY"
                                               "abcdefghijklmnopqrstuvwxyz", k=8))
        self.send_e(f"{self.uid}🱫{self.u_secret}")
        while True:  # 2fa challenge
            code_challenge = self.recv_d()
            if requests.get(f"https://www.authenticatorapi.com/Validate.aspx?"
                            f"Pin={code_challenge}&SecretCode={self.u_secret}").content != b"True":
                self.send_e("N")
            else:
                self.ipk = enclib.rand_b96_str(24)
                self.send_e(enclib.enc_from_pass(self.ipk, self.u_pass[:40], self.u_pass[40:]))
                self.send_e(f"{self.u_name}🱫0🱫0🱫0")
                clients.add_user(self.uid, self.master_key, self.u_secret, self.u_pass,
                                 enclib.pass_to_key(self.ip+self.ipk, self.uid), self.u_name)
                self.main_loop()

    @catch_exception
    def login(self, login_request):
        master_key_c, search_for, uname_or_uid = login_request[4:].split("🱫")
        if search_for == "u":
            try:
                (self.uid, self.master_key, self.u_secret, self.u_pass, self.u_name, self.level, self.r_coin,
                 self.d_coin) = clients.db.execute("SELECT user_id, master_key, secret, user_pass, username, level,"
                                                   " r_coin, d_coin FROM users WHERE username = ?",
                                                   (uname_or_uid,)).fetchone()
            except TypeError:
                self.uid = None
                self.send_e("NU")  # user does not exist
        else:
            try:
                self.uid = uname_or_uid
                (self.master_key, self.u_secret, self.u_pass, self.u_name, self.level, self.r_coin,
                 self.d_coin) = clients.db.execute("SELECT master_key, secret, user_pass, username, level, r_coin,"
                                                   " d_coin FROM users WHERE user_id = ?", (uname_or_uid,)).fetchone()
            except TypeError:
                self.uid = None
                self.send_e("NU")  # user does not exist
        if self.uid:
            if enclib.pass_to_key(master_key_c, self.uid) != self.master_key:
                self.send_e("IMK")  # master key wrong
            else:
                self.send_e("V")
                if search_for == "u":
                    self.send_e(self.uid)
                while True:
                    u_pass_c = self.recv_d()
                    if enclib.pass_to_key(u_pass_c, self.uid) == self.u_pass:
                        self.ipk = enclib.rand_b96_str(24)
                        self.send_e(enclib.enc_from_pass(self.ipk, u_pass_c[:40], u_pass_c[40:]))
                        break
                    else:
                        self.send_e("N")
                self.u_secret = enclib.dec_from_key(self.u_secret, u_pass_c)
                while True:  # 2fa challenge
                    code_challenge = self.recv_d()
                    if requests.get(f"https://www.authenticatorapi.com/Validate.aspx?"
                                    f"Pin={code_challenge}&SecretCode={self.u_secret}").content != b"True":
                        self.send_e("N")
                    else:
                        break
                self.send_e(f"{self.u_name}🱫{self.level}🱫{self.r_coin}🱫{self.d_coin}")
                ipk1, ipk2, ipk3 = clients.db.execute(
                    "SELECT ipk1, ipk2, ipk3 FROM users WHERE user_id = ?",
                    (self.uid,)).fetchone()  # get ip keys from db

                expiry_time = str(datetime.now() + timedelta(days=14))[:-7]
                if ipk1 and ipk2 and ipk3:  # if 3 ip keys, replace the oldest one
                    oldest_ipk = "1"
                    oldest_ipk_d = datetime.strptime(ipk1.split("🱫")[1], "%Y-%m-%d %H:%M:%S")
                    if oldest_ipk_d > datetime.strptime(ipk2.split("🱫")[1], "%Y-%m-%d %H:%M:%S"):
                        oldest_ipk_d = datetime.strptime(ipk2.split("🱫")[1], "%Y-%m-%d %H:%M:%S")
                        oldest_ipk = "2"
                    if oldest_ipk_d > datetime.strptime(ipk3.split("🱫")[1], "%Y-%m-%d %H:%M:%S"):
                        oldest_ipk = "3"
                    clients.db.execute("UPDATE users SET ipk" + oldest_ipk + " = ? WHERE user_id = ?",
                                       (enclib.pass_to_key(self.ip+self.ipk, self.uid)+"🱫"+expiry_time, self.uid))
                elif not ipk1:  # save to empty ip key
                    clients.db.execute("UPDATE users SET ipk1 = ? WHERE user_id = ?",
                                       (enclib.pass_to_key(self.ip+self.ipk, self.uid)+"🱫"+expiry_time, self.uid))
                elif not ipk2:
                    clients.db.execute("UPDATE users SET ipk2 = ? WHERE user_id = ?",
                                       (enclib.pass_to_key(self.ip+self.ipk, self.uid)+"🱫"+expiry_time, self.uid))
                elif not ipk3:
                    clients.db.execute("UPDATE users SET ipk3 = ? WHERE user_id = ?",
                                       (enclib.pass_to_key(self.ip+self.ipk, self.uid)+"🱫"+expiry_time, self.uid))
                clients.db.commit()
                self.main_loop()

    @catch_exception
    def unlock_account(self, login_request):
        self.uid, self.ipk = login_request[4:].split("🱫")
        print(self.uid, self.ipk)
        if clients.check_logged_in(self.uid, self.ip):
            self.send_e("SESH_T")
        else:
            try:
                ipk1, ipk2, ipk3, self.u_name, self.level, self.r_coin, self.d_coin = \
                    clients.db.execute("SELECT ipk1, ipk2, ipk3, username, level, r_coin, "
                                       "d_coin FROM users WHERE user_id = ?", (self.uid,)).fetchone()
            except ValueError:
                self.send_e("N")  # User ID not found
            else:
                self.ipk = enclib.pass_to_key(self.ip + self.ipk, self.uid)

                def check_ipk(_ipk):
                    _ipk, ipk_e = _ipk.split("🱫")
                    if self.ipk != _ipk:
                        return False
                    elif datetime.now() < datetime.strptime(ipk_e, "%Y-%m-%d %H:%M:%S"):
                        return True
                    else:
                        return False

                if ipk1:
                    if check_ipk(ipk1):
                        self.send_e(f"{self.u_name}🱫{self.level}🱫{self.r_coin}🱫{self.d_coin}")
                        self.main_loop()
                if ipk2:
                    if check_ipk(ipk2):
                        self.send_e(f"{self.u_name}🱫{self.level}🱫{self.r_coin}🱫{self.d_coin}")
                        self.main_loop()
                if ipk3:
                    if check_ipk(ipk3):
                        self.send_e(f"{self.u_name}🱫{self.level}🱫{self.r_coin}🱫{self.d_coin}")
                        self.main_loop()
                self.send_e("N")

    def main_loop(self):
        pass


class Client(ClientLogin):
    def main_loop(self):
        clients.login(self.uid, self.ip, self.enc_key)
        print(f"{self.uid} logged in with IP-{self.ip}:{self.port}")
        while True:  # main loop
            request = self.recv_d()
            if not request:
                break
            print(request)  # temp debug for dev
            if request.startswith("LOGOUT_ALL"):  # deletes all IP keys
                clients.db.execute("UPDATE users SET ipk1 = ?, ipk2 = ?, ipk3 = ? WHERE user_id = ?",
                                   (None, None, None, self.uid))
                raise ConnectionResetError

            if request.startswith("LOGOUT"):  # deletes current IP key
                ipk1, ipk2, ipk3 = clients.db.execute("SELECT ipk1, ipk2, ipk3 FROM users WHERE user_id = ?",
                                                      (self.uid,)).fetchone()
                if ipk1:
                    if self.ipk == ipk1.split("🱫")[0]:
                        clients.db.execute("UPDATE users SET ipk1 = ? WHERE user_id = ?", (None, self.uid))
                        clients.db.commit()
                if ipk2:
                    if self.ipk == ipk2.split("🱫")[0]:
                        clients.db.execute("UPDATE users SET ipk2 = ? WHERE user_id = ?", (None, self.uid))
                        clients.db.commit()
                if ipk3:
                    if self.ipk == ipk3.split("🱫")[0]:
                        clients.db.execute("UPDATE users SET ipk3 = ? WHERE user_id = ?", (None, self.uid))
                        clients.db.commit()
                raise ConnectionResetError

            # elif request.startswith("DLAC:"):  # todo delete account
            #    pass

            elif request.startswith("CUP:"):  # change user password
                u_pass_c = request[4:]
                try:
                    self.u_pass, self.u_secret = clients.db.execute("SELECT user_pass, secret FROM users WHERE "
                                                                    "user_id = ?", (self.uid,)).fetchone()
                    if enclib.pass_to_key(u_pass_c, self.uid) != self.u_pass:
                        self.send_e("N")
                    else:
                        self.send_e("V")
                        n_u_pass = self.recv_d()
                        u_secret = enclib.dec_from_key(self.u_secret, u_pass_c)
                        while True:  # 2fa challenge
                            code_challenge = self.recv_d()
                            if requests.get(f"https://www.authenticatorapi.com/Validate.aspx?"
                                            f"Pin={code_challenge}&SecretCode={u_secret}").content != b"True":
                                self.send_e("N")
                            else:
                                break
                        n_ipk = enclib.rand_b96_str(24)
                        expiry_time = str(datetime.now()+timedelta(days=14))[:-7]
                        clients.db.execute("UPDATE users SET secret = ?, user_pass = ?, ipk1 = ?, ipk2 = ?, ipk3 = ? "
                                           "WHERE user_id = ?", (enclib.enc_from_key(self.u_secret, n_u_pass),
                                                                 enclib.pass_to_key(n_u_pass, self.uid),
                                                                 enclib.pass_to_key(self.ip + n_ipk,
                                                                                    self.uid) + "🱫" + expiry_time,
                                                                 None, None, None, self.uid))
                        clients.db.commit()
                        self.send_e(enclib.enc_from_pass(n_ipk, n_u_pass[:40], n_u_pass[40:]))
                except sqlite3.OperationalError:
                    self.send_e("N")

            # todo fix code
            elif request.startswith("CUN:"):  # change username
                n_u_name = request[4:]
                if not 4 < len(n_u_name) < 25:
                    raise InvalidClientData
                if "#" in n_u_name or "  " in n_u_name:
                    raise InvalidClientData
                counter = 0
                while True:
                    counter += 1
                    n_u_name_i = n_u_name + "#" + str(random.randint(111, 999))
                    try:
                        if clients.db.execute("SELECT * FROM users WHERE username = ?",
                                              (n_u_name_i,)).fetchone() is None:
                            clients.db.execute("UPDATE users SET username = ? WHERE user_id = ?",
                                               (n_u_name_i, self.uid))
                            clients.db.commit()
                            self.send_e(n_u_name_i)
                            self.u_name = n_u_name_i
                            break
                    except sqlite3.OperationalError:
                        if counter == 10:
                            self.send_e("N")
                            break

            # todo conversation with server
            elif request.startswith("CON"):  # join public chat
                print(request)
                self.send_e("SERVER🱫V")
                time.sleep(0.1)
                self.send_e("CLIENT2🱫Y")
                time.sleep(3)
                self.send_e("SERVER🱫completed task")
                self.add_action("REQ:CON", self.uid, "Posted CON in chat", 1)

            elif request.startswith("GET"):
                if request == "GET:DebugTool":
                    if self.level < 10:  # todo choose permission level
                        self.send_e("V")
                        # todo send debug tool
                    else:
                        self.send_e("N")

    @staticmethod
    def add_action(t_type, uid, desc, change):
        with open(f"actions.csv", "a", newline='', encoding="utf-8") as csv_file:
            csv.writer(csv_file).writerow([str(datetime.now())[:-7], t_type, uid, desc, change])


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 30678))
s.listen()
print(f"[*] Listening as {str(s).split('laddr=')[1][:-1]}")

while True:  # connection accept loop
    client_socket, client_address = s.accept()
    t = threading.Thread(target=Client, args=(client_socket,), daemon=True).start()
