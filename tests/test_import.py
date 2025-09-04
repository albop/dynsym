from dynsym import read_model


import time

t1 = time.time()
r,A,B,C,D = read_model("tests/rbc.dyno")
t2 = time.time()

print("Time to read and compute Jacobian: ", t2-t1)