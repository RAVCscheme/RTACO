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

# The way I am using pickle files are not thread-safe.

# python3 Opener.py --title "Loan Credential" --id 1 --ip 127.0.0.1 --port 8001 --address 0x202870f3671F1d6B401693FBcF66082781D1958F --rpc-endpoint "http://127.0.0.1:7545"
# python3 Opener.py --title "Loan Credential" --id 2 --ip 127.0.0.1 --port 8002 --address 0x34aB8f91ef8524a9eCF47D2eC6ab1DBdC3a2D704 --rpc-endpoint "http://127.0.0.1:7545"
# python3 Opener.py --title "Loan Credential" --id 3 --ip 127.0.0.1 --port 8003 --address 0xdedCA5790B8899dA5168a4D34b171A8294D0Fb5F --rpc-endpoint "http://127.0.0.1:7545"

parser = argparse.ArgumentParser(description="Anonymous Credential Threshold Opening")
parser.add_argument("--title", type=str, default = None, required = True, help= "This is the title of the Anonymous Credential.")
parser.add_argument("--id", type=str, default = None, required = True,  help= "The id of the opener in the Anonymous Credential")
parser.add_argument("--ip", type=str, default = '127.0.0.1', required = False,  help= "The ip at which Attribute Certifier is running.")
parser.add_argument("--port", type=str, default = None, required = True,  help= "The port on which Attribute Certifier is running.")
parser.add_argument("--address", type=str, default = None, required = True,  help= "The blockchain address on which opener is running.")
parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a opener is connected to blockchain network.")
args = parser.parse_args()

root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

ac_path = os.path.join(root_dir, args.title)
ac_file_path = os.path.join(ac_path, "openersList.pickle")

f = open(ac_file_path,'rb')
openersList = pickle.load(f)
f.close()
openersList.append((args.id, args.address))
f = open(ac_file_path,'wb')
pickle.dump(openersList, f)
f.close()


def getParamsAddress():
	file_path = os.path.join(root_dir, "params_address.pickle")
	f = open(file_path,'rb')
	params_address = pickle.load(f)
	f.close()
	return params_address

def getRequestAddress():
	file_path = os.path.join(root_dir, "request_address.pickle")
	f = open(file_path,'rb')
	request_address = pickle.load(f)
	f.close()
	return request_address

def getOpeningAddress():
	file_path = os.path.join(root_dir, "opening_address.pickle")
	f = open(file_path,'rb')
	opening_address = pickle.load(f)
	f.close()
	return opening_address
def getIssueAddress():
	file_path = os.path.join(root_dir, "issue_address.pickle")
	f = open(file_path,'rb')
	opening_address = pickle.load(f)
	f.close()
	return opening_address
def getAccAddress():
	file_path = os.path.join(root_dir, "accumulator_address.pickle")
	f = open(file_path,'rb')
	verify_address = pickle.load(f)
	f.close()
	return verify_address

def getTotalOpeners(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "no.pickle")
	f = open(ac_file_path,'rb')
	no = pickle.load(f)
	f.close()
	return no

def getThresholdOpeners(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "to.pickle")
	f = open(ac_file_path,'rb')
	to = pickle.load(f)
	f.close()
	return to

def getRegister(title):
	register_path = os.path.join(root_dir, "ac_register.pickle")
	f = open(register_path,'rb')
	RegisteredList = pickle.load(f)
	f.close()
	for register in RegisteredList:
		if register["title"] == title:
			return register
	print("No such Anonymous Credentials.")
	return None

# def downloadParams(title):
# 	ac_path = os.path.join(root_dir, title)
# 	ac_file_path = os.path.join(ac_path, "params.pickle")
# 	f = open(ac_file_path,'rb')
# 	json_params = pickle.load(f)
# 	params = jsonpickle.decode(json_params)
# 	f.close()
# 	return params

def encodeG2(g2):
	return (g2[0].coeffs[0].n, g2[0].coeffs[1].n, g2[1].coeffs[0].n, g2[1].coeffs[1].n)

def decodeToG2(encoded_g2):
	return (FQ2([encoded_g2[0], encoded_g2[1],]), FQ2([encoded_g2[2], encoded_g2[3],]),)

def encodeG2List(g2_list):
  encoded_g2_list = []
  for g2 in g2_list:
    if g2 is not None:
      encoded_g2_list.append(encodeG2(g2))
    else:
      encoded_g2_list.append(None)
  return encoded_g2_list

def decodeToG2List(encoded_g2_list):
  g2_list = []
  for encoded_g2 in encoded_g2_list:
    if encoded_g2 is not None:
      g2_list.append(decodeToG2(encoded_g2))
    else:
      g2_list.append(None)
  return g2_list

def encodeVk(vk):
  g2, g2x, g1y, g2y,ycg = vk
  encoded_vk = []
  encoded_vk.append(encodeG2(g2))
  encoded_vk.append(encodeG2(g2x))
  encoded_vk.append(g1y)
  encoded_g2y = []
  for i in range(len(g2y)):
    encoded_g2y.append(encodeG2(g2y[i]))
  encoded_vk.append(encoded_g2y)
  encoded_vk.append(encodeG2(ycg))
  return tuple(encoded_vk)

def encodeVkList(vks):
  encoded_vks = []
  for vk in vks:
    if vk is not None:
      encoded_vks.append(encodeVk(vk))
    else:
      encoded_vks.append(None)
  return encoded_vks

def decodeVkList(encoded_vks):
  vks = []
  for encoded_vk in encoded_vks:
    if encoded_vk is not None:
      vks.append(decodeVk(encoded_vk))
    else:
      vks.append(None)
  return vks

def decodeVk(encoded_vk):
  encoded_g2, encoded_g2x, g1y, encoded_g2y, encoded_ycG = encoded_vk
  vk = []
  vk.append(decodeToG2(encoded_g2))
  vk.append(decodeToG2(encoded_g2x))
  vk.append(g1y)
  g2y = []
  for i in range(len(encoded_g2y)):
    g2y.append(decodeToG2(encoded_g2y[i]))
  vk.append(g2y)
  vk.append(decodeToG2(encoded_ycG))
  return tuple(vk)


def uploadOpenerKeys(title, id, pk): # not thread-safe.
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "openerKeys.pickle")
	f = open(ac_file_path,'rb')
	json_opks = pickle.load(f)
	f.close()
	opks = jsonpickle.decode(json_opks)
	opks[id-1] = encodeG2(pk)
	f = open(ac_file_path,'wb')
	json_opks = jsonpickle.encode(opks)
	pickle.dump(json_opks, f)
	f.close()

def getAggregateVerificationKey(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "aggregate_vk.pickle")
	f = open(ac_file_path,'rb')
	json_vk = pickle.load(f)
	f.close()
	encoded_aggregate_vk = jsonpickle.decode(json_vk)
	aggregate_vk = decodeVk(encoded_aggregate_vk)
	return aggregate_vk

def getOpenersList(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "openersList.pickle")
	f = open(ac_file_path,'rb')
	openersList = pickle.load(f)
	f.close()
	return openersList

def getSchemaOrder(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "schemaOrder.pickle")
	f = open(ac_file_path,'rb')
	schemaOrder = pickle.load(f)
	f.close()
	return schemaOrder

def getSchema(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "schema.pickle")
	f = open(ac_file_path,'rb')
	schema = pickle.load(f)
	f.close()
	return schema

def loadOpenerKeys(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "openerKeys.pickle")
	f = open(ac_file_path,'rb')
	json_opks = pickle.load(f)
	f.close()
	encoded_opks = jsonpickle.decode(json_opks)
	opks = decodeToG2List(encoded_opks)
	return opks

def loadValidatorKeys(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "validatorKeys.pickle")
	f = open(ac_file_path,'rb')
	json_pk = pickle.load(f)
	f.close()
	vks = jsonpickle.decode(json_pk)
	return vks

def uploadOpenerIpPort(title, opener_id, ip, port):
	ac_path = os.path.join(root_dir, title)
	opener_ip_map = os.path.join(ac_path, "opener_ip_map.pickle")
	f = open(opener_ip_map,'rb')
	opener_ip_map_list = pickle.load(f)
	f.close()
	opener_ip_map_list[opener_id-1] = (ip, port)
	f = open(opener_ip_map,'wb')
	pickle.dump(opener_ip_map_list, f)
	f.close()

def getTotalAttributes(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "q.pickle")
	f = open(ac_file_path,'rb')
	q = pickle.load(f)
	f.close()
	return q

def requestKeys(title):
	register = getRegister(title)
	ip, port = register["ip"], register["port"]
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print ("Socket successfully created")
	except socket.error as err:
		print ("socket creation failed with error %s" %(err))
	s.connect((ip, int(port)))
	print("connected to port : ", port)
	keys = {"sk_a": None, "pk_a" : None}
	try:
		opener = "opener:"+args.id
		s.send(opener.encode())

		keysJSON = s.recv(8192).decode()

		keys = jsonpickle.decode(keysJSON)
		encoded_vk_a, sk_a = keys
		vk_a = decodeToG2(encoded_vk_a)
		print("keys")
		print(sk_a)
		print(vk_a)
	except Exception as e:
		s.shutdown(socket.SHUT_RDWR)
		print(e)
	finally:
		s.close()
	return (vk_a, sk_a)

def uploadAccumelatorKeys(title, id, vk_a):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "AccumelatorKeys.pickle")
	f = open(ac_file_path,'rb')
	json_opks = pickle.load(f)
	f.close()
	opks = jsonpickle.decode(json_opks)
	opks[id-1] = encodeG2(vk_a)
	f = open(ac_file_path,'wb')
	json_opks = jsonpickle.encode(opks)
	pickle.dump(json_opks, f)
	f.close()
	
q = getTotalAttributes(args.title)

params = setup(q, args.title)
no = getTotalOpeners(args.title)
to = getThresholdOpeners(args.title)
(opk, osk) = opener_keygen(params)
(vk_a, sk_a) = requestKeys(args.title)

# credential_id, issuing_session_id, decrypted_ciphershare, public_share, vcerts, combination. 
Registry = {}

uploadOpenerKeys(args.title, int(args.id), opk)
uploadOpenerIpPort(args.title, int(args.id), args.ip, args.port)
uploadAccumelatorKeys(args.title, int(args.id), vk_a)
accumulator_secret_key = None
ac_file_path = os.path.join(ac_path, "accum_secret.pickle") #remove this
f = open(ac_file_path,'rb')
a1 = pickle.load(f)
accumulator_secret_key = a1[int(args.id)]
print("accumulator_secert")
print(accumulator_secret_key)
f.close()
params_address = getParamsAddress()
request_address = getRequestAddress()
opening_address = getOpeningAddress()
issue_address = getIssueAddress()
acc_address = getAccAddress()


# w3 = Web3(Web3.WebsocketProvider(args.rpc_endpoint, websocket_timeout=100))
w3 = Web3(Web3.HTTPProvider(args.rpc_endpoint, request_kwargs = {'timeout' : 300}))

# ------------------------------------------------------------------------
# Params.sol
# All the TTP system parameters and Aggregated Validators Key

tf = json.load(open('./build/contracts/Params.json'))
params_address = Web3.toChecksumAddress(params_address)
params_contract = w3.eth.contract(address = params_address, abi = tf['abi'])

# ------------------------------------------------------------------------
# Request.sol
# Contains verify_pi_o function which validates the user request for anonymous credential

tf = json.load(open('./build/contracts/Request.json'))
request_address = Web3.toChecksumAddress(request_address)
request_contract = w3.eth.contract(address = request_address, abi = tf['abi'])

# ------------------------------------------------------------------------
# Opening.sol
# broadcasts the information during the opening protocol.

tf = json.load(open('./build/contracts/Opening.json'))
opening_address = Web3.toChecksumAddress(opening_address)
opening_contract = w3.eth.contract(address = opening_address, abi = tf['abi'])

tf = json.load(open('./build/contracts/Issue.json'))
issue_address = Web3.toChecksumAddress(issue_address)
issue_contract = w3.eth.contract(address = issue_address, abi = tf['abi'])

tf = json.load(open('./build/contracts/Accumulator.json'))
acc_address = Web3.toChecksumAddress(acc_address)
acc_contract = w3.eth.contract(address = acc_address, abi = tf['abi'])

# -------------------------------------------------------------------------

pending_requests = [] 
updated_count = 0
pending_requests_lock = threading.Lock()
wait_initially = threading.Event()
wait_initially.clear()
def getAccPub(title):
	ac_path = os.path.join(root_dir, title)
	file_path = os.path.join(ac_path, "aggregate_vk_a.pickle")
	f = open(file_path,'rb')
	verify_address = decodeToG2(jsonpickle.decode(pickle.load(f)))
	f.close()
	return verify_address
aggre_pub_key = getAggregateVerificationKey(args.title)
acc_pub_key = getAccPub(args.title)
# def get_kr_share(sender,id):
# 	time.sleep(10)
# 	ac_file_path = os.path.join(root_dir,"blockchain")
# 	ac_file_path = os.path.join(ac_file_path,"user"+sender)
# 	ac_file_path = os.path.join(ac_file_path,"operner_kr_share.pickle")
# 	f = open(ac_file_path,'rb')
# 	data = pickle.load(f)
# 	print(data)
# 	print(data[id-1])
# 	f.close()
# 	return data

def listen_to_requests():#listening to emit events
	wait_initially.wait()
	request_filter = request_contract.events.emitRequest.createFilter(fromBlock="0x0", toBlock='latest')
	acc_filter = acc_contract.events.send_self_revocation.createFilter(fromBlock="0x0", toBlock='latest')
	issue_filter = issue_contract.events.get_ya_shares.createFilter(fromBlock="0x0", toBlock='latest')
	credential_id = params_contract.functions.getMapCredentials(args.title).call()
	assert credential_id != 0, "No such AC."
	while True:
		storage_log = request_filter.get_new_entries()
		storage_log_2 = acc_filter.get_new_entries()
		for i in range(len(storage_log)):
			current_credential_id = storage_log[i]['args']['id']
			if current_credential_id != credential_id :
				continue
			sender = storage_log[i]['args']['sender'] #string
			#kr = get_kr_share(sender,int(args.id))
			
			encoded_cm = storage_log[i]['args']['cm']
			encoded_vcerts = storage_log[i]['args']['vcerts']
			encoded_commitments = storage_log[i]['args']['commitments']
			encoded_ciphershares = storage_log[i]['args']['ciphershares']
			public_m = storage_log[i]['args']['public_m']
			combination = storage_log[i]['args']['combination']
			opener_kr_share = storage_log[i]["args"]["opener_shares"]
			kr = int(opener_kr_share[int(args.id)-1])
			print("kr")
			print(kr)
			vcerts = []
			for i in range(len(encoded_vcerts)):
				vcerts.append(((FQ(encoded_vcerts[i][0]), FQ(encoded_vcerts[i][1])), (encoded_vcerts[i][2], encoded_vcerts[i][3])))
			cm = (FQ(encoded_cm[0]), FQ(encoded_cm[1]))
			commitments = []
			for i in range(len(encoded_commitments)):
				commitments.append((FQ(encoded_commitments[i][0]), FQ(encoded_commitments[i][1])))
			ciphershares = []
			for i in range(len(encoded_ciphershares)):
				ciphershares.append(((FQ2([encoded_ciphershares[i][1], encoded_ciphershares[i][0],]), FQ2([encoded_ciphershares[i][3],encoded_ciphershares[i][2],]),), (FQ2([encoded_ciphershares[i][5], encoded_ciphershares[i][4],]), FQ2([encoded_ciphershares[i][7],encoded_ciphershares[i][6],]),)))
			Lambda = (cm, commitments, ciphershares, public_m, vcerts, combination)
			pending_requests_lock.acquire()
			pending_requests.append((sender,cm, ciphershares[int(args.id)-1], public_m, vcerts, combination,kr))
			pending_requests_lock.release()
			asd = False
			while True:
				storage_log = issue_filter.get_new_entries()
				for i in range(len(storage_log)):
					asd = True
					current_credential_id = storage_log[i]['args']['id']
					print("current_id")
					print(current_credential_id)
					if current_credential_id != credential_id :
						continue
					ans = compute_hash(params, cm)
					s = int.from_bytes(to_binary256(ans), 'big', signed=False)
					a1 = multiply(G1, (accumulator_secret_key + kr) % curve_order)
					a1 = (a1[0].n, a1[1].n)
					tx_hash = acc_contract.functions.recieve_ya_share(int(args.id),a1,s).transact({'from': args.address, 'gas': 100000000})
					w3.eth.waitForTransactionReceipt(tx_hash)
					print("accum_sec_sent")
					print(a1)
				if asd:
					break
		
		for i in range(len(storage_log_2)):
			kr = storage_log_2[i]['args']['kr']
			W = storage_log_2[i]['args']['W']
			H = storage_log_2[i]['args']['H']
			S = storage_log_2[i]['args']['S']
			cm = storage_log_2[i]['args']['cm']
			delta = acc_contract.functions.get_delta().call()
			delta = (FQ(delta[0]), FQ(delta[1]))
			W = (FQ(W[0]), FQ(W[1]))
			H = (FQ(H[0]), FQ(H[1]))
			S = (FQ(S[0]), FQ(S[1]))
			acm = []
			for i in cm:
				acm.append((FQ(i[0]), FQ(i[1])))
			st = time.time()
			tf = VerifyRevokeCred(kr,W,H,S,acm, delta, acc_pub_key,aggre_pub_key)
			et = time.time()
			print("kr_verify_time", et-st)
			print("tf")
			print(tf)
			st = time.time()
			tx_hash = acc_contract.functions.recieve_ya_share_revocation(int(args.id),accumulator_secret_key,s).transact({'from': args.address})
			w3.eth.waitForTransactionReceipt(tx_hash)
			et = time.time()
			print("recieve_ya_share_time", et-st)
		time.sleep(15)

def updateRegistry():
	global updated_count
	global pending_requests
	global osk
	schemaOrder = getSchemaOrder(args.title)
	schema = getSchema(args.title)
	aggregate_vk = getAggregateVerificationKey(args.title)
	_, _, _, beta,ycG = aggregate_vk
	pending_requests_lock.acquire()
	pending_requests_count = len(pending_requests)
	pending_requests_lock.release()
	credential_id = params_contract.functions.getMapCredentials(args.title).call()

	while updated_count < pending_requests_count:
		sender,cm, ciphershare, public_m, vcerts, combination, kr = pending_requests[updated_count]
		h = compute_hash(params, cm)
		_, o, _, _, _, _ = params
		issuing_session_id = int.from_bytes(to_binary256(h), 'big', signed=False)

		Registry.setdefault(credential_id, {})
		Registry[credential_id].setdefault(issuing_session_id, {})
		Registry[credential_id][issuing_session_id].setdefault("private-share", add(elgamal_dec(params, osk, ciphershare) ,multiply(ycG,kr)))
		j = 0
		public_share = None

		for i in range(len(schemaOrder)):
			key = schemaOrder[i]
			if schema[key]["visibility"] == "public":
				if schema[key]["type"] == type("string"):
					public_share = add(public_share, multiply(beta[i], (int.from_bytes(sha256(public_m[j].encode("utf8").strip()).digest(), "big") % o) ))
				else:
					public_share = add(public_share, multiply(beta[i], public_m[j]))
				j += 1
			else:
				pass
		Registry[credential_id][issuing_session_id].setdefault("public-share", public_share) # it contains attributes in the order of schemaOrder
		Registry[credential_id][issuing_session_id].setdefault("vcerts", vcerts)
		Registry[credential_id][issuing_session_id].setdefault("combination", combination)
		updated_count += 1

def opening_event_filter(opening_filter, opener_dict, credential_id):
	Reg = {}
	while True:
		opening_log = opening_filter.get_new_entries()
		for i in range(len(opening_log)):
			_credential_id = opening_log[i]['args']['id']
			if _credential_id != credential_id:
				continue
			opening_session_id = opening_log[i]['args']['opening_session_id']
			opener_address = opening_log[i]['args']['opener_address'] # deduce opener id from this.
			opener_id = opener_dict[opener_address]
			# indexes.add(opener_id)
			openingshares = opening_log[i]['args']['openingshares']
			Reg.setdefault(opener_id, {})
			for j in range(len(openingshares)):
				issuing_session_id = openingshares[j][0]
				pairing_share = FQ12(openingshares[j][1:13])
				Reg[opener_id].setdefault(issuing_session_id, pairing_share) # have to map here opener id to Reg.
		if len(Reg.keys()) >= to:
			return Reg
		time.sleep(15)

def getCAIpPort(title):
	register_path = os.path.join(root_dir, "ca_register.pickle")
	f = open(register_path,'rb')
	RegisteredList = pickle.load(f)
	f.close()
	for register in RegisteredList:
		if register["title"] == title:
			return (register["open-ip"], register["open-port"])
	return None

def openingThread():
	credential_id = params_contract.functions.getMapCredentials(args.title).call()
	assert credential_id != 0, "No such AC."
	opening_filter = opening_contract.events.emitOpening.createFilter(fromBlock="0x0", toBlock='latest')
	aggregate_vk = getAggregateVerificationKey(args.title)
	openersList = getOpenersList(args.title)
	opener_dict = {}
	for opener in openersList:
		opener_dict.setdefault(opener[1], opener[0])
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	s.bind((args.ip, int(args.port)))        
	print ("Opener "+ args.id + " binded to %s" %(args.port))
	s.listen(10)    
	print ("Opener "+ args.id +" is listening")
	while True:
		c, addr = s.accept()
		print("Opening request is received")
		sigmaJSON = c.recv(8192).decode()
		open_sigma = jsonpickle.decode(sigmaJSON)
		updateRegistry()
		opening_session_id = int.from_bytes(to_binary256(open_sigma[0]), 'big', signed=False)
		st = time.time()
		shareRegistry = PreOpening(params, Registry[credential_id], open_sigma)
		send_open_shares = []
		for issuing_session_id in shareRegistry:
			shares = shareRegistry[issuing_session_id]
			pairing_values = [0]* 13
			pairing_values[0] = issuing_session_id
			for i in range(12):
				pairing_values[i+1] = shares.coeffs[i].n
			send_open_shares.append(pairing_values)

		tx_hash = opening_contract.functions.SendOpeningInfo(args.title, opening_session_id, send_open_shares).transact({'from': args.address})
		# opener_receipt = w3.eth.waitForTransactionReceipt(tx_hash)

		Reg = opening_event_filter(opening_filter, opener_dict, credential_id)

		ret_shares = {}
		indexes = [] # opener-ids
		for opener_id in Reg:
			indexes.append(int(opener_id))
			ret_shares.setdefault(int(opener_id), {})
			ret_shares[int(opener_id)] = Reg[opener_id]

		
		issuing_session_id = OpenCred(params, ret_shares, indexes, open_sigma, to, Registry[credential_id], aggregate_vk)
		et = time.time()
		print("Credential openeing", et-st)
		
		if issuing_session_id == None:
			print("No user matched")
		else:
			vcerts = Registry[credential_id][issuing_session_id]["vcerts"]
			combination = Registry[credential_id][issuing_session_id]["combination"]
			print("Which CA Do you want to query ?")
			for i in range(len(combination)):
				print("Enter "+str(i)+" for "+combination[i])
			ca_index = int(input())
			vcert = vcerts[ca_index]

			ca_ip, ca_port = getCAIpPort(combination[ca_index])

			c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			c.connect((ca_ip, int(ca_port)))
			vcertJSON = jsonpickle.encode(vcert)
			c.send(vcertJSON.encode())
			attributesJSON = c.recv(8192).decode()
			attributes = jsonpickle.decode(attributesJSON)
			if attributes is None:
				print("CA refused to disclose the user attributes") # Can configure to get the name of the CA.
			else:
				print("The user is : ")
				print(attributes)
			c.close()

listen_thread  = threading.Thread(target = listen_to_requests)
listen_thread.start()

print("sleeping")

while True:
	time.sleep(20)
	vks = loadValidatorKeys(args.title)
	opks = loadOpenerKeys(args.title)
	if None in vks or None in opks:
		pass
	else:
		wait_initially.set()
		print("Setup is done")
		break 

openingThread()