import rsa
import enclib
import socket
import os

# todo abstract out of bread_client to here
# todo merge example_headless into here and make it a good example


if not os.path.exists("app"):
    os.mkdir("app")

default_salt = "52gy\"J$&)6%0}fgYfm/%ino}PbJk$w<5~j'|+R .bJcSZ.H&3z'A:gip/jtW$6A=G-;|&&rR81!BTElChN|+\"T"


# server class containing connection algorithm and data transfer functions
class Server:
    def __init__(self):
        self.s, self.enc_key = socket.socket(), None
        if os.path.exists("app/server_ip"):
            with open(f"app/server_ip", "rb") as f:
                self.ip = f.read().decode().split(":")
        else:
            self.ip = None

    def connect(self):
        try:
            self.s.connect((self.ip[0], int(self.ip[1])))
            print("Connected to server")
            l_ip, l_port = str(self.s).split("laddr=")[1].split("raddr=")[0][2:-3].split("', ")
            s_ip, s_port = str(self.s).split("raddr=")[1][2:-2].split("', ")
            print(f" << Server connected via {l_ip}:{l_port} -> {s_ip}:{s_port}")
            self.s.send(b"CLI")
            pub_key, pri_key = rsa.newkeys(512)
            try:
                self.s.send(rsa.PublicKey.save_pkcs1(pub_key))
            except ConnectionResetError:
                return False
            print(" >> Public RSA key sent")
            enc_seed = rsa.decrypt(self.s.recv(128), pri_key).decode()
            self.enc_key = enclib.pass_to_key(enc_seed[:18], enc_seed[18:], 100000)
            print(" << Client enc_seed and enc_salt received and loaded\n -- RSA Enc bootstrap complete")
            return True
        except ConnectionRefusedError:
            print("Connection refused")
            return False
        except socket.gaierror:
            print("Invalid IP")
            return False

    def send_e(self, text):  # encrypt and send data to server
        try:
            self.s.send(enclib.enc_from_key(text, self.enc_key))
        except ConnectionResetError:
            print("CONNECTION_LOST, reconnecting...")
            if self.ip and self.connect():
                self.s.send(enclib.enc_from_key(text, self.enc_key))
            else:
                print("Failed to reconnect")

    def recv_d(self, buf_lim=1024):  # receive and decrypt data to server
        try:
            return enclib.dec_from_key(self.s.recv(buf_lim), self.enc_key)
        except ConnectionResetError:
            print("CONNECTION_LOST, reconnecting...")
            if self.ip and self.connect():
                return enclib.dec_from_key(self.s.recv(buf_lim), self.enc_key)
            else:
                print("Failed to reconnect")
