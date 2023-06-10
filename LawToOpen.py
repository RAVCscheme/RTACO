import jsonpickle
import socket
import argparse
from web3 import Web3
import os
import pickle
import json 

# python3 LawToOpen.py --title "Loan Credential" --rpc-endpoint "http://127.0.0.1:7545"


parser = argparse.ArgumentParser(description="Anonymous Credential Law to Opening")
parser.add_argument("--title", type=str, default = None, required = True, help= "This is the title of the Anonymous Credential.")
parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a opener is connected to blockchain network.")
args = parser.parse_args()

root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

def getTotalOpeners(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "no.pickle")
	f = open(ac_file_path,'rb')
	no = pickle.load(f)
	f.close()
	return no

def getOpenerIpPort(title):
	ac_path = os.path.join(root_dir, title)
	opener_ip_map = os.path.join(ac_path, "opener_ip_map.pickle")
	f = open(opener_ip_map,'rb')
	opener_ip_map_list = pickle.load(f)
	f.close()
	return opener_ip_map_list

def getParamsAddress():
	file_path = os.path.join(root_dir, "params_address.pickle")
	f = open(file_path,'rb')
	params_address = pickle.load(f)
	f.close()
	return params_address

params_address = getParamsAddress()
# w3 = Web3(Web3.WebsocketProvider(args.rpc_endpoint, websocket_timeout=100))
w3 = Web3(Web3.HTTPProvider(args.rpc_endpoint, request_kwargs = {'timeout' : 300}))

# ------------------------------------------------------------------------
# Params.sol
# All the TTP system parameters and Aggregated Validators Key

tf = json.load(open('./build/contracts/Params.json'))
params_address = Web3.toChecksumAddress(params_address)
params_contract = w3.eth.contract(address = params_address, abi = tf['abi'])

# ------------------------------------------------------------------------

credential_id = params_contract.functions.getMapCredentials(args.title).call()
assert credential_id != 0, "No such AC."

no = getTotalOpeners(args.title)
opener_ip_map_list = getOpenerIpPort(args.title)



ac_file_path = os.path.join(root_dir, "served_service_requests.pickle")
f = open(ac_file_path,'rb')
service_dict = pickle.load(f)
f.close()

print("Select a session to open : ")
for session in service_dict.keys():
	print(session)

session = int(input("Enter session id : "))

open_sigma = service_dict[session][credential_id][0]
print(open_sigma)
# count = 0
for opener_ip_port in opener_ip_map_list:
	# if count == 0:
	# 	count += 1
	# 	continue
	ip, port = opener_ip_port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, int(port)))
	sigmaJSON = jsonpickle.encode(open_sigma)
	s.send(sigmaJSON.encode())
	s.close()
	# count += 1