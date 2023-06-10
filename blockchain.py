import jsonpickle
from TTP import *
from SP_verify import *
import datetime
import time

import argparse
import os
import sys
import pickle
import socket
import json
from web3 import Web3

from TTP import *
from py_ecc_tester import *

mode = 0o777
root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

def getIssueAddress():
	file_path = os.path.join(root_dir, "request_address.pickle")
	f = open(file_path,'rb')
	issue_address = pickle.load(f)
	f.close()
	return issue_address

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545", request_kwargs = {'timeout' : 300}))
request_address = getIssueAddress()

tf = json.load(open('./build/contracts/Request.json'))
issue_address = Web3.toChecksumAddress(request_address)
issue_contract = w3.eth.contract(address = issue_address, abi = tf['abi'])

issue_filter = issue_contract.events.emitRequest.createFilter(fromBlock="0x0", toBlock='latest')

specific_user_dir = os.path.join(root_dir, "blockchain")

delta = G1
id_kr = {}
try:
	os.mkdir(specific_user_dir, mode = mode)
except FileExistsError as e:
	pass

def write_kr_shares(send, data,filename):
	ac_file_path = os.path.join(specific_user_dir,"user"+send)
	ac_file_path = os.path.join(ac_file_path,filename)
	f = open(ac_file_path,'wb')
	pickle.dump(data, f)
	f.close()

def gen_kr_shares(sender_addr):
	kr,op_kr_shares,vk_kr_shares = create_accumulator_shares(curve_order,3,3,2,2) # change this 
	print("kr")
	print(kr)
	print("op_kr_shares")
	print(op_kr_shares)
	print("vk_kr_shares")
	print(vk_kr_shares)
	write_kr_shares(sender_addr,op_kr_shares,"operner_kr_share.pickle")
	write_kr_shares(sender_addr, vk_kr_shares,"validators_kr_share.pickle")
	ac_file_path = os.path.join(specific_user_dir,"kr.pickle")
	f = open(ac_file_path,'wb')
	pickle.dump(kr, f)
	f.close()
	id_kr.setdefault(sender_addr,kr)

def make_dir(sender_addr):
	blockchain_dir = os.path.join(root_dir, "blockchain")
	try:
		os.mkdir(blockchain_dir+ "/user"+sender_addr, mode = mode)
	except FileExistsError as e:
		pass

while True:
	signature_log = issue_filter.get_new_entries()
	for i in range(len(signature_log)):
			_credential_id = signature_log[i]['args']['id']
			sender = signature_log[i]['args']['sender']
			vcert = signature_log[i]["args"]["vcerts"]
			commitment = signature_log[i]["args"]["commitments"]
			# X = signature_log[i]["args"]["validator_shares"]
			# Y = signature_log[i]["args"]["Y"]
			public_m = signature_log[i]["args"]["public_m"]
			combination = signature_log[i]["args"]["combination"]
			make_dir(sender)
			gen_kr_shares(sender)
			
            #send kr shares to validators and openers

            #wait for emitIssue and ask openers to share ya shares

            #gen_kr_and_witness_send to user
			
	
	print(signature_log)
	time.sleep(5)