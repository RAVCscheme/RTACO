from py_ecc.bn128 import *
from py_ecc_tester import *
a = (FQ(1),FQ(2))
b = G2
c = pairing(b,a)
r = multiply(b, 3)
y = modInverse(3, curve_order)
print(y)
print(curve_order -3)
t = multiply(a,y)
h = pairing(r,t)
print(c)
print("sdfghjk")
print(add(h,c))