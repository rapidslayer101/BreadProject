import tickers_and_cache as tnc

# This file is for testing the ticker data and cache functions

while True:
    c_list = ["Tesla"]
    t_objects, t_results = tnc.TNS(c_list).get_objects_and_results()
    if not t_objects:
        print("Ticker not found: TNS failed to resolve ticker")
    else:
        break

for t in t_objects:
    print(t_objects[t].shares_full())
#print(t_results)
