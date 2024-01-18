import authlib
import enclib

# Create a client object
s = enclib.ClientSocket()

# Connect to the server and get account info
uname, level, r_coin, d_coin = authlib.connect_system(s)

# Example of sending a request to the server
s.send_e("CON")

# Example of receiving a response from the server
print(s.recv_d())  # returns server response "SERVER🱫V"


