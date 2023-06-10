from operator import truediv
import jsonpickle
import json
from TTP import *

import datetime
import time

import argparse
import os
import sys
import pickle
import socket
import threading

# python3 AttributeCertifier.py --title "Identity Certificate" --name IdP --req-ip 127.0.0.1 --req-port 3001  --open-ip 127.0.0.1 --open-port 7001
# python3 AttributeCertifier.py --title "Income Certificate" --name Employer --req-ip 127.0.0.1 --req-port 3002  --open-ip 127.0.0.1 --open-port 7002 --dependency "Identity Certificate"

parser = argparse.ArgumentParser(description="Attribute Certifier Creation")
parser.add_argument("--title", type=str, default = None, required = True, help= "This is the title of the Verifiable Certificate.")
parser.add_argument("--name", type=str, default = None, required = True,  help= "The name of provider giving the Verifiable Certificate")
parser.add_argument("--req-ip", type=str, default = '127.0.0.1', required = False,  help= "The ip at which Attribute Certifier is running for Vcert request.")
parser.add_argument("--req-port", type=str, default = None, required = True,  help= "The port on which Attribute Certifier is running for Vcert request.")
parser.add_argument("--open-ip", type=str, default = '127.0.0.1', required = False,  help= "The ip at which Attribute Certifier is running for opener's request.")
parser.add_argument("--open-port", type=str, default = None, required = True,  help= "The port on which Attribute Certifier is running for opener's request.")
parser.add_argument('--dependency', nargs='+', help='The Vcerts on which the current Vcert issuance depends on.', required=False)
args = parser.parse_args()

mode = 0o777
root_dir = "/home/vinay/Downloads/ModifierVersionGanache/ROOT"

try:
	os.mkdir(root_dir, mode = mode)
except FileExistsError as e:
	pass

register_path = os.path.join(root_dir, "ca_register.pickle")
# req_ip_map = os.path.join(root_dir, "ca_req_ip_map.pickle")
# open_ip_map = os.path.join(root_dir, "ca_open_ip_map.pickle")
encoding_types = os.path.join(root_dir, "encoding_type_map.pickle")

try:
	f = open(register_path,'rb')
	RegisteredList = pickle.load(f)
	f.close()
	register = { "title":args.title, "name" : args.name, "req-ip" : args.req_ip, "req-port":args.req_port, "open-ip" : args.open_ip, "open-port":args.open_port, "dependency": [] }
	if args.dependency != None:
		register = { "title":args.title, "name" : args.name, "req-ip" : args.req_ip, "req-port":args.req_port, "open-ip" : args.open_ip, "open-port":args.open_port, "dependency": args.dependency }
	RegisteredList.append(register)
	f = open(register_path,'wb')
	pickle.dump(RegisteredList, f)
	f.close()
except FileNotFoundError as e:
	f = open(register_path,'wb')
	register = { "title":args.title, "name" : args.name, "req-ip" : args.req_ip, "req-port":args.req_port, "open-ip" : args.open_ip, "open-port":args.open_port, "dependency": [] }
	if args.dependency != None:
		register = { "title":args.title, "name" : args.name, "req-ip" : args.req_ip, "req-port":args.req_port, "open-ip" : args.open_ip, "open-port":args.open_port, "dependency": args.dependency }
	pickle.dump([register], f)
	f.close()
	
# try:
# 	f = open(req_ip_map,'rb')
# 	req_ip_map_table = pickle.load(f)
# 	f.close()
# 	req_ip_map_table.setdefault(args.title, (args.req_ip, args.req_port))
# 	f = open(req_ip_map,'wb')
# 	pickle.dump(req_ip_map_table, f)
# 	f.close()
# except FileNotFoundError as e:
# 	f = open(req_ip_map,'wb')
# 	req_ip_map_table = { args.title : (args.req_ip, args.req_port) }
# 	pickle.dump(req_ip_map_table, f)
# 	f.close()

# try:
# 	f = open(open_ip_map,'rb')
# 	open_ip_map_table = pickle.load(f)
# 	f.close()
# 	open_ip_map_table.setdefault(args.title, (args.open_ip, args.open_port))
# 	f = open(open_ip_map,'wb')
# 	pickle.dump(open_ip_map_table, f)
# 	f.close()
# except FileNotFoundError as e:
# 	f = open(open_ip_map,'wb')
# 	open_ip_map_table = { args.title : (args.open_ip, args.open_port) }
# 	pickle.dump(open_ip_map_table, f)
# 	f.close()

try:
	f = open(encoding_types,'rb')
	encoding_type_map = pickle.load(f)
	f.close()
except FileNotFoundError as e:
	f = open(encoding_types,'wb')
	encoding_type_map = {"1": type("string"), "2": type(1), "3": type(datetime.datetime.now())}
	pickle.dump(encoding_type_map, f)
	f.close()

# define schema. schema includes secret master key.
schema = {}
encoding = {}
schemaOrder = []

key = "msk"
schemaOrder.append(key)
schema.setdefault(key, {"type" : encoding_type_map["2"], "visibility": "private"})
encoding.setdefault(key, 2)
print("The first attribute of " + args.title +" is secret master key (msk)")

while True:
	checker = input("Do u want to add the private attribute to "+args.title + " : ")
	if checker == "Y" or checker == "y":
		key = input("Enter the name of the attribute : ")
		schemaOrder.append(key)
		value = input("Choose the type of the attribute string - 1, number - 2, and datetime - 3 : ")
		schema.setdefault(key, {"type" : encoding_type_map[value], "visibility": "private"})
		encoding.setdefault(key, int(value))
	else:
		break
while True:
	checker = input("Do u want to add the public attribute to "+args.title + " : ")
	if checker == "Y" or checker == "y":
		key = input("Enter the name of the attribute : ")
		schemaOrder.append(key)
		value = input("Choose the type of the attribute string - 1, number - 2, and datetime - 3: ")
		schema.setdefault(key, {"type" : encoding_type_map[value], "visibility": "public"})
		encoding.setdefault(key, int(value))
	else:
		break

key = "r"
schemaOrder.append(key)
schema.setdefault(key, {"type" : encoding_type_map["2"], "visibility": "private"})
encoding.setdefault(key, 2)
print("The last attribute of " + args.title +" is a blinding factor (r)")

ca_path = os.path.join(root_dir, args.title)
try:
	os.mkdir(ca_path, mode = mode)
except FileExistsError as e:
	pass

ca_file_path = os.path.join(ca_path, "schema.pickle")
f = open(ca_file_path,'wb')
pickle.dump(schema, f)
f.close()
ca_file_path = os.path.join(ca_path, "encoding.pickle")
f = open(ca_file_path,'wb')
pickle.dump(encoding, f)
f.close()
ca_file_path = os.path.join(ca_path, "schemaOrder.pickle")
f = open(ca_file_path,'wb')
pickle.dump(schemaOrder, f)
f.close()

q = len(schemaOrder)

#public params generation.
params = ttp_setup(q-1, args.title) # exclude r.
ca_file_path = os.path.join(ca_path, "params.pickle")
f = open(ca_file_path,'wb')
json_params = jsonpickle.encode(params)
pickle.dump(json_params, f)
f.close()

# pub - priv key pair generation.
pk, sk = ttpKeyGen(params)
ca_file_path = os.path.join(ca_path, "pk.pickle")
f = open(ca_file_path,'wb')
json_pk = jsonpickle.encode(pk)
pickle.dump(json_pk, f)
f.close()

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

def downloadPrevPublicInformation(title):
	return (downloadParams(title), downloadPk(title))

def updatePreviousCAInformation(dependency_CA):
	prevParams, prevPks = [], []
	if dependency_CA == None:
		return ([], [])
	for i in range(len(dependency_CA)):
		title = dependency_CA[i]
		params, pk = downloadPrevPublicInformation(title)
		prevParams.append(params)
		prevPks.append(pk)
	return (prevParams, prevPks)

# fixed order and one should follow this order.
combinations = []
while True:
	checker = input("Do u want to add a combination : ")
	if checker == "Y" or checker == "y":
		combination = input("Enter the CAs in order with coma seperation (no space after coma) : ").split(",")
		combinations.append(combination)
	else:
		break

def checkCombination(combination):
	for i in range(len(combinations)):
		if len(combinations[i]) == len(combination):
			j = 0
			while j < len(combination):
				if combinations[i][j] != combination[j]:
					break
				j += 1
			if j == len(combination):
				return True
	return False

dependency_CA = args.dependency
prevParams, prevPks = updatePreviousCAInformation(dependency_CA) # use combination to get those prev_params

served_count = 0
pending_requests = []
served_requests = []
pending_requests_lock = threading.Lock()  # pending_requests list act as producer and consumer.
event_object = threading.Event() # if there is one request in pending_requests it will notify serve_requests.
event_object_lock = threading.Lock() # this lock helps while working with event_object event.

def listen_to_requests(name, ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	s.bind((ip, int(port)))        
	print (name + " binded to %s  for Certificate Requests" %(port))
	s.listen(10)    
	print (name +" is listening for Certificate requests")
	while True:
		try:
			c, addr = s.accept()
			requestJSON = c.recv(8192).decode()
			(prevCombination, prevVcerts, attributes, commit, zkpok, user_ip, user_port) = jsonpickle.decode(requestJSON)
			if not checkCombination(prevCombination):
				continue
			event_object_lock.acquire()
			pending_requests_lock.acquire()
			pending_requests.append((prevCombination, prevVcerts, attributes, commit, zkpok, user_ip, user_port))
			pending_requests_lock.release()
			event_object.set()
			event_object_lock.release()
			c.close()
		except Exception as e:
			print(e)
			s.shutdown(socket.SHUT_RDWR)
			s.close()

def serve_requests():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	while True:
		event_object.wait()
		pending_requests_lock.acquire()
		(_, prevVcerts, attributes, commit, zkpok, user_ip, user_port) = pending_requests[served_count]
		pending_requests_lock.release()
		s.connect(user_ip, int(user_port))

		for i in range(len(prevVcerts)):
			if not VerifyVcerts(prevParams[i], prevPks[i], prevVcerts[i][1], SHA256(prevVcerts[i][0])):
				served_count += 1
				event_object_lock.acquire()
				if served_count == len(pending_requests):
					event_object.clear()
				event_object_lock.release()
				continue

		attribute = []
		encode_str = []
		for key in schemaOrder[1:len(schemaOrder)-1]:
			attribute.append(attributes[key])
			encode_str.append(encoding[key])
		encoded_attribute = encode_attributes(attribute, encode_str)
		result  = VerifyZKPoK(params, prevParams, prevVcerts, encoded_attribute, commit, zkpok)
		if result == False:
			s.send("Vcert Reqeust Failed".encode())
		else:
			print("User with ")
			for key in schemaOrder[1:len(schemaOrder)-1]:
				print(key, " : ", attributes[key])
			print("has requested Verifiable Certificate.")
			checker = input("Do you want to issue ?")
			if checker == "Y" or checker == "y":
				signature = SignCommitment(params, sk, commit)
				issueVcert = (commit, signature)
				issueVcertJSON = jsonpickle.encode(issueVcert)
				s.send(issueVcertJSON.encode())
				served_requests.append((commit, signature, attributes))
			else:
				s.send("CA refused to issue the verifiable certificate.".encode())
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		served_count += 1
		event_object_lock.acquire()
		if served_count == len(pending_requests):
			event_object.clear()
		event_object_lock.release()

def findUser(served_requests, vcert):
	for request in served_requests:
		commit, signature, attributes = request
		if commit[0].n == vcert[0][0].n and commit[1].n == vcert[0][1].n and signature[0] == vcert[1][0] and signature[1] == vcert[1][1]:
			return attributes
	return None


def open_requests(name, ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	s.bind((ip, int(port)))        
	print (name + " binded to %s for opener requests" %(port))
	s.listen(10)    
	print (name +" is listening for open requests")
	while True:
		try:
			c, addr = s.accept()
			openJSON = c.recv(8192).decode()
			vcert = jsonpickle.decode(openJSON)
			checker = input("Do you want to disclose user information ?")
			if checker == "y" or checker == "Y":
				attributes = findUser(served_requests, vcert)
			else:
				attributes = None
			attributesJSON = jsonpickle.encode(attributes)
			c.send(attributesJSON.encode())
			c.close()
		except Exception as e:
			print(e)
			s.shutdown(socket.SHUT_RDWR)
			s.close()

listen_thread = threading.Thread(target = listen_to_requests, args = (args.name, args.req_ip, args.req_port))
serve_thread  = threading.Thread(target = serve_requests)
open_thread = threading.Thread(target = open_requests, args = (args.name, args.open_ip, args.open_port))

listen_thread.start()
serve_thread.start()
open_thread.start()

