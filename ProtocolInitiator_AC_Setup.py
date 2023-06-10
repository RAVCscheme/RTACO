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
#No address to change
# python3 ProtocolInitiator_AC_Setup.py --title "Loan Credential" --name Loaner --ip 127.0.0.1 --port 4000 --dependency "Identity Certificate" "Income Certificate"

parser = argparse.ArgumentParser(description="Anonymous Credentials registration")
parser.add_argument("--title", type=str, default = None, required = True, help= "This is the title of the Anonymous Credential.")
parser.add_argument("--name", type=str, default = None, required = True,  help= "The name of organisation giving the Anonymous Credential")
parser.add_argument("--ip", type=str, default = '127.0.0.1', required = False,  help= "The ip at which organisation is running.")
parser.add_argument("--port", type=str, default = None, required = True,  help= "The port on which organisation is running.")
parser.add_argument('--dependency', nargs='+', help='The Vcerts on which the Anonymous Credential issuance depends on.', required=False)
args = parser.parse_args()

mode = 0o777
root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"

register_path = os.path.join(root_dir, "ac_register.pickle")
# ip_map = os.path.join(root_dir, "ac_ip_map.pickle")
encoding_types = os.path.join(root_dir, "encoding_type_map.pickle")


try:
	f = open(encoding_types,'rb')
	encoding_type_map = pickle.load(f)
	f.close()
except FileNotFoundError as e:
	f = open(encoding_types,'wb') 
	encoding_type_map = {"1": type("string"), "2": type(1), "3": type(datetime.datetime.now())}
	pickle.dump(encoding_type_map, f)
	f.close()

try:
	f = open(register_path,'rb')
	RegisteredList = pickle.load(f)
	f.close()
	register = { "title":args.title, "name" : args.name, "ip" : args.ip, "port":args.port, "dependency": [] }
	if args.dependency != None:
		register = { "title":args.title, "name" : args.name, "ip" : args.ip, "port":args.port, "dependency": args.dependency }
	RegisteredList.append(register)
	f = open(register_path,'wb')
	pickle.dump(RegisteredList, f)
	f.close()
except FileNotFoundError as e:
	f = open(register_path,'wb')
	register = { "title":args.title, "name" : args.name, "ip" : args.ip, "port":args.port, "dependency": [] }
	if args.dependency != None:
		register = { "title":args.title, "name" : args.name, "ip" : args.ip, "port":args.port, "dependency": args.dependency }
	pickle.dump([register], f)
	f.close()

# try:
# 	f = open(ip_map,'rb')
# 	ip_map_table = pickle.load(f)
# 	f.close()
# 	ip_map_table.setdefault(args.title,  (args.ip, args.port))
# 	f = open(ip_map,'wb')
# 	pickle.dump(ip_map_table, f)
# 	f.close()
# except FileNotFoundError as e:
# 	f = open(ip_map,'wb')
# 	ip_map_table = { args.title : (args.ip, args.port) }
# 	pickle.dump(ip_map_table, f)
# 	f.close()

ac_path = os.path.join(root_dir, args.title)
try:
	os.mkdir(ac_path, mode = mode)
except FileExistsError as e:
	pass

schema = {}
encoding = {}
include_indexes = {}
schemaOrder = []

dependency_CA = args.dependency

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

# def downloadParams(title):
# 	ca_path = os.path.join(root_dir, title)
# 	ca_file_path = os.path.join(ca_path, "params.pickle")
# 	f = open(ca_file_path,'rb')
# 	json_params = pickle.load(f)
# 	params = jsonpickle.decode(json_params)
# 	f.close()
# 	return params

# def downloadPk(title):
# 	ca_path = os.path.join(root_dir, title)
# 	ca_file_path = os.path.join(ca_path, "pk.pickle")
# 	f = open(ca_file_path,'rb')
# 	json_pk = pickle.load(f)
# 	pk = jsonpickle.decode(json_pk)
# 	f.close()
# 	return pk

# for i in range(len(dependency_CA)):
# 	ttp_schema = downloadSchema(dependency_CA[i])
# 	ttp_schemaOrder = downloadSchemaOrder(dependency_CA[i])
# 	ttp_encoding = downloadEncoding(dependency_CA[i])
# 	include_indexes.setdefault(args.title, {})
# 	for k in ttp_schemaOrder:
# 		checker = input("Do u want to add the attribute \'"+k+"\' to "+args.title)
# 		if checker == "Y" or checker == "y":
# 			schema.setdefault(k, {"type" : ttp_schema[k]["type"], "visibility" : "private"})
# 			schemaOrder.append(k)
# 			encoding.setdefault(k, ttp_encoding[k])
# 			include_indexes[args.title].setdefault(k, 1)
# 		else:
# 			include_indexes[args.title].setdefault(k, 0)
# while True:
# 	checker = input("Do u want to add a public attribute")
# 	if checker == "Y" or checker == "y":
# 		key = input("Enter the name of the attribute : ")
# 		schemaOrder.append(key)
# 		value = input("Choose the type of the attribute string - 1, number - 2, and datetime - 3 : ")
# 		schema.setdefault(key, {"type" : encoding_type_map[value], "visibility" : "public"})
# 		encoding.setdefault(key, int(value))
# 	else:
# 		break

while True:
	checker = input("Do u want to add the private attribute to "+args.title + " : ") 
	if checker == "Y" or checker == "y":
		key = input("Enter the name of the attribute : ")
		schemaOrder.append(key)
		value = input("Choose the type of the attribute string - 1, number - 2, or datetime - 3: ")
		schema.setdefault(key, {"type" : encoding_type_map[value], "visibility": "private"})
		encoding.setdefault(key, int(value))
	else:
		break
while True:
	checker = input("Do u want to add the public attribute to "+args.title + " : ")
	if checker == "Y" or checker == "y":
		key = input("Enter the name of the attribute : ")
		schemaOrder.append(key)
		value = input("Choose the type of the attribute string - 1, number - 2, or datetime - 3: ")
		schema.setdefault(key, {"type" : encoding_type_map[value], "visibility": "public"})
		encoding.setdefault(key, int(value))
	else:
		break

combinations = []
while True:
	checker = input("Do u want to add a combination : ")
	if checker == "Y" or checker == "y":
		combination = input("Enter the CAs in order with coma seperation (no space after coma) : ").split(",")
		combinations.append(combination)
	else:
		break

# This include indexes work only for one order of attributes.
include_indexes = {}
for certifier in dependency_CA:
	ca_schemaOrder = downloadSchemaOrder(certifier)
	ca_indexes = []
	for attr in ca_schemaOrder:
		value = input("Is the private attribute \'"+attr+ "\' is included in " + args.title +" : ")
		if value == "Y" or value == 'y':
			ca_indexes.append(1)
		else:
			ca_indexes.append(0)
	include_indexes.setdefault(certifier, ca_indexes)
			

ac_file_path = os.path.join(ac_path, "combinations.pickle")
f = open(ac_file_path,'wb')
pickle.dump(combinations, f)
f.close()

q = len(schemaOrder)

ac_file_path = os.path.join(ac_path, "schema.pickle")
f = open(ac_file_path,'wb')
pickle.dump(schema, f)
f.close()
ac_file_path = os.path.join(ac_path, "encoding.pickle")
f = open(ac_file_path,'wb')
pickle.dump(encoding, f)
f.close()
ac_file_path = os.path.join(ac_path, "schemaOrder.pickle")
f = open(ac_file_path,'wb')
pickle.dump(schemaOrder, f)
f.close()
ac_file_path = os.path.join(ac_path, "include_indexes.pickle")
f = open(ac_file_path,'wb')
pickle.dump(include_indexes, f)
f.close()

nv = int(input("Total number of validators in "+ args.title + " : "))
tv = int(input("Threshold parameter for validators in "+ args.title + " : "))

no = int(input("Total number of openers in "+ args.title + " : "))
to = int(input("Threshold parameter for openers in "+ args.title + " : "))

params = setup(q, args.title) # does not include sk_u.

ac_file_path = os.path.join(ac_path, "q.pickle")
f = open(ac_file_path,'wb')
pickle.dump(q, f)
f.close()
ac_file_path = os.path.join(ac_path, "nv.pickle")
f = open(ac_file_path,'wb')
pickle.dump(nv, f)
f.close()
ac_file_path = os.path.join(ac_path, "tv.pickle")
f = open(ac_file_path,'wb')
pickle.dump(tv, f)
f.close()
ac_file_path = os.path.join(ac_path, "no.pickle")
f = open(ac_file_path,'wb')
pickle.dump(no, f)
f.close()
ac_file_path = os.path.join(ac_path, "to.pickle")
f = open(ac_file_path,'wb')
pickle.dump(to, f)
f.close()
# ac_file_path = os.path.join(ac_path, "params.pickle") 
# f = open(ac_file_path,'wb')
# json_params = jsonpickle.encode(params)
# pickle.dump(json_params, f)
# f.close()
ac_file_path = os.path.join(ac_path, "validatorKeys.pickle")
f = open(ac_file_path,'wb')
vks = [None] * nv
json_pk = jsonpickle.encode(vks)
pickle.dump(json_pk, f)
f.close()
ac_file_path = os.path.join(ac_path, "openerKeys.pickle")
f = open(ac_file_path,'wb')
opk = [None] * no
json_pk = jsonpickle.encode(opk)
pickle.dump(json_pk, f)
f.close()
ac_file_path = os.path.join(ac_path, "AccumelatorKeys.pickle")
f = open(ac_file_path,'wb')
opk = [None] * no
json_pk = jsonpickle.encode(opk)
pickle.dump(json_pk, f)
f.close()
ac_file_path = os.path.join(ac_path, "opener_ip_map.pickle")
f = open(ac_file_path,'wb')
ips = [None] * no
pickle.dump(ips, f)
f.close()
ac_file_path = os.path.join(ac_path, "openersList.pickle")
f = open(ac_file_path,'wb')
pickle.dump([], f)
f.close()
ac_file_path = os.path.join(ac_path, "validatorsList.pickle")
f = open(ac_file_path,'wb')
pickle.dump([], f)
f.close()
