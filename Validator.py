import jsonpickle
import socket
import argparse
import os
from web3 import Web3
import json
import pickle
import threading

from py_ecc_tester import *

# python3 Validator.py --title "Loan Credential" --id 1 --address 0x444D3aa9426Ca8e339d607bF53262A8B524B844e --rpc-endpoint "http://127.0.0.1:7545"
# python3 Validator.py --title "Loan Credential" --id 2 --address 0x2D0B894312087b3BF55e4432871b6FD3CC8c180A --rpc-endpoint "http://127.0.0.1:7545"
# python3 Validator.py --title "Loan Credential" --id 3 --address 0x5126e167868d403dba7DbC5a28bA0e5ACbb086C0 --rpc-endpoint "http://127.0.0.1:7545"

parser = argparse.ArgumentParser(description="Anonymous Credential")
parser.add_argument("--title", type=str, default = None, required = True, help= "This is the title of the Anonymous Credential.")
# parser.add_argument("--name", type=str, default = None, required = True, help= "This is the organization of the Anonymous Credential.")
parser.add_argument("--id", type=str, default = None, required = True,  help= "The id of the validator giving the Anonymous Credential")
# parser.add_argument("--ip", type=str, default = '127.0.0.1', required = False,  help= "The ip at which validator is running.")
# parser.add_argument("--port", type=str, default = None, required = True,  help= "The port on which validator is running.")
parser.add_argument("--address", type=str, default = None, required = True,  help= "The blockchain address on which validator is running.")
parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a validator is connected to blockchain network.")

args = parser.parse_args()


root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

# validator_address = hex(int(args.address, base = 16))
validator_address = args.address

ac_path = os.path.join(root_dir, args.title)
ac_file_path = os.path.join(ac_path, "validatorsList.pickle")


f = open(ac_file_path,'rb')
validatorsList = pickle.load(f)
f.close()
validatorsList.append((args.id, args.address))
f = open(ac_file_path,'wb')
pickle.dump(validatorsList, f)
f.close()



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
  g2, g2x, g1y, g2y, ycg = vk
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
	keys = {"sk": None, "pk" : None}
	try:
		validator = "validator:"+args.id
		s.send(validator.encode())

		keysJSON = s.recv(8192).decode()

		keys = jsonpickle.decode(keysJSON)
		encoded_vk, sk = keys
		vk = decodeVk(encoded_vk)
	except Exception as e:
		s.shutdown(socket.SHUT_RDWR)
		print(e)
	finally:
		s.close()
	return (vk, sk)

def loadOpenerKeys(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "openerKeys.pickle")
	f = open(ac_file_path,'rb')
	json_pk = pickle.load(f)
	f.close()
	encoded_opks = jsonpickle.decode(json_pk)
	opks = decodeToG2List(encoded_opks)
	return opks

def loadValidatorKeys(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "validatorKeys.pickle")
	f = open(ac_file_path,'rb')
	json_pk = pickle.load(f)
	f.close()
	encoded_vks = jsonpickle.decode(json_pk)
	vks = decodeVkList(encoded_vks)
	return vks

def uploadValidatorKeys(title, id, pk): 
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "validatorKeys.pickle")
	f = open(ac_file_path,'rb')
	json_pks = pickle.load(f)
	f.close()
	pks = jsonpickle.decode(json_pks)
	pks[id-1] = encodeVk(pk)
	f = open(ac_file_path,'wb')
	json_pks = jsonpickle.encode(pks)
	pickle.dump(json_pks, f)
	f.close()

# -------------------------------------------------------
def getTotalAttributes(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "q.pickle")
	f = open(ac_file_path,'rb')
	q = pickle.load(f)
	f.close()
	return q

q = getTotalAttributes(args.title)

params = setup(q, args.title)
(vk, sk) = requestKeys(args.title)
uploadValidatorKeys(args.title, int(args.id), vk)

# -------------------------------------------------------

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

def getIssueAddress():
	file_path = os.path.join(root_dir, "issue_address.pickle")
	f = open(file_path,'rb')
	issue_address = pickle.load(f)
	f.close()
	return issue_address


params_address = getParamsAddress()
request_address = getRequestAddress()
issue_address = getIssueAddress()

# w3 = Web3(Web3.WebsocketProvider(args.rpc_endpoint, websocket_timeout=60))
w3 = Web3(Web3.HTTPProvider(args.rpc_endpoint, request_kwargs = {'timeout' : 300}))

# ------------------------------------------------------------------------
# Params.sol

tf = json.load(open('./build/contracts/Params.json'))
params_address = Web3.toChecksumAddress(params_address)
params_contract = w3.eth.contract(address = params_address, abi = tf['abi'])

# ------------------------------------------------------------------------
# Request.sol

tf = json.load(open('./build/contracts/Request.json'))
request_address = Web3.toChecksumAddress(request_address)
request_contract = w3.eth.contract(address = request_address, abi = tf['abi'])

# ------------------------------------------------------------------------
# Issue.sol

tf = json.load(open('./build/contracts/Issue.json'))
issue_address = Web3.toChecksumAddress(issue_address)
issue_contract = w3.eth.contract(address = issue_address, abi = tf['abi'])

# -------------------------------------------------------------------------

pending_requests = []
served_count = 0
pending_requests_lock = threading.Lock()
wait_initially = threading.Event()
wait_initially.clear()
sender_kr ={}
def listen_to_requests():#Where code waits for emit event
	wait_initially.wait()
	request_filter = request_contract.events.emitRequest.createFilter(fromBlock="0x0", toBlock='latest')
	credential_id = params_contract.functions.getMapCredentials(args.title).call()
	assert credential_id != 0, "No such AC."
	while True:
		storage_log = request_filter.get_new_entries()
		for i in range(len(storage_log)):
			current_credential_id = storage_log[i]['args']['id']
			if current_credential_id != credential_id :
				continue
			sender = storage_log[i]['args']['sender'] #string
			encoded_cm = storage_log[i]['args']['cm']
			encoded_vcerts = storage_log[i]['args']['vcerts']
			encoded_commitments = storage_log[i]['args']['commitments']
			# encoded_ciphershares = storage_log[i]['args']['ciphershares']
			public_m = storage_log[i]['args']['public_m']
			combination = storage_log[i]['args']['combination']
			validator_kr_share = storage_log[i]["args"]["validator_shares"]
			vcerts = []
			for i in range(len(encoded_vcerts)):
				vcerts.append(((FQ(encoded_vcerts[i][0]), FQ(encoded_vcerts[i][1])), (encoded_vcerts[i][2], encoded_vcerts[i][3])))
			cm = (FQ(encoded_cm[0]), FQ(encoded_cm[1]))
			commitments = []
			for i in range(len(encoded_commitments)):
				commitments.append((FQ(encoded_commitments[i][0]), FQ(encoded_commitments[i][1])))
			# ciphershares = []
			# for i in range(len(encoded_ciphershares)):
			# 	ciphershares.append(((FQ2([encoded_ciphershares[i][1], encoded_ciphershares[i][0],]), FQ2([encoded_ciphershares[i][3],encoded_ciphershares[i][2],]),), (FQ2([encoded_ciphershares[i][5], encoded_ciphershares[i][4],]), FQ2([encoded_ciphershares[i][7],encoded_ciphershares[i][6],]),)))
			# Lambda = (cm, commitments, ciphershares, public_m, vcerts, combinations)
			pending_requests_lock.acquire()
			pending_requests.append((sender, cm, commitments, public_m, vcerts, combination, validator_kr_share))
			pending_requests_lock.release()
		time.sleep(10)

# def get_kr_share(sender,id):
# 	ac_file_path = os.path.join(root_dir,"blockchain")
# 	ac_file_path = os.path.join(ac_file_path,"user"+sender)
# 	ac_file_path = os.path.join(ac_file_path,"validators_kr_share.pickle")
# 	f = open(ac_file_path,'rb')
# 	data = pickle.load(f)[id-1]
# 	f.close()
# 	return data

def issuePartialCredentials(pending_requests_count, served_count, sk):
	sender, cm, commitments, public_m, vcerts, combination, validator_kr_share = pending_requests[served_count]
	time.sleep(2)
	#kr = get_kr_share(sender,int(args.id))
	kr = validator_kr_share[int(args.id)-1]
	print("kr")
	print(kr)
	h = compute_hash(params, cm)
	_, o, _, _, _, _ = params
	issuing_session_id = int.from_bytes(to_binary256(h), 'big', signed=False)
	sender_kr.setdefault(issuing_session_id,kr)
	print("sender_kr")
	print(sender_kr)
	public_m_encoding = params_contract.functions.get_public_m_encoding(args.title).call()
	encoded_public_m = []
	for i in range(len(public_m)):
		if public_m_encoding[i] == 0:
			encoded_public_m.append(int(public_m[i]))
		else:
			encoded_public_m.append(int.from_bytes(sha256(public_m[i].encode("utf8").strip()).digest(), "big") % o)

	Lambda = (cm, commitments)
	st  = time.time()
	blind_sig = BlindSignAttr(params, sk,kr,Lambda, encoded_public_m)
	et = time.time()
	print("BlindSignAttr", et-st)
	send_h = [blind_sig[0][0].n, blind_sig[0][1].n]
	send_t = [blind_sig[1][0].n, blind_sig[1][1].n]

	# Upload the blind signature to Issue.sol by Validator_1
	tx_hash = issue_contract.functions.SendBlindSign(args.title, sender, send_h, send_t).transact({'from':validator_address})


#new thread is created to listen to emit events
listen_thread = threading.Thread(target = listen_to_requests)
listen_thread.start()

print("sleeping")

while True:
	time.sleep(40)
	vks = loadValidatorKeys(args.title)
	opks = loadOpenerKeys(args.title)
	if None in vks or None in opks:
		pass
	else:
		wait_initially.set()
		print("Setup is done")
		break

while True:
	time.sleep(5)
	pending_requests_lock.acquire()
	pending_requests_count = len(pending_requests)
	pending_requests_lock.release()
	while served_count < pending_requests_count:
		#checker = input("you have pending requests, Do you want to serve ?")
		print("Skipped Validator inputting")
		checker="y"
		if checker == "y" or checker == "Y":
			issuePartialCredentials(pending_requests_count, served_count, sk)
			served_count += 1
		else:
			pass