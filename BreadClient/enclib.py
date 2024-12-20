import datetime
import hashlib
import multiprocessing
import os
import random
import socket
import sys
import time

import rsa

# enc 13.0.0 - CREATED BY RAPIDSLAYER101 (Scott Bree)
default_salt = "52gy\"J$&)6%0}fgYfm/%ino}PbJk$w<5~j'|+R .bJcSZ.H&3z'A:gip/jtW$6A=G-;|&&rR81!BTElChN|+\"T"
_cpu_count_ = multiprocessing.cpu_count()  # the chunking size
_xor_salt_len_ = 7  # 94^8 combinations
_default_pass_depth_ = 100000  # the hash loop depth
_b94set_ = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/`!\"$%^&*() -=[{]};:'@#~\\|,<.>?"
_b96set_ = _b94set_+"¬£"


# generate a random base 96 string of a given length
def rand_b96_str(num, alpha_set=_b96set_):
    return "".join(random.choices(alpha_set, k=int(num)))


# convert a string to another base
def to_base(base_fr: int, base_to: int, hex_to_convert, alpha_set=_b96set_):
    if not all([digit in alpha_set[:base_fr] for digit in str(hex_to_convert)]):
        return f"Input contains characters not in the base: {alpha_set[:base_fr]} "
    if 2 > base_to or base_to > len(alpha_set):
        return f"Base out of range 2-{len(alpha_set)}"
    else:
        decimal, power = 0, len(str(hex_to_convert))-1
        for digit in str(hex_to_convert):
            decimal += alpha_set.index(digit)*base_fr**power
            power -= 1
        hexadecimal = ""
        while decimal > 0:
            hexadecimal, decimal = alpha_set[decimal % base_to]+hexadecimal, decimal//base_to
        return hexadecimal


# attempts to find the base of an input string
def get_base(data_to_resolve: str):
    for i in range(96):
        if to_base(i+2, i+2, data_to_resolve) == data_to_resolve:
            return i+2


# turns a password and salt into a key
# used to save a key so encryption/decryption does not require the generation of a key each time
# can also be used as a string hider to hide data other than a password
def pass_to_key(password: str, salt: str, depth=100000):
    password, salt = password.encode(), salt.encode()
    for i in range(depth):
        password = hashlib.sha512(password+salt).digest()
    return to_base(16, 96, password.hex())


# generates a key of equal length to the data then xor the data with the key
def _xor_(data, key, xor_salt):
    key_value, key = [], key.encode()
    for i in range((len(data)//64)+1):
        key = hashlib.sha512(key+xor_salt).digest()
        key_value.append(key)
    key = b"".join(key_value)[:len(data)]
    return (int.from_bytes(data, sys.byteorder) ^ int.from_bytes(key, sys.byteorder)).to_bytes(len(data), sys.byteorder)


def _encrypter_(text, key, threading=False, file_output=False):
    if not isinstance(text, bytes):
        text = text.encode()
    xor_salt = "".join(random.choices(_b94set_, k=_xor_salt_len_)).encode()
    if not threading:
        return xor_salt+_xor_(text, key, xor_salt)
    else:
        text_len = len(text)
        block_size = (text_len+100) // _cpu_count_
        if text_len//block_size > (50000000//_cpu_count_) and not file_output:
            return xor_salt+_xor_(text, key, xor_salt)
        else:
            pool, result_objects = _block_encrypter_(text, key, block_size, xor_salt)
            if file_output:
                with open(file_output, "wb") as f:
                    for loop, result in enumerate(result_objects):
                        if loop == 0:
                            data = xor_salt+result.get()
                            f.write(data)
                        else:
                            f.write(result.get())
                pool.join()
            else:
                d_data = b""
                for result in result_objects:
                    d_data += result.get()
                d_data = xor_salt + d_data
                pool.join()
                return d_data


def _decrypter_(text, key, decode=True, threading=False, file_output=False):
    text_len = len(text)
    xor_salt, text = text[:_xor_salt_len_], text[_xor_salt_len_:]
    if not threading:
        block = _xor_(text, key, xor_salt)
        if decode:
            try:
                return block.decode()
            except UnicodeDecodeError:
                return block
        else:
            return block
    else:
        block_size = (text_len+93) // _cpu_count_
        if text_len//block_size > (50000000//_cpu_count_) and not file_output:
            block = _xor_(text, key, xor_salt)
            if decode:
                try:
                    return block.decode()
                except UnicodeDecodeError:
                    return block
            else:
                return block
        else:
            pool, result_objects = _block_encrypter_(text, key, block_size, xor_salt)
            if file_output:
                d_data = [x.get() for x in result_objects]
                if isinstance(d_data[0], bytes):
                    with open(f"{file_output}", "wb") as f:
                        for block in d_data:
                            f.write(block)
                if isinstance(d_data[0], str):
                    with open(f"{file_output}", "w", encoding="utf-8") as f:
                        for block in d_data:
                            f.write(block.replace("\r", ""))
                pool.join()
            else:
                d_data = b""
                for result in result_objects:
                    d_data += result.get()
                if decode:
                    try:
                        d_data = d_data.decode()
                    except UnicodeDecodeError:
                        pass
                pool.join()
                return d_data


def _block_encrypter_(text, key, block_size, xor_salt):
    text = [text[i:i + block_size] for i in range(0, len(text), block_size)]
    key1, alpha_gen, counter, keys_salt = int(to_base(96, 16, key), 36), _b94set_, 0, ""
    while len(alpha_gen) > 0:
        counter += 2
        value = int(str(key1)[counter:counter + 2]) << 1
        while value > len(alpha_gen) - 1:
            value = value // 2
        if len(str(key1)[counter:]) < 2:
            keys_salt += alpha_gen
            alpha_gen = alpha_gen.replace(alpha_gen, "")
        else:
            chosen = alpha_gen[value]
            keys_salt += chosen
            alpha_gen = alpha_gen.replace(chosen, "")
    block_keys = []
    for i in range(len(text)):
        key = pass_to_key(key, keys_salt, 1)
        block_keys.append(key)
    print(f"Launching {len(text)} threads")
    pool = multiprocessing.Pool(_cpu_count_)
    result_objects = [pool.apply_async(_xor_, args=(text[x], block_keys[x], xor_salt)) for x in range(0, len(text))]
    pool.close()
    return pool, result_objects


# returns the file size of a file in standard units
def get_file_size(file):
    size, power, n = [os.path.getsize(file), 2 ** 10, 0]
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)}{power_labels[n]}"


# a wrapper for the encrypter function to support file encryption and decryption
def _file_encrypter_(enc, file, key, file_output):
    start = time.perf_counter()
    if os.path.exists(file):
        file_name = file.split("/")[-1].split(".")[:-1]  # file_type = file.split("/")[-1].split(".")[-1:]
        print(f"{file_name} is {get_file_size(file)}, should take {round(os.path.getsize(file)/136731168.599, 2)}s")
        with open(file, 'rb') as hash_file:
            data = hash_file.read()
        if enc:
            _encrypter_(data, key, True,  file_output)
        else:
            _decrypter_(data, key, True, True, file_output)
        print(f"ENC/DEC COMPLETE OF {get_file_size(file)} IN {round(time.perf_counter()-start, 2)}s")
    else:
        return "File not found"


# a selection of wrappers for the encrypter function for encryption and decryption

# encrypts data
def enc_from_pass(text, password, salt, depth=_default_pass_depth_, threading=False):
    return _encrypter_(text, pass_to_key(password, salt, depth), threading)


# uses a pre-generated key to encrypt data
def enc_from_key(text, key, threading=False):
    return _encrypter_(text, key, threading)


# decrypts data
def dec_from_pass(e_text, password, salt, depth=_default_pass_depth_, decode=True, threading=False):
    return _decrypter_(e_text, pass_to_key(password, salt, depth), decode, threading)


# uses a pre-generated key to decrypt data
def dec_from_key(e_text, key, decode=True, threading=False):
    return _decrypter_(e_text, key, decode, threading)


# encrypts a file  # todo improve file encryption
def enc_file_from_pass(file, password, salt, file_output, depth=_default_pass_depth_):
    return _file_encrypter_(True, file, pass_to_key(password, salt, depth), file_output)


# decrypts a file  # todo improve file encryption
def dec_file_from_pass(e_file, password, salt, file_output, depth=_default_pass_depth_):
    return _file_encrypter_(False, e_file, pass_to_key(password, salt, depth), file_output)


def generate_master_key(master_key, salt, depth_time, current_depth=0, self=None):
    time.sleep(0.2)
    start, time_left, loop_timer = time.perf_counter(), depth_time, time.perf_counter()
    while time_left > 0:
        current_depth += 1
        master_key = hashlib.sha512(master_key+salt).digest()
        if time.perf_counter()-loop_timer > 0.25:
            try:
                time_left -= (time.perf_counter()-loop_timer)
                loop_timer = time.perf_counter()
                real_dps = int(round(current_depth/(time.perf_counter()-start), 0))
                print(f"Runtime: {round(time.perf_counter()-start, 2)}s  "
                      f"Time Left: {round(time_left, 2)}s  "
                      f"DPS: {round(real_dps/1000000, 3)}M  "
                      f"Depth: {current_depth}/{round(real_dps*time_left, 2)}  "
                      f"Progress: {round((depth_time-time_left)/depth_time*100, 3)}%")
                if self:
                    self.pin_code_text = f"Generating Key and Pin ({round(time_left, 2)}s left)"
            except ZeroDivisionError:
                pass
    mkey = to_base(16, 96, master_key.hex())
    pin_code = to_base(10, 36, current_depth)
    if self:
        self.rand_confirmation = str(random.randint(0, 9))
        self.pin_code_text = f"Account Pin: {pin_code}"
        self.rand_confirm_text = f"Enter {self.rand_confirmation} below.\n" \
                                 f"By proceeding with account creation you agree to our Terms and Conditions."
    return mkey, pin_code


def regenerate_master_key(master_key, salt, depth_to, current_depth=0, self=None):
    start, depth_left, loop_timer = time.perf_counter(), depth_to-current_depth, time.perf_counter()
    for depth_count in range(1, depth_left+1):
        master_key = hashlib.sha512(master_key+salt).digest()
        if time.perf_counter()-loop_timer > 0.25:
            try:
                loop_timer = time.perf_counter()
                real_dps = int(round(depth_count/(time.perf_counter()-start), 0))
                print(f"Runtime: {round(time.perf_counter()-start, 2)}s  "
                      f"Time Left: {round((depth_left-depth_count)/real_dps, 2)}s  "
                      f"DPS: {round(real_dps/1000000, 3)}M  "
                      f"Depth: {current_depth+depth_count}/{depth_to}  "
                      f"Progress: {round((current_depth+depth_count)/depth_to*100, 3)}%")
                if self:
                    self.gen_left_text = f"Generating master key " \
                                         f"({round((depth_left-depth_count)/real_dps, 2)}s left)"
            except ZeroDivisionError:
                pass
    return to_base(16, 96, master_key.hex())


# rounds dt to an amount of seconds
# this function can be used to create a time based key system
def round_time(dt=None, round_to=30):
    if not dt:
        dt = datetime.datetime.now()
    seconds = (dt.replace(tzinfo=None)-dt.min).seconds
    return dt+datetime.timedelta(0, (seconds+round_to/2)//round_to*round_to-seconds, -dt.microsecond)


# hashes a file using the SHA512 algorithm
def hash_a_file(file):
    hash_ = hashlib.sha512()
    with open(file, 'rb') as hash_file:
        buf = hash_file.read(262144)
        while len(buf) > 0:
            hash_.update(buf)
            buf = hash_file.read(262144)
    return to_base(16, 96, hash_.hexdigest())


# todo add timeout to this function
def drive_insert_detector(time_out=None):
    dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    before_drives = [f"{d}:\\" for d in dl if os.path.exists(f"{d}:\\")]
    while True:  # check all possible new drives
        now_drives = [f"{d}:\\" for d in dl if os.path.exists(f"{d}:\\")]
        if before_drives != now_drives:
            try:
                return [d for d in now_drives if d not in before_drives][0]
            except IndexError:
                before_drives = [f"{d}:\\" for d in dl if os.path.exists(f"{d}:\\")]
        time.sleep(0.1)


# server class containing connection algorithm and data transfer functions
class ClientSocket:
    def __init__(self):
        self.s, self.enc_key = socket.socket(), None
        if os.path.exists("app/server_ip"):
            with open(f"app/server_ip", "rb") as f:
                self.ip = f.read().decode().split(":")
        else:
            self.ip = None

    def connect(self, connection_type=b"HDL"):
        try:
            self.s.connect((self.ip[0], int(self.ip[1])))
            print("Connected to server")
            l_ip, l_port = str(self.s).split("laddr=")[1].split("raddr=")[0][2:-3].split("', ")
            s_ip, s_port = str(self.s).split("raddr=")[1][2:-2].split("', ")
            print(f" << Server connected via {l_ip}:{l_port} -> {s_ip}:{s_port}")
            self.s.send(connection_type)
            pub_key, pri_key = rsa.newkeys(512)
            try:
                self.s.send(rsa.PublicKey.save_pkcs1(pub_key))
            except ConnectionResetError:
                return False
            print(" >> Public RSA key sent")
            enc_seed = rsa.decrypt(self.s.recv(128), pri_key).decode()
            self.enc_key = pass_to_key(enc_seed[:18], enc_seed[18:], 100000)
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
            self.s.send(enc_from_key(text, self.enc_key))
        except ConnectionResetError:
            print("CONNECTION_LOST, reconnecting...")
            if self.ip and self.connect():
                self.s.send(enc_from_key(text, self.enc_key))
            else:
                print("Failed to reconnect")

    def recv_d(self, buf_lim=1024, decode=True, threading=False):  # receive and decrypt data to server
        try:
            return dec_from_key(self.s.recv(buf_lim), self.enc_key, decode, threading)
        except ConnectionResetError:
            print("CONNECTION_LOST, reconnecting...")
            if self.ip and self.connect():
                return dec_from_key(self.s.recv(buf_lim), self.enc_key)
            else:
                print("Failed to reconnect")

    def recv_file(self, buffer=65356):
        file_data = self.recv_d()
        if file_data == "N":
            return False
        else:
            file_name, file_size = file_data.split("🱫")
            file_size = int(file_size)
            print(f"Downloading file {file_name} ({file_size})...")
            all_bytes = b""
            start = time.perf_counter()
            for i in range(file_size//buffer):
                bytes_read = self.recv_d(buffer, False)
                if time.perf_counter() - start > 0.25:
                    start = time.perf_counter()
                    print(f"Downloading {file_name[:-4]} ({round((len(all_bytes) / file_size) * 100, 2)}%)")
                all_bytes += bytes_read
            all_bytes += self.recv_d((file_size % (buffer-7))+7, False)
            with open(f"{file_name}", "wb") as f:
                f.write(all_bytes)
            if hash_a_file(file_name) == self.recv_d():
                print(f"Downloaded {file_name} ({get_file_size(file_name)})")
                self.send_e("V")
                return True
            else:
                print("File hash does not match server. Download failed")
                self.send_e("N")
                self.recv_file(32678)

