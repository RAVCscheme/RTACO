from re import A
import jsonpickle
from TTP import *
from py_ecc_tester import *

from datetime import datetime
import time

import argparse
import os
import pickle
import socket
import threading
import json
from web3 import Web3
#No address to change
# python3 ProtocolInitiator_UpdateCAInformation.py --titles "Identity Certificate" "Income Certificate" --address 0xE279a5e0DEb02eDe68876bea8206EeFb2Ab0E96C --rpc-endpoint "http://127.0.0.1:7545"

parser = argparse.ArgumentParser(description="Update Attribute Certifiers information to smart contracts")
parser.add_argument('--titles', nargs='+', help='The attribute certifiers in the system', required=True)
parser.add_argument("--address", type=str, default = None, required = True,  help= "The blockchain address on which Protocol Initiator is running")
parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a client is connected to blockchain network")
args = parser.parse_args()

mode = 0o777
root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

try:
	os.mkdir(root_dir, mode = mode)
except FileExistsError as e:
	pass 

def downloadCAParams(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "params.pickle")
	f = open(ca_file_path,'rb')
	json_params = pickle.load(f)
	params = jsonpickle.decode(json_params)
	f.close()
	return params

def downloadCAPk(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "pk.pickle")
	f = open(ca_file_path,'rb')
	json_pk = pickle.load(f)
	pk = jsonpickle.decode(json_pk)
	f.close()
	return pk

def getParamsAddress():
	file_path = os.path.join(root_dir, "params_address.pickle")
	f = open(file_path,'rb')
	params_address = pickle.load(f)
	f.close()
	return params_address

params_address = getParamsAddress()

for title in args.titles:
	_, _, _, hs = downloadCAParams(title)
	pk = downloadCAPk(title)
	encoded_hs = [(x[0].n, x[1].n) for x in hs]
	encoded_pk = (pk[0].n, pk[1].n)
		
	# w3 = Web3(Web3.WebsocketProvider(args.rpc_endpoint, websocket_timeout = 100))
	w3 = Web3(Web3.HTTPProvider(args.rpc_endpoint))
		
	tf = json.load(open('./build/contracts/Params.json'))
	params_address = Web3.toChecksumAddress(params_address)
	params_contract = w3.eth.contract(address = params_address, abi = tf['abi'])
		
	tx_hash = params_contract.functions.set_ttp_params(title, encoded_pk, encoded_hs).transact({'from': args.address})
	w3.eth.waitForTransactionReceipt(tx_hash)