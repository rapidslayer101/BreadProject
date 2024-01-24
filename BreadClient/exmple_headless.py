import authlib
import enclib

# Create a client object
s = enclib.ClientSocket()

# Connect to the server and get account info
uname, level, r_coin, d_coin = authlib.connect_system(s)

while True:
    request = input(f"<{uname}>: ")
    # if request not just blank spaces
    if request.strip():
        s.send_e(request)  # typing "GET:IlluminationSDK" will download the file

        if request == "CON":  # Example of receiving a response from the server
            print(s.recv_d())  # returns server response "SERVER🱫V"
            print(s.recv_d())  # returns server response "CLIENT2🱫Y"
            print(s.recv_d())  # returns server response "SERVER🱫completed task"

        if request.startswith("GET:"):  # get a file from the server  # todo admin request of files
            if not s.recv_file(s.recv_d()):
                print("Insufficient permissions to download this file or file does not exist")

        else:
            response = s.recv_d()
            if response != "INV_REQ":
                print(response)
            else:
                print("Invalid request - using these may get you kicked")


# Commands accessible to this interface:
# LOGOUT_ALL - deletes all user keys, data and logs out everywhere
# LOGOUT - deletes current user key, data and logs out
# CON - test command
