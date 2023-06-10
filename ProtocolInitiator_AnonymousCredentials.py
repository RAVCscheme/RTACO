import jsonpickle
import json
from TTP import *
from py_ecc_tester import *

from datetime import datetime
import time

import argparse
import os
import pickle
import socket
import threading
from web3 import Web3
#No address to change:
# python3 ProtocolInitiator_AnonymousCredentials.py --title "Loan Credential" --address 0xE279a5e0DEb02eDe68876bea8206EeFb2Ab0E96C --validator-addresses 0x444D3aa9426Ca8e339d607bF53262A8B524B844e 0x2D0B894312087b3BF55e4432871b6FD3CC8c180A 0x5126e167868d403dba7DbC5a28bA0e5ACbb086C0 --opener-addresses 0x202870f3671F1d6B401693FBcF66082781D1958F 0x34aB8f91ef8524a9eCF47D2eC6ab1DBdC3a2D704 0xdedCA5790B8899dA5168a4D34b171A8294D0Fb5F --rpc-endpoint "http://127.0.0.1:7545"

parser = argparse.ArgumentParser(description="Anonymous Credentials registration")
parser.add_argument("--title", type=str, default = None, required = True, help= "This is the title of the Anonymous Credential.")
# parser.add_argument("--name", type=str, default = None, required = True,  help= "The name of organisation giving the Anonymous Credential")
# parser.add_argument("--ip", type=str, default = '127.0.0.1', required = False,  help= "The ip at which organisation is running.")
# parser.add_argument("--port", type=str, default = None, required = True,  help= "The port on which organisation is running.")
# parser.add_argument('--dependency', nargs='+', help='The Vcerts on which the Anonymous Credential issuance depends on.', required=False)
parser.add_argument("--address", type=str, default = None, required = True,  help= "The blockchain address on which organization is running.")
parser.add_argument('--validator-addresses', nargs='+', help='The blockchain addresses of the validators for the Anonymous Credential issuance.', required=True)
parser.add_argument('--opener-addresses', nargs='+', help='The blockchain addresses of the openers for the Anonymous Credential opening.', required=True)
parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a client is connected to blockchain network.")
args = parser.parse_args() 

root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

register_path = os.path.join(root_dir, "ac_register.pickle")
encoding_types = os.path.join(root_dir, "encoding_type_map.pickle")

f = open(encoding_types,'rb')
encoding_type_map = pickle.load(f)
f.close()

def getRegister(register_path):
	f = open(register_path,'rb')
	RegisteredList = pickle.load(f)
	f.close()
	for register in RegisteredList:
		if register["title"] == args.title:
			return register
	print("No such Anonymous Credentials.")
	return None

register = getRegister(register_path)
name, ip, port, dependency = register["name"], register["ip"], register["port"], register["dependency"]


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

def getOpeningAddress():
	file_path = os.path.join(root_dir, "opening_address.pickle")
	f = open(file_path,'rb')
	opening_address = pickle.load(f)
	f.close()
	return opening_address

def getACCAddress():
    file_path = os.path.join(root_dir, "accumulator_address.pickle")
    f = open(file_path,'rb')
    opening_address = pickle.load(f)
    print(opening_address)
    f.close()
    return opening_address

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
  g2, g2x, g1y, g2y,ycG = vk
  encoded_vk = []
  encoded_vk.append(encodeG2(g2))
  encoded_vk.append(encodeG2(g2x))
  encoded_vk.append(g1y)
  encoded_g2y = []
  for i in range(len(g2y)):
    encoded_g2y.append(encodeG2(g2y[i]))
  encoded_vk.append(encoded_g2y)
  encoded_vk.append(encodeG2(ycG))
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

params_address       = getParamsAddress()
request_address      = getRequestAddress()
issue_address        = getIssueAddress()
opening_address      = getOpeningAddress()
accumulator_address  = getACCAddress()

# w3 = Web3(Web3.WebsocketProvider(args.rpc_endpoint, websocket_timeout = 100))
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
# Issue.sol
# stores information required for issuance of AC.

tf = json.load(open('./build/contracts/Issue.json'))
issue_address = Web3.toChecksumAddress(issue_address)
issue_contract = w3.eth.contract(address = issue_address, abi = tf['abi'])

# -------------------------------------------------------------------------
# Opening.sol
# broadcasts the information during the opening protocol.

tf = json.load(open('./build/contracts/Opening.json'))
opening_address = Web3.toChecksumAddress(opening_address)
opening_contract = w3.eth.contract(address = opening_address, abi = tf['abi'])

tf = json.load(open('./build/contracts/Accumulator.json'))
accumulator_address = Web3.toChecksumAddress(accumulator_address)
acc_contract = w3.eth.contract(address = accumulator_address, abi = tf['abi'])

# -------------------------------------------------------------------------

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

def getTotalValidators(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "nv.pickle")
	f = open(ac_file_path,'rb')
	nv = pickle.load(f)
	f.close()
	return nv

def getThresholdValidators(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "tv.pickle")
	f = open(ac_file_path,'rb')
	tv = pickle.load(f)
	f.close()
	return tv

def getTotalAttributes(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "q.pickle")
	f = open(ac_file_path,'rb')
	q = pickle.load(f)
	f.close()
	return q

# def downloadParams(title):
# 	ac_path = os.path.join(root_dir, title)
# 	ac_file_path = os.path.join(ac_path, "params.pickle")
# 	f = open(ac_file_path,'rb')
# 	json_params = pickle.load(f)
# 	params = jsonpickle.decode(json_params)
# 	f.close()
# 	return params

def getCombinations(title):
	ac_path = os.path.join(root_dir, title)
	ac_file_path = os.path.join(ac_path, "combinations.pickle")
	f = open(ac_file_path,'rb')
	combinations = pickle.load(f)
	f.close()
	return combinations

nv = getTotalValidators(args.title)
tv = getThresholdValidators(args.title)
no = getTotalOpeners(args.title)
to = getThresholdOpeners(args.title) 
q = getTotalAttributes(args.title)

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
  g2, g2x, g1y, g2y,ycG = vk
  print("encd")
  print(ycG)
  encoded_vk = []
  encoded_vk.append(encodeG2(g2))
  encoded_vk.append(encodeG2(g2x))
  encoded_vk.append(g1y)
  encoded_g2y = []
  for i in range(len(g2y)):
    encoded_g2y.append(encodeG2(g2y[i]))
  encoded_vk.append(encoded_g2y)
  encoded_vk.append(encodeG2(ycG))
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

def encodeVK_Alist(vk):
     vks = []
     for i in vk:
          vks.append(encodeG2(i))
     return vks
     
# params = downloadParams(args.title)
params = setup(q, args.title)

(sk, vk) = ttp_keygen(params, tv, nv)
aggregate_vk = agg_key(params, vk)
aggregate_sk = agg_key_sec(params, sk)
print("aggreg_vk")
print(aggregate_vk)
print("aggreg_sk")
print(aggregate_sk)

(sk_a, vk_a) = ttp_accumelator_keygen(params,to,no)
aggregate_vk_a = agg_key_accumulator(params, vk_a)
accumulator_private_key_shares = {}
for i in range(no):
     accumulator_private_key_shares.setdefault(i+1,sk_a[i])
print("accum_shares")
print(accumulator_private_key_shares)
encoded_vks = encodeVkList(vk)

encoded_aggregate_vk = encodeVk(aggregate_vk)

encoded_vks_a = encodeVK_Alist(vk_a)

encoded_aggregate_vk_a = encodeG2(aggregate_vk_a)

ac_path = os.path.join(root_dir, args.title)
ac_file_path = os.path.join(ac_path, "accum_secret.pickle")
f = open(ac_file_path,'wb')
pickle.dump(accumulator_private_key_shares, f)
f.close()
ac_file_path = os.path.join(ac_path, "vk.pickle")
f = open(ac_file_path,'wb')
json_vk = jsonpickle.encode(encoded_vks)
pickle.dump(json_vk, f)
f.close()

ac_file_path = os.path.join(ac_path, "aggregate_vk.pickle")
f = open(ac_file_path,'wb')
json_aggregate_vk = jsonpickle.encode(encoded_aggregate_vk)
pickle.dump(json_aggregate_vk, f)
f.close()

ac_file_path = os.path.join(ac_path, "vk_a.pickle")
f = open(ac_file_path,'wb')
json_vk = jsonpickle.encode(encoded_vks_a)
pickle.dump(json_vk, f)
f.close()

ac_file_path = os.path.join(ac_path, "aggregate_vk_a.pickle")
f = open(ac_file_path,'wb')
json_aggregate_vk = jsonpickle.encode(encoded_aggregate_vk_a)
pickle.dump(json_aggregate_vk, f)
f.close()
ac_file_path = os.path.join(ac_path, "public_params.pickle")
f = open(ac_file_path,'wb')
h = multiply(G1,genRandom())
l = [(G1[0].n,G1[1].n),encodeG2(G2),(h[0].n, h[1].n), encodeG2(multiply(G2, genRandom()))]
l = jsonpickle.encode(l)
pickle.dump(l, f)
f.close()
# -------------------------------------------------------------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
s.bind((ip, int(port)))        
print (name + " binded to %s" %(port))
s.listen(10)    
print (name +" is listening")
key_request_count = 0
while key_request_count < nv:
	try:
		c, addr = s.accept()
		validator = c.recv(8192).decode() # validator:1
		v_id = int(validator.split(":")[1])
		keys = (encoded_vks[v_id-1], sk[v_id-1])
		keysJSON = jsonpickle.encode(keys)
		c.send(keysJSON.encode())
		print("sent keys to Validator : ", str(v_id))
		key_request_count += 1
		c.close()
	except Exception as e:
		print(e)
		s.shutdown(socket.SHUT_RDWR)
		s.close()
                
key_request_count = 0
while key_request_count < no:
	try:
		c, addr = s.accept()
		opener = c.recv(8192).decode() # validator:1
		o_id = int(opener.split(":")[1])
		keys = (encoded_vks_a[o_id-1], sk_a[o_id-1])
		keysJSON = jsonpickle.encode(keys)
		c.send(keysJSON.encode())
		print("sent keys to Opener : ", str(o_id))
		key_request_count += 1
		c.close()
	except Exception as e:
		print(e)
		s.shutdown(socket.SHUT_RDWR)
		s.close()



# ---------------------------------------------------------------

organization_address = args.address

while True:
	time.sleep(10)
	vks = loadValidatorKeys(args.title)
	opks = loadOpenerKeys(args.title)
	if None in vks or None in opks:
		pass
	else:
		print("Setup is done")
		break

# -------------------------- Validators key generation  -----------------------------

_, o, g1, hs, g2, e = params	
encoded_hs = [(hs[i][0].n, hs[i][1].n) for i in range(len(hs))]
(_, alpha, g1_beta, beta, yvG)= aggregate_vk

encoded_alpha = ((alpha[0].coeffs[1].n, alpha[0].coeffs[0].n), (alpha[1].coeffs[1].n, alpha[1].coeffs[0].n))
encoded_beta = [((beta[i][0].coeffs[1].n,beta[i][0].coeffs[0].n),(beta[i][1].coeffs[1].n,beta[i][1].coeffs[0].n)) for i in range(len(beta))]
encoded_g1_beta = [(g1_beta[i][0].n, g1_beta[i][1].n) for i in range(len(g1_beta))]
encoded_opk = [[[opks[i][0].coeffs[1].n, opks[i][0].coeffs[0].n],[opks[i][1].coeffs[1].n, opks[i][1].coeffs[0].n]] for i in range(no)]

# ---------------------  setting params to contract (Params.sol) --------------------------

# validator params
#  string[][] _combinations

encoded_include_indexes = getIncludeIndexes(args.title, dependency)

combinations = getCombinations(args.title)

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

schema = downloadSchema(args.title)
schemaOrder = downloadSchemaOrder(args.title)
encoding = downloadEncoding(args.title)
public_m_encoding = []
for key in schemaOrder:
	if schema[key]['visibility'] == 'public':
		public_m_encoding.append(encoding[key])


tx_hash = params_contract.functions.set_params(args.title, encoded_hs, encoded_alpha, encoded_g1_beta, encoded_beta, encoded_opk, combinations, dependency, encoded_include_indexes, public_m_encoding).transact({'from': organization_address})
w3.eth.waitForTransactionReceipt(tx_hash)

tx_hash = acc_contract.functions.set_accumulator(no,to,nv,tv).transact({'from': organization_address})
print(tx_hash)
w3.eth.waitForTransactionReceipt(tx_hash)


opener_addresses = args.opener_addresses
validator_addresses = args.validator_addresses

for opener_addr in opener_addresses:
	tx_hash = opening_contract.functions.addOpener(opener_addr).transact({'from':organization_address})
	w3.eth.waitForTransactionReceipt(tx_hash)

for validator_addr in validator_addresses:
	tx_hash = issue_contract.functions.addIssuer(validator_addr).transact({'from':organization_address})
	w3.eth.waitForTransactionReceipt(tx_hash)