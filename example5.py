import jsonpickle
import json
from TTP import *

from datetime import date
import time

import argparse
import os
import sys
import pickle
import socket
import threading
from web3 import Web3

from py_ecc_tester import *
root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

def getAccAddress():
	file_path = os.path.join(root_dir, "accumulator_address.pickle")
	f = open(file_path,'rb')
	verify_address = pickle.load(f)
	f.close()
	return verify_address

acc_address = getAccAddress()
ab = "http://127.0.0.1:7546"
w3 = Web3(Web3.HTTPProvider(ab, request_kwargs = {'timeout' : 300}))
tf = json.load(open('./build/contracts/Accumulator.json'))
acc_address = Web3.toChecksumAddress(acc_address)
acc_contract = w3.eth.contract(address = acc_address, abi = tf['abi'])

a = acc_contract.functions.get_delta().call()
print(a[1])