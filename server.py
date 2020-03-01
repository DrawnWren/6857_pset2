from flask import abort, Flask, request
from os import urandom
from aes import AES
from time import time, sleep
import atexit

# key is represented as a list of 16 byte ints
key = list(urandom(16))

print(key)

aes = AES()

app = Flask(__name__)

@app.route("/")
def application():
	num = request.args.get('num', '')
	try:
		num = int(num)
	except ValueError:
		abort(400)
	if (num > 10000  or num < 0):
		abort(400)

	output = ""
	for i in range(num):
		start = time()
		m = list(urandom(16))
		aes.clearOnesCount()
		cipher = aes.encrypt(m, key, 16)
		#delay simulated here, not necessarily the same delay as the one on the server
		if(int(aes.getOnesCount()) > 11*128/2):
			sleep(0.004)
		output += " ".join(map(str, m)) + ", " + " ".join(map(str, cipher))+", "+ str(time() - start) +"; \n"
	#timings on local may or may not match the timing on the actual server
	return output

if __name__ == '__main__':
	app.run(port=3000, threaded=False)
