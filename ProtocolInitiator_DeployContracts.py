import argparse
import os
import pickle
#change all address
# python3 ProtocolInitiator_DeployContracts.py --params-address 0x5821cf75FA4907D020feE0614af796e01c5a9C6b --request-address 0xeD2207ff1147e10eebd22d7B8b718178D2aa7eD5 --issue-address 0x4b3b9558EdaFc1fBb60C9418952fa1eda4C33483 --opening-address 0xc22e42015915a88048c3F66c69bc60a4fF1DAd30


parser = argparse.ArgumentParser(description="Smart Contracts Deployment")
# parser.add_argument("--address", type=str, default = None, required = True,  help= "The blockchain address on which Protocol Initiator is running.")
parser.add_argument("--params-address", type=str, default = None, required = True,  help= "The blockchain address at which params contract is deployed.")
parser.add_argument("--request-address", type=str, default = None, required = True,  help= "The blockchain address at which request contract is deployed.")
parser.add_argument("--issue-address", type=str, default = None, required = True,  help= "The blockchain address at which issue contract is deployed.")
parser.add_argument("--opening-address", type=str, default = None, required = True,  help= "The blockchain address at which opening contract is deployed.")
parser.add_argument("--accumulator-address", type=str, default = None, required = True,  help= "The blockchain address at which accumulator contract is deployed.")
# parser.add_argument("--rpc-endpoint", type=str, default = None, required = True,  help= "The node rpc endpoint through which a client is connected to blockchain network.")
args = parser.parse_args()

mode = 0o777
root_dir = "/home/neel/acad/DTRAC/ravc-main/ROOT"
try:
	os.mkdir(root_dir, mode = mode)
except FileExistsError as e:
	pass

def uploadAddresses(address, filename):
	file_path = os.path.join(root_dir, filename)
	f = open(file_path,'wb')
	pickle.dump(address, f)
	f.close()

#print(args.params_address)
#print("Displaying Output as: % s" % args.params_address)
uploadAddresses(args.params_address, "params_address.pickle")
uploadAddresses(args.request_address, "request_address.pickle")
uploadAddresses(args.issue_address, "issue_address.pickle")
uploadAddresses(args.opening_address, "opening_address.pickle")
uploadAddresses(args.accumulator_address, "accumulator_address.pickle")