import sqlite3
import enclib
import time
import os
import rsa
import zlib
import socket
import random
import requests
import threading
from datetime import datetime, timedelta
from csv import writer, reader
from captcha.image import ImageCaptcha


# custom exception for invalid data from a client
class InvalidClientData(Exception):
    pass


# class containing data for logged in users
class Users:
    logged_in_users = []
    uid_keys = {}

    def __init__(self):
        self.db = sqlite3.connect('cnc_server.db', check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY NOT NULL UNIQUE,"
                        "creation_time DATE NOT NULL, master_key TEXT NOT NULL, secret TEXT NOT NULL,"
                        "user_pass TEXT NOT NULL, ipk1 TEXT, ipk2 TEXT, ipk3 TEXT, ipk4 TEXT, username TEXT NOT NULL, "
                        "last_online DATE NOT NULL, level FLOAT NOT NULL, r_coin FLOAT NOT NULL, d_coin FLOAT NOT NULL)")

    def login(self, u_id, ip, enc_key):
        self.logged_in_users.append(u_id)
        self.logged_in_users.append(ip)
        self.uid_keys.update({u_id: enc_key})

    def logout(self, u_id, ip):
        try:
            self.logged_in_users.pop(self.logged_in_users.index(u_id))
            self.logged_in_users.pop(self.logged_in_users.index(ip))
            self.uid_keys.pop(u_id)
            self.db.execute("UPDATE users SET last_online = ? WHERE user_id = ?", (str(datetime.now())[:-7], u_id))
            self.db.commit()
        except ValueError:
            pass

    def add_user(self, uid, master_key, secret, u_pass, ipk, username):
        now = str(datetime.now())[:-7]
        expiry_time = str(datetime.now()+timedelta(days=14))[:-7]
        self.db.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (uid, now,
                        enclib.pass_to_key(master_key, uid), enclib.enc_from_key(secret, u_pass),
                        enclib.pass_to_key(u_pass, uid), ipk+"🱫"+expiry_time, None,
                        None, None, username, now, 99, 0, 0))
        self.db.commit()
        # todo move to database
        #with open(f"users/{uid}/transactions.csv", "w", newline='', encoding="utf-8") as csv:
        #    writer(csv).writerows([["Date", "Type", "Amount", "Spent", "Description", "Hash"],
        #                          [str(datetime.now())[:-7], "NACD", "350", "0", "New account 350 D bonus",
        #                           enclib.pass_to_key(f"{str(datetime.now())[:-7]}NACD3500New account"
        #                                              f" 350 D bonus", uid)]])

    def check_logged_in(self, uid, ip):
        if uid in self.logged_in_users:
            return True
        elif ip in self.logged_in_users:
            return True
        else:
            return False


def add_action(uid, t_type, amount, spent, desc):
    pass
    # todo move to database
    #with open(f"users/{uid}/transactions.csv", "r", encoding="utf-8") as csv:
    #    prev_hash = list(reader(csv))[-1][5]
    #with open(f"users/{uid}/transactions.csv", "a", newline='', encoding="utf-8") as csv:
    #    writer(csv).writerow([str(datetime.now())[:-7], t_type, amount, spent, desc, enclib.pass_to_key(
    #        f"{str(datetime.now())[:-7]}{t_type}{amount}{spent}{desc}", prev_hash)])


users = Users()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 30678))
s.listen()
print(f"[*] Listening as {str(s).split('laddr=')[1][:-1]}")


def client_connection(cs):
    try:
        ip, port = str(cs).split("raddr=")[1][2:-2].split("', ")
        connection_type = str(cs.recv(32))[2:-1]
        print(f"NEW CLIENT --- Type-{connection_type} IP-{ip}:{port}")
        uid = None
        if connection_type == "CLI":
            try:
                pub_key_cli = rsa.PublicKey.load_pkcs1(cs.recv(256))
            except ValueError:
                raise InvalidClientData
            enc_seed = enclib.rand_b96_str(36)
            cs.send(rsa.encrypt(enc_seed.encode(), pub_key_cli))
            enc_key = enclib.pass_to_key(enc_seed[:18], enc_seed[18:], 100000)

            def send_e(text):  # encrypt and send to client
                try:
                    cs.send(enclib.enc_from_key(text, enc_key))
                except zlib.error:
                    raise ConnectionResetError

            def recv_d(buf_lim=1024):  # decrypt data from client
                try:
                    return enclib.dec_from_key(cs.recv(buf_lim), enc_key)
                except zlib.error:
                    raise ConnectionResetError
        else:
            def send_e(text):
                cs.send(text.encode())

            def recv_d(buf_lim=1024):
                return cs.recv(buf_lim).decode()

            # todo temp kick other client types
            raise InvalidClientData

        while True:  # login loop
            login_request = recv_d()
            print(login_request)  # temp debug for dev

            if login_request == "CAP":  # captcha request
                img = ImageCaptcha(width=280, height=90)
                captcha_text = "".join(random.choices("23456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=int(10)))
                print(captcha_text)
                img.generate(captcha_text)  # todo remove the need for a file
                img.write(captcha_text, 'captcha.jpg')
                with open("captcha.jpg", "rb") as f:
                    send_e(f.read())
                counter = 0
                while True:
                    counter += 1
                    captcha_attempt = recv_d()
                    if captcha_attempt != captcha_text:
                        send_e("N")
                        if counter > 3:
                            time.sleep(10)  # rate limit
                    else:
                        send_e("V")
                        break

                log_or_create = recv_d()
                if log_or_create.startswith("NAC:"):  # new account
                    master_key, u_pass = log_or_create[4:].split("🱫")
                    while True:  # create random unique user id
                        uid = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=8))
                        u_name = uid+"#"+str(random.randint(111, 999))
                        if users.db.execute("SELECT user_id FROM users WHERE user_id = ?", (uid,)).fetchone() is None:
                            break
                    u_secret = "".join(random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXY"
                                                      "abcdefghijklmnopqrstuvwxyz", k=8))
                    send_e(f"{uid}🱫{u_secret}")
                    while True:  # 2fa challenge
                        code_challenge = recv_d()
                        if requests.get(f"https://www.authenticatorapi.com/Validate.aspx?"
                                        f"Pin={code_challenge}&SecretCode={u_secret}").content != b"True":
                            send_e("N")
                        else:
                            ipk = enclib.rand_b96_str(24)
                            send_e(enclib.enc_from_pass(ipk, u_pass[:40], u_pass[40:]))
                            send_e(f"{u_name}🱫0🱫0🱫0")
                            users.add_user(uid, master_key, u_secret, u_pass,
                                           enclib.pass_to_key(ip+ipk, uid), u_name)
                            break

                if log_or_create.startswith("LOG:"):  # login
                    print(log_or_create)
                    master_key_c, search_for, uname_or_uid = log_or_create[4:].split("🱫")
                    if search_for == "u":
                        try:
                            uid, master_key, u_secret, u_pass, u_name, level, r_coin, d_coin = users.db.execute(
                                "SELECT user_id, master_key, secret, user_pass, username, level, r_coin, d_coin "
                                "FROM users WHERE username = ?", (uname_or_uid,)).fetchone()
                        except TypeError:
                            uid = None
                            send_e("NU")  # user does not exist
                    else:
                        try:
                            uid = uname_or_uid
                            master_key, u_secret, u_pass, u_name, level, r_coin, d_coin = users.db.execute(
                                "SELECT master_key, secret, user_pass, username, level, r_coin, d_coin "
                                "FROM users WHERE user_id = ?", (uname_or_uid,)).fetchone()
                        except TypeError:
                            uid = None
                            send_e("NU")  # user does not exist
                    if uid:
                        if enclib.pass_to_key(master_key_c, uid) != master_key:
                            send_e("IMK")  # master key wrong
                        else:
                            send_e("V")
                            if search_for == "u":
                                send_e(uid)
                            while True:
                                u_pass_c = recv_d()
                                if enclib.pass_to_key(u_pass_c, uid) == u_pass:
                                    ipk = enclib.rand_b96_str(24)
                                    send_e(enclib.enc_from_pass(ipk, u_pass_c[:40], u_pass_c[40:]))
                                    break
                                else:
                                    send_e("N")
                            u_secret = enclib.dec_from_key(u_secret, u_pass_c)
                            while True:  # 2fa challenge
                                code_challenge = recv_d()
                                if requests.get(f"https://www.authenticatorapi.com/Validate.aspx?"
                                                f"Pin={code_challenge}&SecretCode={u_secret}").content != b"True":
                                    send_e("N")
                                else:
                                    break
                            send_e(f"{u_name}🱫{level}🱫{r_coin}🱫{d_coin}")
                            ipk1, ipk2, ipk3, ipk4 = users.db.execute(
                                "SELECT ipk1, ipk2, ipk3, ipk4 FROM users WHERE user_id = ?",
                                (uid,)).fetchone()  # get ip keys from db

                            expiry_time = str(datetime.now() + timedelta(days=14))[:-7]
                            if ipk1 and ipk2 and ipk3 and ipk4:  # if 4 ip keys, replace the oldest one
                                oldest_ipk = "1"
                                oldest_ipk_d = datetime.strptime(ipk1.split("🱫")[1], "%Y-%m-%d %H:%M:%S")
                                if oldest_ipk_d > datetime.strptime(ipk2.split("🱫")[1], "%Y-%m-%d %H:%M:%S"):
                                    oldest_ipk_d = datetime.strptime(ipk2.split("🱫")[1], "%Y-%m-%d %H:%M:%S")
                                    oldest_ipk = "2"
                                if oldest_ipk_d > datetime.strptime(ipk3.split("🱫")[1], "%Y-%m-%d %H:%M:%S"):
                                    oldest_ipk_d = datetime.strptime(ipk3.split("🱫")[1], "%Y-%m-%d %H:%M:%S")
                                    oldest_ipk = "3"
                                if oldest_ipk_d > datetime.strptime(ipk4.split("🱫")[1], "%Y-%m-%d %H:%M:%S"):
                                    oldest_ipk = "4"
                                users.db.execute("UPDATE users SET ipk" + oldest_ipk + " = ? WHERE user_id = ?",
                                                 (enclib.pass_to_key(ip+ipk, uid)+"🱫"+expiry_time, uid))
                            elif not ipk1:  # save to empty ip key
                                users.db.execute("UPDATE users SET ipk1 = ? WHERE user_id = ?",
                                                 (enclib.pass_to_key(ip+ipk, uid)+"🱫"+expiry_time, uid))
                            elif not ipk2:
                                users.db.execute("UPDATE users SET ipk2 = ? WHERE user_id = ?",
                                                 (enclib.pass_to_key(ip+ipk, uid)+"🱫"+expiry_time, uid))
                            elif not ipk3:
                                users.db.execute("UPDATE users SET ipk3 = ? WHERE user_id = ?",
                                                 (enclib.pass_to_key(ip+ipk, uid)+"🱫"+expiry_time, uid))
                            elif not ipk4:
                                users.db.execute("UPDATE users SET ipk4 = ? WHERE user_id = ?",
                                                 (enclib.pass_to_key(ip+ipk, uid)+"🱫"+expiry_time, uid))
                            users.db.commit()
                            break

            elif login_request.startswith("ULK:"):  # unlock account
                uid, u_ipk = login_request[4:].split("🱫")
                print(uid, u_ipk)
                if users.check_logged_in(uid, ip):
                    send_e("SESH_T")
                else:
                    try:
                        ipk1, ipk2, ipk3, ipk4, u_name, level, r_coin, d_coin = \
                            users.db.execute("SELECT ipk1, ipk2, ipk3, ipk4, username, level, r_coin, "
                                             "d_coin FROM users WHERE user_id = ?", (uid,)).fetchone()
                    except ValueError:
                        send_e("N")  # User ID not found
                    else:
                        u_ipk = enclib.pass_to_key(ip+u_ipk, uid)

                        def check_ipk(ipk):
                            ipk, ipk_e = ipk.split("🱫")
                            if u_ipk != ipk:
                                return False
                            elif datetime.now() < datetime.strptime(ipk_e, "%Y-%m-%d %H:%M:%S"):
                                return True
                            else:
                                return False

                        if ipk1:
                            if check_ipk(ipk1):
                                send_e(f"{u_name}🱫{level}🱫{r_coin}🱫{d_coin}")
                                break
                        if ipk2:
                            if check_ipk(ipk2):
                                send_e(f"{u_name}🱫{level}🱫{r_coin}🱫{d_coin}")
                                break
                        if ipk3:
                            if check_ipk(ipk3):
                                send_e(f"{u_name}🱫{level}🱫{r_coin}🱫{d_coin}")
                                break
                        if ipk4:
                            if check_ipk(ipk4):
                                send_e(f"{u_name}🱫{level}🱫{r_coin}🱫{d_coin}")
                                break
                        send_e("N")

            else:
                raise InvalidClientData

        users.login(uid, ip, enc_key)
        print(f"{uid} logged in with IP-{ip}:{port}")
        while True:  # main loop
            request = recv_d()
            print(request)  # temp debug for dev

            if request.startswith("LOG_A"):  # deletes all IP keys
                raise ConnectionResetError

            #elif request.startswith("DLAC:"):  # todo delete account
            #    pass

            elif request.startswith("CUP:"):  # change user password
                u_pass_c = request[4:]
                try:
                    u_pass, u_secret = users.db.execute("SELECT user_pass, secret FROM users WHERE user_id = ?",
                                                        (uid,)).fetchone()
                    if enclib.pass_to_key(u_pass_c, uid) != u_pass:
                        send_e("N")
                    else:
                        send_e("V")
                        n_u_pass = recv_d()
                        u_secret = enclib.dec_from_key(u_secret, u_pass_c)
                        while True:  # 2fa challenge
                            code_challenge = recv_d()
                            if requests.get(f"https://www.authenticatorapi.com/Validate.aspx?"
                                            f"Pin={code_challenge}&SecretCode={u_secret}").content != b"True":
                                send_e("N")
                            else:
                                break
                        n_ipk = enclib.rand_b96_str(24)
                        expiry_time = str(datetime.now()+timedelta(days=14))[:-7]
                        users.db.execute("UPDATE users SET secret = ?, user_pass = ?, ipk1 = ?, ipk2 = ?, ipk3 = ?, "
                                         "ipk4 = ? WHERE user_id = ?", (enclib.enc_from_key(u_secret, n_u_pass),
                                                                        enclib.pass_to_key(n_u_pass, uid),
                                                                        enclib.pass_to_key(ip+n_ipk, uid)+"🱫"+expiry_time,
                                                                        None, None, None, uid))
                        users.db.commit()
                        send_e(enclib.enc_from_pass(n_ipk, n_u_pass[:40], n_u_pass[40:]))
                except sqlite3.OperationalError:
                    send_e("N")

            # todo fix code
            elif request.startswith("CUN:"):  # change username
                if d_coin < 5:
                    raise InvalidClientData
                else:
                    n_u_name = request[4:]
                    if not 4 < len(n_u_name) < 25:
                        raise InvalidClientData
                    if "#" in n_u_name or "  " in n_u_name:
                        raise InvalidClientData
                    counter = 0
                    while True:
                        counter += 1
                        n_u_name_i = n_u_name+"#"+str(random.randint(111, 999))
                        try:
                            if users.db.execute("SELECT * FROM users WHERE username = ?",
                                                (n_u_name_i,)).fetchone() is None:
                                d_coin = round(d_coin-5, 2)
                                users.db.execute("UPDATE users SET username = ?, d_coin = ? WHERE user_id = ?",
                                                 (n_u_name_i, d_coin, uid))
                                users.db.commit()
                                add_action(uid, "CUN", 0, 5, f"Changed u_name to {n_u_name_i}")
                                send_e(n_u_name_i)
                                u_name = n_u_name_i
                                break
                        except sqlite3.OperationalError:
                            if counter == 10:
                                send_e("N")
                                break

            # todo conversation with server
            elif request.startswith("CON"):  # join public chat
                print(request)
                send_e("SERVER🱫V")
                time.sleep(0.1)
                send_e("CLIENT2🱫Y")
                time.sleep(3)
                send_e("SERVER🱫completed task")

    except ConnectionResetError:  # client disconnection exception handler
        print(f"{uid}-{ip}:{port} DC")
        if ip in users.logged_in_users:
            users.logout(uid, ip)
    except InvalidClientData:  # invalid client data exception handler
        print(f"{uid}-{ip}:{port} DC - modified/invalid client request")
        if ip in users.logged_in_users:
            users.logout(uid, ip)

        # todo move to database
        #with open(f"users/{uid}/log.txt", "a") as log:  # log logout time
        #    if request:
        #        log.write(f"{str(datetime.now())[:-7]} - ICR: {request}\n")
        #    else:
        #        log.write(f"{str(datetime.now())[:-7]} - ICR: None\n")


while True:  # connection accept loop
    client_socket, client_address = s.accept()
    t = threading.Thread(target=client_connection, args=(client_socket,), daemon=True).start()