from py_ecc_tester import *

ab = setup(9,"jsgdcjs")

# kr,so, sv = create_accumulator_shares(ab[1],10,7,4,3)
# print(so)
# print(sv)
# op = [None,None,None,None,None,None,3,0,0,0]
# filter = [so[i] for i in range(len(op)) if op[i] is not None]
# va = [None,14,2,4,None,None,None]
# filter2 = [sv[i] for i in range(len(va)) if va[i] is not None]
# indexeso = [i+1 for i in range(len(op)) if op[i] is not None]
# print(indexeso)
# indexesv = [i+1 for i in range(len(va)) if va[i] is not None]
# print(indexesv)
# l = lagrange_basis(indexeso,ab[1])
# print(len(l))
# l2 = lagrange_basis(indexesv,ab[1])
# print(len(l2))
# aggr_sec = 0
# aggr_sec2 = 0
# for i in range(len(indexeso)):
#     aggr_sec +=((filter[i]*l[i]) % ab[1])
# for i in range(len(indexesv)):
#     aggr_sec2 +=((filter2[i]*l2[i]) % ab[1])
# print(aggr_sec % ab[1])
# print(aggr_sec2 % ab[1])
sk = [1568188583147293945235648135932167259990358308122301426132586479017667884300,1532268110407581890559814942281806861559192473574235800132686942752909638330 , 1496347637667869835883981748631446463128026639026170174132787406488151392360]
sk2 = [7554896717864573679825019737652604914915463461692234745804107295963423077920, 13505684379842141359738558145722682171409402780714102439475728576644420025570,19456472041819709039652096553792759427903342099735970133147349857325416973220]
op = [0,0,0]
filter = [sk[i] for i in range(len(op)) if op[i] is not None]
indexeso = [i+1 for i in range(len(op)) if op[i] is not None]
print(sk)
l = lagrange_basis(indexeso,ab[1])
print("l")
print(l)
aggr_sec = 0
for i in range(len(indexeso)):
    aggr_sec +=((filter[i]*l[i]) % ab[1])
print(aggr_sec%ab[1])

op = [0,0,0]
filter = [sk2[i] for i in range(len(op)) if op[i] is not None]
indexeso = [i+1 for i in range(len(op)) if op[i] is not None]
print(sk2)
l = lagrange_basis(indexeso,ab[1])
print("l")
print(l)
aggr_sec = 0
for i in range(len(indexeso)):
    aggr_sec +=((filter[i]*l[i]) % ab[1])
print(aggr_sec%ab[1])