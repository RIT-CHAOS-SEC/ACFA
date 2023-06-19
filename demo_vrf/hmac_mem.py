import hmac
import hashlib

def format_pmem(barray):
	# print(barray[:32])

	# convert hex char to int
	for i in range(0, len(barray)):
		try:
			barray[i] = int(barray[i])
		except ValueError:
			barray[i] = ord(barray[i])-55
	# print(barray[:32])

	# swap half-byte endianess
	for i in range(0, len(barray), 4):
		tmp = barray[i:(i+2)]
		barray[i:(i+2)] = barray[(i+2):(i+4)]
		barray[(i+2):(i+4)] = tmp
	# print(barray[:32])

	# convert to list of 8-bit vals
	tmp = []
	for i in range(0, len(barray), 2):
		tmp.append(barray[i]*16+barray[i+1])
	barray = tmp
	# print(barray[:16])

	# convert list of bytes to bytes
	
	for i in range(0, len(barray)):
		barray[i] = (barray[i]).to_bytes(1,byteorder='big')
	# print(barray[:16])
	barray = b''.join(barray)

	return barray

def read_mem(filepath):
	# returns list of 4-bit vals
	out = []
	with open(filepath, 'r') as fp:
		lines = fp.readlines()
		for line in lines:
			if '@' not in line:
				continue
			mem = line.split()
			for i in range(1, len(mem)):
				out.extend(mem[i])
	return out


def hmac_mem(key, att_size):
	pmem = read_mem('../msp_bin/pmem.mem')
	pmem = format_pmem(pmem)
	att_mem = pmem[:att_size]
	# print("expected (att_mem): "+str(att_mem[:16]))
	resp = hmac.new(key, msg=att_mem, digestmod=hashlib.sha256).digest()

	# print("hmac(pmem, k) = "+str(resp))
	return resp


if __name__ == '__main__':
	## Test example
	key = []
	for i in range(0, 32):
		key.append(b'\x00')
	key = b''.join(key)

	resp = hmac_mem(key, 0x1fff)

	prv_resp = b'UB \x015\xd0\x08Z\x82E\n\x181@\x00h'
	print(prv_resp)
	print(resp)
	print("--------------------------")
	for i in range(0, 16):
		print(str(prv_resp[i].to_bytes(1,byteorder='big'))+"    "+str(resp[i].to_bytes(1,byteorder='big')))
	print("--------------------------")
	for i in range(0, 16):
		print(str(prv_resp[i])+"    "+str(resp[i]))