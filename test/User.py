import jsonpickle
from TTP import *

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

# python3 User.py --unique-name user1 --ip 127.0.0.1 --port 6001 --address 0x23B0505cE4C8f15667Ffae865a6a9c4Acb571F33 --rpc-endpoint "ws://127.0.0.1:7545"
# python3 User.py --unique-name user2 --ip 127.0.0.1 --port 6002 --address 0x48dC061f216f82A886B7E2aF06c677Ba16aB08dA --rpc-endpoint "ws://127.0.0.1:7545"

parser = argparse.ArgumentParser(description="User Creation")
parser.add_argument("--unique-name", type=str, required = True, help= "A name that uniquely identifies the user.")
parser.add_argument("--ip", type=str, default = '127.0.0.1', required = False,  help= "The ip at which user is waiting for Vcert.")
parser.add_argument("--port", type=str, default = None, required = True,  help= "The port on which user is waiting for Vcert.")
parser.add_argument("--address", type=str, default = None, required = True,  help= "The blockchain address on which user is running.")
parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a user is connected to blockchain network.")
args = parser.parse_args()

mode = 0o777
root_dir = "/home/vinay/Downloads/ModifierVersionGanache/ROOT"

msk = genRandom()
user_addr = args.address

try:
	os.mkdir(root_dir, mode = mode)
except FileExistsError as e:
	pass

user_dir = os.path.join(root_dir, "USER")
try:
	os.mkdir(user_dir, mode = mode)
except FileExistsError as e:
	pass

specific_user_dir = os.path.join(user_dir, args.unique_name)
try:
	os.mkdir(user_dir, mode = mode)
except FileExistsError as e:
	pass

def gethostbytitle(title):
	register_path = os.path.join(root_dir, "ca_register.pickle")
	f = open(register_path,'rb')
	RegisteredList = pickle.load(f)
	f.close()
	for register in RegisteredList:
		if register["title"] == title:
			return (register["req-ip"], register["req-port"])
	return ('', '')

def downloadSchema(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "schema.pickle")
	f = open(ca_file_path,'rb')
	schema = pickle.load(f)
	f.close()
	return schema

def downloadEncoding(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "encoding.pickle")
	f = open(ca_file_path,'rb')
	encoding = pickle.load(f)
	f.close()
	return encoding

def downloadSchemaOrder(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "schemaOrder.pickle")
	f = open(ca_file_path,'rb')
	schemaOrder = pickle.load(f)
	f.close()
	return schemaOrder

def downloadParams(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "params.pickle")
	f = open(ca_file_path,'rb')
	json_params = pickle.load(f)
	params = jsonpickle.decode(json_params)
	f.close()
	return params

def downloadPk(title):
	ca_path = os.path.join(root_dir, title)
	ca_file_path = os.path.join(ca_path, "pk.pickle")
	f = open(ca_file_path,'rb')
	json_pk = pickle.load(f)
	pk = jsonpickle.decode(json_pk)
	f.close()
	return pk

def downloadPublicInformation(title):
	return (downloadSchema(title), downloadEncoding(title), downloadSchemaOrder(title), downloadParams(title), downloadPk(title))

def updateRequiredVcerts(requiredVcerts):
	prevCombination, prevParams, prevVcerts, prevAttributes = [], [], [], []
	for i in range(len(requiredVcerts)):
		title = requiredVcerts[i]["title"]
		prevCombination.append(title)
		schema, encoding, schemaOrder, params, pk = downloadPublicInformation(title)
		prevVcerts.append((requiredVcerts[i]["commit"], requiredVcerts[i]["signature"]))
		prevParams.append(params)
		attributes = [requiredVcerts[i]["msk"]]
		encode_str = [0]
		for key in schemaOrder:
			attributes.append(requiredVcerts[i]["attributes"][key])
			encode_str.append(encoding[key])
		attributes.append(requiredVcerts[i]["r"])
		encode_str.append(0)
		prevAttributes.append(encode_attributes(attributes, encode_str))
	return (prevCombination, prevParams, prevVcerts, prevAttributes)

def RequestVcert(title, requiredVcerts = []):
	ip, port = gethostbytitle(title)
	if port == '':
		print("vcert request failed")
		return
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error as err:
		print ("socket creation failed with error %s" %(err))
	s.connect((ip, int(port)))
	print("connected to port : ", port)
	vcert = {"title":title, "attributes" : None, "commit": None, "signature": None}
	try:
		prevCombination, prevParams, prevVcerts, prevAttributes = updateRequiredVcerts(requiredVcerts)
		schema, encoding, schemaOrder, params, pk = downloadPublicInformation(title)
		attributes = {}
		for key in schemaOrder:
			value = None
			if schemaOrder[key] == "msk":
				value = msk
			elif schemaOrder[key] == "r":
				value = genRandom()
			elif encoding[key] == 1:
				value = input("Enter the attribute \'"+key+"\' of type "+str(schema[key]["type"]))
			elif encoding[key] == 2:
				value = int(value = input("Enter the attribute \'"+key+"\' of type "+str(schema[key]["type"])))
			elif encoding[key] == 3:
				str_date = input("Enter the attribute \'"+key+"\' in Y-m-d format")
				_date = datetime.datetime.strptime(str_date,"%Y-%m-%d").date()
				value = int(_date.strftime('%Y%m%d'))
			attributes.setdefault(key, value)

		attribute = []
		encode_str = []
		for key in schemaOrder:
			attribute.append(attributes[key])
			encode_str.append(encoding[key])

		encoded_attribute = encode_attributes(attribute, encode_str)
		commit = GenCommitment(params, encoded_attribute)
		prevAttributes.append([attribute[0], attribute[-1]])
		zkpok = GenZKPoK(params, prevParams, prevVcerts, prevAttributes, commit)

		# prevVcerts = [(x[1], x[2]) for x in prevVcerts]

		# requestObject = VCertRequestJSON(prevVcerts, attributes, commit, zkpok)
		requestJSON = jsonpickle.encode((prevCombination, prevVcerts, attributes, commit, zkpok, args.ip, args.port))
		s.send(requestJSON.encode())
		s.close()

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		s.bind((args.ip, int(args.port)))        
		print (args.unique_name + " binded to %s" %(port))
		s.listen(5)    
		print (args.unique_name +" is listening")
		c, addr = s.accept()

		issueVcertJSON = s.recv(8192).decode()

		issueVcert = jsonpickle.decode(issueVcertJSON)
		_commit, signature = issueVcert

		if commit != _commit:
			print("Request is corrupted.")
		elif VerifyVcerts(params, pk, signature, SHA256(commit)) == True:
			vcert["attributes"] = attributes
			vcert["commit"] = commit
			vcert["signature"] = signature
		else:
			print("Request is corrupted.")
	except Exception as e:
		print(e)
	finally:
		s.close()
	return vcert

vcert1 = RequestVcert("Identity Certificate")
print(vcert1)
print("Got Identity Certificate")
vcert2 = RequestVcert("Income Certificate", [vcert1])
print(vcert2)
print("Got Income Certificate")
all_vcerts = [vcert1, vcert2]

# -----------------------------------------------------------------

def getValidatorsList(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "validatorsList.pickle")
	f = open(ac_file_path,'rb')
	validatorsList = pickle.load(f)
	f.close()
	return validatorsList

def getAggregateVerificationKey(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "aggregate_vk.pickle")
	f = open(ac_file_path,'rb')
	json_aggregate_vk = pickle.load(f)
	f.close()
	aggregate_vk = jsonpickle.decode(json_aggregate_vk)
	return aggregate_vk

def getVerificationKeys(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "vk.pickle")
	f = open(ac_file_path,'rb')
	json_vk = pickle.load(f)
	f.close()
	vk = jsonpickle.decode(json_vk)
	return vk

def getOpenersList(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "openersList.pickle")
	f = open(ac_file_path,'rb')
	openersList = pickle.load(f)
	f.close()
	return openersList

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
  g2, g2x, g1y, g2y = vk
  encoded_vk = []
  encoded_vk.append(encodeG2(g2))
  encoded_vk.append(encodeG2(g2x))
  encoded_vk.append(g1y)
  encoded_g2y = []
  for i in range(len(g2y)):
    encoded_g2y.append(encodeG2(g2y[i]))
  encoded_vk.append(encoded_g2y)
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
  encoded_g2, encoded_g2x, g1y, encoded_g2y = encoded_vk
  vk = []
  vk.append(decodeToG2(encoded_g2))
  vk.append(decodeToG2(encoded_g2x))
  vk.append(g1y)
  g2y = []
  for i in range(len(encoded_g2y)):
    g2y.append(decodeToG2(encoded_g2y[i]))
  vk.append(g2y)
  return tuple(vk)


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

def getThresholdOpeners(title):
	ac_path = os.path.join(root_dir, ac_title)
	ac_file_path = os.path.join(ac_path, "to.pickle")
	f = open(ac_file_path,'rb')
	to = pickle.load(f)
	f.close()
	return to

def getThresholdValidators(title):
	ac_path = os.path.join(root_dir, ac_title)
	ac_file_path = os.path.join(ac_path, "tv.pickle")
	f = open(ac_file_path,'rb')
	tv = pickle.load(f)
	f.close()
	return tv

def getTotalOpeners(title):
	ac_path = os.path.join(root_dir, ac_title)
	ac_file_path = os.path.join(ac_path, "no.pickle")
	f = open(ac_file_path,'rb')
	no = pickle.load(f)
	f.close()
	return no

def getTotalValidators(title):
	ac_path = os.path.join(root_dir, ac_title)
	ac_file_path = os.path.join(ac_path, "nv.pickle")
	f = open(ac_file_path,'rb')
	nv = pickle.load(f)
	f.close()
	return nv

def getTotalAttributes(title):
	ac_path = os.path.join(root_dir, ac_title)
	ac_file_path = os.path.join(ac_path, "q.pickle")
	f = open(ac_file_path,'rb')
	q = pickle.load(f)
	f.close()
	return q

def downloadACParams(title):
	q = getTotalAttributes(title)
	params = setup(q, title)
	return params

ac_title = input("Enter the anonymous credentials title that you want to request (Loan Credential)")

while True:
	time.sleep(15)
	vks = loadValidatorKeys(ac_title)
	opks = loadOpenerKeys(ac_title)
	if None in vks or None in opks:
		pass
	else:
		print(ac_title + " setup is done")
		break

validatorsList = getValidatorsList(ac_title)

validator_dict = {}
for validator in validatorsList:
	validator_dict.setdefault(validator[1], validator[0])

params = downloadACParams(ac_title)
vks = getVerificationKeys(ac_title)
aggregate_vk = getAggregateVerificationKey(ac_title)
opks = loadOpenerKeys(ac_title)


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

def getVerifyAddress():
	file_path = os.path.join(root_dir, "verify_address.pickle")
	f = open(file_path,'rb')
	verify_address = pickle.load(f)
	f.close()
	return verify_address

w3 = Web3(Web3.WebsocketProvider(args.rpc_endpoint, websocket_timeout=60))

params_address = getParamsAddress()
request_address = getRequestAddress()
issue_address = getIssueAddress()
verify_address = getVerifyAddress()

# ------------------------------ ------------------------------------------
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
# Issue.sol
# stores information required for issuance of AC.

tf = json.load(open('./build/contracts/Issue.json'))
issue_address = Web3.toChecksumAddress(issue_address)
issue_contract = w3.eth.contract(address = issue_address, abi = tf['abi'])

# ------------------------------------------------------------------------
# Verify.sol
# verifies the AC with selective disclosure of attributes.

tf = json.load(open('./build/contracts/Verify.json'))
verify_address = Web3.toChecksumAddress(verify_address)
verify_contract = w3.eth.contract(address = verify_address, abi = tf['abi'])

# --------------------------------------------------------------------------

def getCombinations(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "combinations.pickle")
	f = open(ac_file_path,'rb')
	combinations = pickle.load(f)
	f.close()
	return combinations

def checkCombinations(title, combination):
	combinations = getCombinations(title)
	for c in combinations:
		if set(c) == set(combination):
			return True
	return False

def getIncludeIndexes(title, _dependency):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "include_indexes.pickle")
	f = open(ac_file_path,'rb')
	include_indexes = pickle.load(f)
	f.close()
	_include_indexes = []
	for key in _dependency:
		_include_indexes.append(include_indexes[key])
	return _include_indexes

# def _getIncludeIndexes(title, combination):
# 	ac_path = os.path.join(root_dir, title)
# 	ac_file_path = os.path.join(ac_path, "include_indexes.pickle")
# 	f = open(ac_file_path,'rb')
# 	include_indexes = pickle.load(f)
# 	f.close()

# def getIncludeIndexes(title, combination):
# 	encoded_include_indexes = []
# 	for i in range(len(combination)):
# 		ttp_schemaOrder = downloadSchemaOrder(combination[i])
# 		include_indexes = _getIncludeIndexes(title, combination)
# 		encoded_include_indexes.append([0])
# 		for k in ttp_schemaOrder:
# 			encoded_include_indexes[-1].append(include_indexes[combination[i]][k])
# 		encoded_include_indexes[-1].append(0)
# 	return encoded_include_indexes


def CredentialRequest(title, vcerts, combination, public_m = []): #should be encoded public_m
	assert checkCombinations(title, combination), "No such combination."
	params = downloadACParams(title)
	aggregate_vk = getAggregateVerificationKey(title)
	to = getThresholdOpeners(title)
	no = getTotalOpeners(title)
	opks = loadOpenerKeys(title)
	prevVcerts = []	
	prevParams = []
	all_encoded_attr = []
	for cert in vcerts:
		_, encoding, schemaOrder, params, _ = downloadPublicInformation(cert["title"])
		prevParams.append(params)
		prevVcerts.append((cert["commit"], cert["signature"]))
		attributes = cert["attributes"]
		attribute = []
		encode_str = []
		for key in schemaOrder:
			attribute.append(attributes[key])
			encode_str.append(encoding[key])
		encoded_attribute = encode_attributes(attribute, encode_str)
		all_encoded_attr.append(encoded_attribute)

	include_indexes = getIncludeIndexes(title, combination)
	Lambda, os = PrepareCredRequest(params, aggregate_vk, to, no, opks, prevParams, all_encoded_attr, include_indexes, public_m)
	
	(cm, commitments, pi_s, hp, C, pi_o, Dw, Ew, hr, bo) = Lambda
	send_cm = (cm[0].n, cm[1].n)
	send_commitments = [(commitments[i][0].n, commitments[i][1].n) for i in range(len(commitments))]
	send_ciphershares= [([([C[i][j][0].coeffs[1].n,C[i][j][0].coeffs[0].n],[C[i][j][1].coeffs[1].n, C[i][j][1].coeffs[0].n]) for j in range(2)],) for i in range(len(C))]
	send_compressed_cipher = (send_commitments, send_ciphershares)
	private_m = []
	schema = downloadSchema(title)
	for key in schemaOrder:
		if schema[key]['visibility'] == 'private':
			private_m.append(credential["attributes"][key])
	send_hp =  [[(hp[i][j-1][0].n, hp[i][j-1][1].n) for j in range(1, to)] for i in range(len(private_m))]
	send_hr = [(hr[i][0].n, hr[i][1].n) for i in range(len(hr))]
	send_bo = [([bo[i][0].coeffs[1].n,bo[i][0].coeffs[0].n],[bo[i][1].coeffs[1].n,bo[i][1].coeffs[0].n]) for i in range(len(bo))]
	send_Dw = [([Dw[i][0].coeffs[1].n,Dw[i][0].coeffs[0].n],[Dw[i][1].coeffs[1].n,Dw[i][1].coeffs[0].n]) for i in range(len(Dw))]
	send_Ew = [([Ew[i][0].coeffs[1].n,Ew[i][0].coeffs[0].n],[Ew[i][1].coeffs[1].n,Ew[i][1].coeffs[0].n]) for i in range(len(Ew))]
	send_compressed_G2Points = (send_Dw, send_Ew)
	send_vcerts = [((prevVcerts[i][0][0].n, prevVcerts[i][0][1].n), prevVcerts[i][1]) for i in range(len(prevVcerts))]

	pi_s = list(pi_s)
	pi_s.append(combination)
	pi_s = tuple(pi_s)

	print("sending for verification")
	str_public_m = [str(public_m[i]) for i in range(len(public_m))]
	tx_hash = request_contract.functions.RequestCred(title, send_vcerts, send_cm, send_compressed_cipher, send_hp, send_hr, send_bo, pi_s, pi_o, send_compressed_G2Points, str_public_m).transact({'from':user_addr})
	return Lambda, os

# def issue_event_filter(contract):
# 	transfer_filter = contract.events.emitIssue.createFilter(fromBlock="0x0", toBlock='latest')
# 	while True:
# 		signature_log = transfer_filter.get_new_entries()
# 		for i in range(len(signature_log)):
# 			credential_id = signature_log[i]['args']['id']
# 			receiver = signature_log[i]['args']['receiver']
# 			# # only filter the user's blind signatures.
# 			# if _receiver != user_addr:
# 			# 	continue
# 			issuer_address = signature_log[i]['args']['issuer_address']
# 			encoded_h = signature_log[0]['args']['h']
# 			encoded_t = signature_log[0]['args']['t']
# 			#send this data to receiver.
# 			h = (FQ(encoded_h[0]), FQ(encoded_h[1]))
# 			t = (FQ(encoded_t[0]), FQ(encoded_t[1]))
# 			blind_sig = (h, t)
# 		time.sleep(15)


def ReceivePartialCredentials(title, issue_filter, signs, os):
	credential_id = params_contract.functions.getMapCredentials(title).call()
	assert credential_id != 0, "No such AC."
	aggregate_vk = getAggregateVerificationKey(title)
	tv = getTotalValidators(title)
	signs_count = 0
	while True: 
		signature_log = issue_filter.get_new_entries()
		for i in range(len(signature_log)):
			_credential_id = signature_log[i]['args']['id']
			if credential_id != _credential_id:
				continue
			receiver = signature_log[i]['args']['receiver']
			if receiver != user_addr:
				continue
			issuer_address = signature_log[i]['args']['issuer_address']
			_h = signature_log[i]['args']['h']
			_t = signature_log[i]['args']['t']

			h = (FQ(_h[0]), FQ(_h[1]))
			t = (FQ(_t[0]), FQ(_t[1]))
			blind_sig = (h, t)
			issuer_id = validator_dict[issuer_address]
			if signs[issuer_id-1] is None:
				signs[issuer_id-1] = Unblind(params, aggregate_vk, blind_sig, os)
				signs_count += 1
		if signs_count >= tv:
			break
		time.sleep(10)

def getAttributes(title, vcerts, combination, public_m = []):
	attributes = {}
	schema = downloadSchema(title)
	schemaOrder = downloadSchemaOrder(title)
	for key in schemaOrder:
		attributes.setdefault(key, None)

	include_indexes = getIncludeIndexes(title, combination)
	for i in range(len(combination)):
		CASchemaOrder = downloadSchemaOrder(combination[i])
		for j in range(len(include_indexes[i])):
			if include_indexes[i][j] == 1:
				attributes[CASchemaOrder[j]] = vcerts[i]["attributes"][CASchemaOrder[j]]
	
	schema = downloadSchema(title)
	i = 0
	for key in schemaOrder:
		if schema[key]['visibility'] == 'public':
			attributes[key] = public_m[i]
			i += 1
	return attributes

def RequestService(credential, user_addr):
	title = credential["title"]
	print("The available policies are : ")
	total_policies = verify_contract.functions.gettotalPolicies(title).call()
	for i in range(total_policies):
		policy = verify_contract.functions.getPolicy(title, i+1).call()
		print("choose "+str(i+1)+" for : ", str(policy))
	policy_id = int(input("Choose any policy : "))
	disclose_index = verify_contract.functions.getPolicy(title, policy_id).call()
	original_attr = []
	schemaOrder = downloadSchemaOrder(credential["title"])
	for key in schemaOrder:
		original_attr.append(credential["attributes"][key])
	disclose_attr = [original_attr[i] for i in range(len(original_attr)) if disclose_index[i]==1]
	str_disclose_attr = [str(disclose_attr[i]) for i in range(len(disclose_attr))]
	encoding = downloadEncoding(title)

	params = downloadACParams(title)
	_, o, _, _, _, _ = params

	ac_encode_str = []
	private_m = []
	schema = downloadSchema(credential["title"])
	for key in schemaOrder:
		if schema[key]['visibility'] == 'private':
			private_m.append(credential["attributes"][key])
			ac_encode_str.append(encoding[schemaOrder[key]])

	encoded_original_attr = encode_attributes(original_attr, ac_encode_str)
	encoded_disclose_attr = [encoded_original_attr[i] for i in range(len(encoded_original_attr)) if disclose_index[i]==1]
	disclose_attr_enc = [ac_encode_str[i] for i in range(len(ac_encode_str)) if disclose_index[i]==1]

	public_m = []
	public_m_encoding = []
	for key in schemaOrder:
		if schema[key]['visibility'] == 'public':
			public_m.append(credential["attributes"][key])
			public_m_encoding.append(schema[key]["type"])
	encoded_public_m = []
	for i in range(len(public_m)):
		if public_m_encoding[i] == 1:
			encoded_public_m.append(int.from_bytes(sha256(public_m[i].encode("utf8").strip()).digest(), "big") % o)
		else:
			encoded_public_m.append(public_m[i])

	aggregate_vk = getAggregateVerificationKey(credential["title"])

	# proving the possession of AC (Off-chain by user) private_m, disclose_index, disclose_attr, disclose_attr_enc, public_m
	Theta, aggr = ProveCred(params, aggregate_vk, aggr_sig, private_m, disclose_index, disclose_attr, disclose_attr_enc, encoded_public_m)
	(kappa, nu, rand_sig, proof, Aw, _timestamp) = Theta
	# Aw, _timestamp, proof = proof_v

	send_kappa = ((kappa[0].coeffs[1].n, kappa[0].coeffs[0].n), (kappa[1].coeffs[1].n, kappa[1].coeffs[0].n))
	send_nu = (nu[0].n, nu[1].n)
	send_sigma = [(rand_sig[i][0].n, rand_sig[i][1].n) for i in range(len(rand_sig))]
	send_theta = (send_kappa, send_nu, send_sigma, proof)
	send_Aw =  ((Aw[0].coeffs[1].n, Aw[0].coeffs[0].n), (Aw[1].coeffs[1].n, Aw[1].coeffs[0].n))
	if aggr:
		send_aggr = ((aggr[0].coeffs[1].n, aggr[0].coeffs[0].n), (aggr[1].coeffs[1].n, aggr[1].coeffs[0].n))
	else:
		send_aggr = ((0, 0), (0, 0))

	str_public_m = [str(public_m[i]) for i in range(len(public_m))]
	tx_hash = verify_contract.functions.VerifyCred(title, send_theta, str_public_m, send_Aw, send_aggr, disclose_index, str_disclose_attr, disclose_attr_enc, _timestamp).transact({'from':user_addr})

# -------------------------------------------------------------------------------------------------

combination = list(map(str, input("Enter a combination you want to use for credential request (Identity Certificate,Income Certificate)").split(",")))
# combination = ["Identity Certificate", "Income Certificate"] # give some input here. like selecting a combination.

vcerts = []
for cert in all_vcerts:
	if cert["title"] in combination:
		vcerts.append(cert)

#need a handling of public_m
public_m = []
attributes = getAttributes(ac_title, vcerts, combination, public_m)
credential = {"title": ac_title, "attributes" : attributes, "credential": None}

nv = getTotalValidators(args.title)
signs = [None] * nv
tv = getThresholdValidators(args.title)
issue_filter = issue_contract.events.emitIssue.createFilter(fromBlock="0x0", toBlock='latest')

Lambda, os = CredentialRequest(ac_title, vcerts, combination, public_m)
ReceivePartialCredentials(ac_title, issue_filter, signs, os)

aggr_sig = AggCred(params, signs)
credential["credential"] = aggr_sig

RequestService(credential, user_addr)