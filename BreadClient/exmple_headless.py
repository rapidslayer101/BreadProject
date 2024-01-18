import authlib
import enclib

# todo make this connection method valid and usable

# Create a client object
s = enclib.ClientSocket()
uname, level, r_coin, d_coin = authlib.connect_system(s)
print(uname, level, r_coin, d_coin)
s.send_e("CON")
print(s.recv_d())  # returns server response "SERVER🱫V"


