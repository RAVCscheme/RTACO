import json
from web3 import Web3
import os
from py_ecc_tester import *
import pickle
import jsonpickle

print(G1)
sec_shares = create_accumulator_shares(curve_order, 3,2,3,2)
kr_shares = create_accumulator_shares(curve_order,3,2,3,2)
ya = sec_shares[0]
kr = kr_shares[0]
ans1 = multiply(G1,(ya+kr)%curve_order)
print("ans1")
print(ans1)
opner_ya_shares = sec_shares[1]
opner_kr_shares = kr_shares[1]
a = [multiply(G1,(opner_ya_shares[i] + opner_kr_shares[i])) for i in range(len(opner_kr_shares))]
params = (0,curve_order,0,0,0,0)
ans2 = agg_key_accumulator(params, a)
print("ans2")
print(ans2)