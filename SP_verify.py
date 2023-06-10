import jsonpickle
import socket
import argparse
from web3 import Web3
import os
import pickle
import json
import threading
from py_ecc_tester import *

#only change Verify address as in deployed address
# python3 SP.py --title 'Loan Service' --name Bank --address 0xB1A0d85CFeA6ce282729adb7e66CD69f57DC3245 --verify-address 0xBE931E940E2E86c310f7ba619b10006B0089E05D --rpc-endpoint "http://127.0.0.1:7545" --accepts 'Loan Credential'

root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

#w3 = Web3(Web3.WebsocketProvider(args.rpc_endpoint, websocket_timeout = 60))
#w3 = Web3(Web3.HTTPProvider(args.rpc_endpoint, request_kwargs = {'timeout' : 300}))

def getParamsAddress():
	file_path = os.path.join(root_dir, "params_address.pickle")
	f = open(file_path,'rb')
	params_address = pickle.load(f)
	f.close()
	return params_address

def uploadVerifyAddress(verify_address):
	file_path = os.path.join(root_dir, "verify_address.pickle")
	f = open(file_path,'wb')
	pickle.dump(verify_address, f)
	f.close()

def getTotalAttributes(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "q.pickle")
	f = open(ac_file_path,'rb')
	q = pickle.load(f)
	f.close()
	return q

def downloadSchema(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "schema.pickle")
	f = open(ca_file_path,'rb')
	schema = pickle.load(f)
	f.close()
	return schema

def downloadSchemaOrder(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "schemaOrder.pickle")
	f = open(ca_file_path,'rb')
	schemaOrder = pickle.load(f)
	f.close()
	return schemaOrder

def downloadEncoding(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "encoding.pickle")
	f = open(ca_file_path,'rb')
	encoding = pickle.load(f)
	f.close()
	return encoding

def decodeToG2(encoded_g2):
	return (FQ2([encoded_g2[0], encoded_g2[1],]), FQ2([encoded_g2[2], encoded_g2[3],]),)

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

def getAggregateVerificationKey(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "aggregate_vk.pickle")
	f = open(ac_file_path,'rb')
	json_aggregate_vk = pickle.load(f)
	f.close()
	encoded_aggregate_vk = jsonpickle.decode(json_aggregate_vk)
	aggregate_vk = decodeVk(encoded_aggregate_vk)
	return aggregate_vk
#Taken from Request Service from User.py
def getPublicParams(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "public_params.pickle")
	f = open(ac_file_path,'rb')
	ans = jsonpickle.decode(pickle.load(f))
	ans = [(FQ(ans[0][0]), FQ(ans[0][1])), decodeToG2(ans[1]), (FQ(ans[2][0]), FQ(ans[2][1])), decodeToG2(ans[3])]
	f.close()
	return ans

def getAccPub(title):
	ac_path = os.path.join(root_dir, title)
	file_path = os.path.join(ac_path, "aggregate_vk_a.pickle")
	f = open(file_path,'rb')
	verify_address = decodeToG2(jsonpickle.decode(pickle.load(f)))
	f.close()
	return verify_address


def SP_RequestService(title,disclose_index,Theta,encoded_disclosed_attr,encoded_public_m, pi_c, delta):
	#title = credential["title"]
	# schema = downloadSchema(title)
	# schemaOrder = downloadSchemaOrder(title)
	params = downloadACParams(title)
	public_params = getPublicParams(title)
	pub_key = getAccPub(title)
	# _, o, _, _, _, _ = params

	# encoded_private_m = encode_attributes(private_m, ac_encode_str)
	# encoded_disclose_attr = [encoded_private_m[i] for i in range(len(encoded_private_m)) if disclose_index[i]==1]
	# disclose_attr_enc = [ac_encode_str[i] for i in range(len(ac_encode_str)) if disclose_index[i]==1]

	# public_m = []
	# public_m_encoding = []
	# for key in schemaOrder:
	# 	if schema[key]['visibility'] == 'public':
	# 		public_m.append(credential["attributes"][key])
	# 		public_m_encoding.append(schema[key]["type"])
	# encoded_public_m = []
	# for i in range(len(public_m)):
	# 	if public_m_encoding[i] == 1:
	# 		encoded_public_m.append(int.from_bytes(sha256(public_m[i].encode("utf8").strip()).digest(), "big") % o)
	# 	else:
	# 		encoded_public_m.append(public_m[i])

	aggregate_vk = getAggregateVerificationKey(title)

	# # proving the possession of AC (Off-chain by user) private_m, disclose_index, disclose_attr, disclose_attr_enc, public_m
	# Theta, aggr = ProveCred(params, aggregate_vk, aggr_sig, encoded_private_m, disclose_index, disclose_attr, disclose_attr_enc, encoded_public_m)
	# (kappa, nu, rand_sig, proof, Aw, _timestamp) = Theta
	# #Aw, _timestamp, proof = proof_v

	# #Uncomment below to do SP Verification on-chain
	# send_kappa = ((kappa[0].coeffs[1].n, kappa[0].coeffs[0].n), (kappa[1].coeffs[1].n, kappa[1].coeffs[0].n))
	# send_nu = (nu[0].n, nu[1].n)
	# send_sigma = [(rand_sig[i][0].n, rand_sig[i][1].n) for i in range(len(rand_sig))]
	# send_theta = (send_kappa, send_nu, send_sigma, proof)
	# send_Aw =  ((Aw[0].coeffs[1].n, Aw[0].coeffs[0].n), (Aw[1].coeffs[1].n, Aw[1].coeffs[0].n))
	# if aggr:
	# 	send_aggr = ((aggr[0].coeffs[1].n, aggr[0].coeffs[0].n), (aggr[1].coeffs[1].n, aggr[1].coeffs[0].n))
	# else:
	# 	send_aggr = ((0, 0), (0, 0))

	# str_public_m = [str(public_m[i]) for i in range(len(public_m))]
	# encoded_disclosed_attr = encode_attributes(disclose_attr, disclose_attr_enc)
	st = time.time()
	tf = VerifyCred(params, aggregate_vk, Theta, disclose_index, encoded_disclosed_attr, encoded_public_m, pi_c, public_params, pub_key, delta)
	et = time.time()
	print("Credential verify", et-st)
	print("Verify Cred : ")
	return tf
	#off-chain SP verification
	#tx_hash = verify_contract.functions.VerifyCred(title, send_theta, str_public_m, send_Aw, send_aggr, disclose_index, str_disclose_attr, disclose_attr_enc, _timestamp).transact({'from':user_addr})

def downloadACParams(title):
	q = getTotalAttributes(title)
	params = setup(q, title)
	return params

#Commented below 3
# verify_address = args.verify_address
# uploadVerifyAddress(verify_address)
# params_address = getParamsAddress()

# ------------------------------------------------------------------------
# Params.sol
# All the TTP system parameters and Aggregated Validators Key

# tf = json.load(open('./build/contracts/Params.json'))
# params_address = Web3.toChecksumAddress(params_address)
# params_contract = w3.eth.contract(address = params_address, abi = tf['abi'])

# ------------------------------------------------------------------------

# ------------------------------------------------------------------------
# Verify.sol
# verifies the AC with selective disclosure of attributes.

# tf = json.load(open('./build/contracts/Verify.json'))
# verify_address = Web3.toChecksumAddress(verify_address)
# verify_contract = w3.eth.contract(address = verify_address, abi = tf['abi'])

# -------------------------------------------------------------------------


# register_path = os.path.join(root_dir, "ac_register.pickle")
# f = open(register_path,'rb')
# RegisteredList = pickle.load(f)
# f.close()

# acceptable_ACs = args.accepts
# for cur_title in acceptable_ACs:
# 	ac_path = os.path.join(root_dir, cur_title)
# 	ac_file_path = os.path.join(ac_path, "schemaOrder.pickle")
# 	f = open(ac_file_path,'rb')
# 	schemaOrder = pickle.load(f)
# 	f.close()

# 	ac_path = os.path.join(root_dir, cur_title)
# 	ac_file_path = os.path.join(ac_path, "schema.pickle")
# 	f = open(ac_file_path,'rb')
# 	schema = pickle.load(f)
# 	f.close()

# 	ac_path = os.path.join(root_dir, cur_title)
# 	ac_file_path = os.path.join(ac_path, "encoding.pickle")
# 	f = open(ac_file_path,'rb')
# 	encoding = pickle.load(f)
# 	f.close()

# 	policy = []
# 	while True:
# 		cur_policy = []
# 		print("Choose the policy for "+ cur_title +" : ")
# 		for k in schemaOrder:
# 			if schema[k]['visibility'] == "private":
# 				tmp = input("Do you choose the "+ k +" to be disclosed ? ")
# 				if tmp == 'no' or tmp == 'n':
# 					cur_policy.append(0)
# 				else:
# 					cur_policy.append(1)
# 		policy.append(cur_policy)
# 		tmp = input("Do you want to another policy ? ")
# 		if tmp == 'no' or tmp == 'n':
# 			break

# 	tx_hash = verify_contract.functions.setPolicy(cur_title, policy).transact({'from':SP_addr})
# 	w3.eth.waitForTransactionReceipt(tx_hash)

# pending_service_requests = []
# pending_requests_lock = threading.Lock()
# served_count = 0
# served_service_requests = []

# def listen_to_service_requests():
# 	verify_filter = verify_contract.events.emitVerify.createFilter(fromBlock="0x0", toBlock='latest')
# 	while True:
# 		service_log = verify_filter.get_new_entries()
# 		for i in range(len(service_log)):
# 			credential_id = service_log[i]['args']['id']
# 			credential = service_log[i]['args']['credential']
# 			public_m = service_log[i]['args']['public_m'] # collect encoding from public repository. (pickle files)
# 			disclosed_indexes = service_log[i]['args']['disclosed_indexes']
# 			disclosed_attributes = service_log[i]['args']['disclosed_attributes']
# 			sigma = ((FQ(credential[0]), FQ(credential[1])),(FQ(credential[2]), FQ(credential[3])))
# 			pending_service_requests.append((credential_id, sigma, public_m, disclosed_indexes, disclosed_attributes))
# 		time.sleep(15)

# def serve_requests(pending_requests_count):
# 	global served_count
# 	service_dict = {}
# 	file_path = os.path.join(root_dir, "served_service_requests.pickle")
# 	try:
# 		f = open(file_path,'rb')
# 		service_dict = pickle.load(f)
# 		f.close()
# 	except:
# 		f = open(file_path,'wb')
# 		pickle.dump(service_dict, f)
# 		f.close()

# 	while served_count < pending_requests_count:
# 		(credential_id, sigma, public_m, disclosed_indexes, disclosed_attributes) = pending_service_requests[served_count]
# 		params = None
# 		for i in range(len(RegisteredList)):
# 			cur_title = RegisteredList[i]["title"]
# 			_credential_id = params_contract.functions.getMapCredentials(cur_title).call()
# 			if _credential_id == credential_id:
# 				params = downloadACParams(cur_title)
# 		h = compute_hash(params, sigma[0])
# 		service_session_id = int.from_bytes(to_binary256(h), 'big', signed=False)
# 		service_dict.setdefault(service_session_id, {})
# 		service_dict[service_session_id].setdefault(credential_id, (sigma, public_m, disclosed_indexes, disclosed_attributes))
# 		print(disclosed_attributes)
# 		served_count += 1
		
# 	f = open(file_path,'wb')
# 	pickle.dump(service_dict, f)
# 	f.close()



# listen_thread = threading.Thread(target = listen_to_service_requests)
# listen_thread.start()

# while True:
# 	time.sleep(20)
# 	pending_requests_lock.acquire()
# 	pending_requests_count = len(pending_service_requests)
# 	pending_requests_lock.release()
# 	if served_count < pending_requests_count:
# 		checker = input("you have pending requests, Do you want to serve ?")
# 		if checker == "y" or checker == "Y":
# 			serve_requests(pending_requests_count)