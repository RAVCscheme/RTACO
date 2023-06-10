from py_ecc_tester import *
import pickle
import jsonpickle

sec_shares = create_accumulator_shares(curve_order, 3,2,3,2)
kr_shares = create_accumulator_shares(curve_order,3,2,3,2)
ya = sec_shares[0]
kr = kr_shares[0]
ya_kr = ya +kr
ya_kr_inv = modInverse(ya_kr, curve_order)
r_1 = [genRandom() for i in range(len(kr_shares[1]))]
zr_inv = [modInverse(ya_kr * i% curve_order, curve_order) for i in r_1]

print("ya*kr")
print(ya*kr%curve_order)
mult = [sec_shares[1][i]*kr_shares[1][i]% curve_order for i in range(len(sec_shares[1]))]
ans = sum(mult)
print(3*ans%curve_order)


