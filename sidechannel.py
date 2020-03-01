#!/usr/bin/env python3

import requests
import pickle

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
        print("Got short tuple, {}".format(r))
        continue
    pt, ct, time = r
    if i == 1:
        print(len(pt), len(ct))
        print(pt)
        print(ct)
        print(time)
    times_sum += float(time)
    tuples[i] = (pt, ct, time)
    n += 1

times_mean = times_sum / n

print("Times mean", times_mean)

delayed = 0
for t in tuples:
    if len(t) != 3 or type(t) == str:
        print(t)
        print("T HAS WRONG LENGTH YOu fUcKInG IDIIOT")
        continue
    pt, ct, time = t
    pt = pt.replace("\n","")
    pt = pt.split(" ")
    pt = list(filter(lambda x: x != '', pt))
    if float(time) > times_mean:
        delayed += 1

        for i in range(16):

            b = int(pt[i], 16)
            # print("pt is {} and has type {}".format(pt, type(pt)))
            # print(type(pt[i]))
            for j in range(8):
                # each bit of means is taking only one bit from the byte represented by pt
                bitwise_res = ((b >> j) ^ 1) & 1
                means[8 * i + j] += int(bitwise_res)
    else:
        for i in range(16):
            b = int(pt[i], 16)
            # print("pt is {} and has type {}".format(pt, type(pt)))
            # print(type(pt[i]))
            for j in range(8):
                # each bit of means is taking only one bit from the byte represented by pt
                bitwise_res = ((b >> j) ^ 1) & 1
                not_means[8 * i + j] += int(bitwise_res)


print("There were {} delayed encryptions".format(delayed))
print("n is {} means are {}".format(n,means))
# divide sums to get means
for i in range(128):
    means[i] = means[i] / (not_means[i] + means[i])

print(means)
print(''.join(map(str,means)))
