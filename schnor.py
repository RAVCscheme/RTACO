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

kr1 = 4874496416515046213763525970492968123042418842331640680719648767045975360027
# kr2 = random.randint(2, curve_order)
# kr3 = random.randint(2, curve_order)
ya = 18037786433369617983613241431103676809489016113774013085983191952038737594346
print("kr1 = " ,kr1)

delta = multiply(G1,(ya+kr1)%curve_order)
print("delta = ", delta)
W1 = multiply(delta, modInverse((ya+kr1)%curve_order, curve_order))
print("W1 = " ,W1)

h2 = multiply(G2,random.randint(2, curve_order))
g = multiply(G1,random.randint(2, curve_order))
pp = [G1, G2, h2,g]

tau1 = random.randint(2, curve_order)
tau2 = random.randint(2, curve_order)
print("tau1 = ", tau1)
pie_I_1 = add(multiply(G1,tau1), multiply(g, tau2))
print("pi_i_1 = ", pie_I_1)

pie_I_2 = add(W1, multiply(g,tau1))
r = random.randint(2, curve_order)
r_r = random.randint(2, curve_order)
r_tau_1 = random.randint(2, curve_order)
print("tau1 = ", r_tau_1)
r_tau_2 = random.randint(2, curve_order)
r_delta_1 = random.randint(2, curve_order)
r_delta_2 = random.randint(2, curve_order)
commit = add(multiply(h2, r), multiply(G2,kr1))
a = ((20714125610476264572248139578798647176232379163906792757131192708982371082177, 19358198519371450433306546655692202203144701372655683916970449011484293515601), (14945050140401705244036412705676334334067341595735047740014909399066818264531, 7158868001394208171836152559021570010923019186195479903828146792664772600721))
pub = (FQ2([a[0][0], a[0][1]]),FQ2([a[1][0], a[1][1]]))
print("pub")
print(pub)
print(multiply(G2,ya))
CI = add(commit, pub)
delta_1 = (r*tau1)%curve_order
delta_2 = (r*tau2)%curve_order
R1 = add(multiply(G1, r_tau_1), multiply(g,r_tau_2))
print("R1 = ", R1)
R2 = add(add(multiply(pie_I_1, r_r),multiply(G1, (r_delta_1*(-1))%curve_order)),multiply(g, (r_delta_2*(-1))%curve_order))
R3 = (pairing(CI, multiply(g, r_tau_1))) * (pairing(h2, multiply(g,(-1*r_delta_1)%curve_order))) * (pairing(h2, multiply(pie_I_2, r_r)))

c = random.randint(2, curve_order)
s_r = (r_r + (c*r))%curve_order
s_tau_1 = (r_tau_1 + (c*tau1))%curve_order
s_tau_2 = (r_tau_2 + (c*tau2))%curve_order
s_delta_1 = (r_delta_1 + (c*delta_1))%curve_order
s_delta_2 = (r_delta_2 + (c*delta_2))%curve_order

# # #verifier checks
inv = modInverse(c,curve_order)
ans1 = add(add(multiply(pie_I_1, (c*(-1))%curve_order), multiply(G1, s_tau_1)), multiply(g,s_tau_2))
#ans1 = add(add(multiply(pie_I_1, (c*(-1))%curve_order), multiply(G1, s_tau_1)), multiply(g, s_tau_2))
print(ans1 == R1)
ans2 = add(add(multiply(pie_I_1, s_r), multiply(G1, (s_delta_1*(-1))%curve_order)), multiply(g,(s_delta_2*(-1))%curve_order))
print(ans2 == R2)
ans3 = R3 * (pairing(CI, multiply(pie_I_2,c)))
ans4 = (pairing(CI,multiply(g, s_tau_1))) * (pairing(h2, multiply(g, ((-1)*s_delta_1)%curve_order))) *(pairing(h2,multiply(pie_I_2, s_r))) * (pairing(G2, multiply(delta, c)))

print("ans3 = ", ans3)
print("ans4 = ", ans4)
print(ans3==ans4)
