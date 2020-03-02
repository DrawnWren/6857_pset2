#!/usr/bin/env python3
from os import urandom
import requests
import pickle
from aes import AES

aes = AES()

URL = "https://courses.csail.mit.edu/6.857/2020/6857_aes.php"
payload = {"num": "1000"}

more = False

if more:
    res = requests.get(url=URL, params=payload)
    tuples = res.text.split(";")
    f = open("save.p", "rb")
    print("{} new tuples".format(len(tuples)))
    old_tuples = pickle.load(f)
    old_tuples.extend(tuples)
    tuples = old_tuples
    print("{} total tuples ".format(len(tuples)))
    f.close()
    f = open("save.p", "wb")
    pickle.dump(tuples, f)
    f.close()
else:
    tuples = pickle.load(open("save.p", "rb"))




means = [0 for i in range(128)]
not_means = [0 for i in range(128)]
times_sum = 0
n = 0
for i in range(len(tuples)):
    s = tuples[i]
    r = s.split(",")
    if len(r) != 3:
        continue
    pt, ct, time = r
    times_sum += float(time)
    tuples[i] = (pt, ct, time)
    n += 1

times_mean = times_sum / n

print("Times mean", times_mean)
print(tuples[0])

# string of space delimited ints to a list of ints
def to_bytes(s):
    s = s.replace("\n", "")
    ct_bytes = filter(lambda x: x != "", s.split(" "))
    ct_bytes = map(int, ct_bytes)
    ct_bytes = list(ct_bytes)
    return ct_bytes


delayed = 0
for t in tuples:
    if len(t) != 3 or type(t) == str:
        continue
    pt, _, time = t
    pt = to_bytes(pt)
    if float(time) > times_mean:
        delayed += 1
        for i in range(16):
            for j in range(8):
                # each element of means is taking only one bit from the byte represented by pt
                bitwise_res = ((pt[i] >> j) ^ 1) & 1
                means[8 * i + j] += int(bitwise_res)
    else:
        for i in range(16):
            for j in range(8):
                bitwise_res = ((pt[i] >> j) ^ 1) & 1
                not_means[8 * i + j] += int(bitwise_res)


print("There were {} delayed encryptions".format(delayed))
# divide sums to get means
min = 1
max = 0
for i in range(128):
    means[i] = means[i] / (not_means[i] + means[i])
    if means[i] < min:
        min = means[i]
    if means[i] > max:
        max = means[i]

print("Min and max are {}, {}".format(min, max))
m_m = sum(means) / len(means)
print("Mean is {}".format(m_m))

print(means)
for i in range(128):
    if means[i] > m_m:
        means[i] = 1
    else:
        means[i] = 0

print("".join(map(str, means)))

bytes = [0 for i in range(16)]
for i in range(16):
    bytes[i] = int("".join(map(str, means[8 * i : 8 * i + 8])), 2)

print("Guessing key {}".format(bytes))

# testing function
def serialize_and_deserialize(t):
    m,cipher,_ = t
    pt = " ".join(map(str, m))
    ct = " ".join(map(str, cipher))
    return (to_bytes(pt), to_bytes(ct), 0)

for (pt, ct, _) in tuples:
    pt = to_bytes(pt)
    ct = to_bytes(ct)

    test = False

    # to test the functionality of my comparations
    if test:
        m = list(urandom(16))
        cipher = aes.encrypt(m, bytes, 16)
        pt,ct, _ = serialize_and_deserialize((m,cipher,0))

    if len(pt) != len(ct):
        print("Length of messages does not match")

    res = aes.decrypt(ct, bytes, 16)
    if pt != res:
        print("Got {} instead of {}".format(res, pt))
        break

    if test:
        print("Test passed")
        break
