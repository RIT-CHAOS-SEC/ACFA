import serial
import time
import hmac
import hashlib
# import random
# import csv
from parse_cflog import *
from hmac_mem import *
from verify import *

#----------------- Main Script ----------------#

##### UART / SERIAL PORT CONFIGURATION

## Modify based on your machine & connection
dev = '/dev/ttyUSB1' ## ubuntu syntax
# dev = 'COM4'		 ## windows syntax
## BAUD Rate USB-UART
baud = 9600
## serial python objcet
ser = serial.Serial(dev, baud, timeout=0.5)

## Setup initiaal 
chal_size = 32
challenge = get_init_challenge(chal_size)

challenge = [x.to_bytes(1,byteorder='big') for x in challenge]
challenge = b''.join(challenge)

METADATA_SIZE = 6
#####

key_size = 32

key = [0,0,0,0,0,0,0,0,
       0,0,0,0,0,0,0,0,
       0,0,0,0,0,0,0,0,
       0,0,0,0,0,0,0,0]
key = [x.to_bytes(1,byteorder='big') for x in key]
key = b''.join(key)

## Start of AER. equals e000 if attesting PMEM
aermin = b'\xe0\x00'
## End of AER. equals addr of acfa_exit if attesting PMEM
aermax = b'\xe2\x4a'

## internal variables
max_log_size = 256
sim_idx = 0
report_num = 0
last = 0

## Timing variables
total_time = 0
runtime_rounds = []

## expected cflog start address
cflog_start_addr = "0xe03e"

print(" ")
print(header)
print(" ")
print("-------- To begin, press \"Program device\" in Vivado")
print("======================================================================")
print(" ")

debugfile = open('prot.log', 'w')
app = 1
while last == 0 and app == 1:
	print("---- Iteration "+str(report_num)+" ----", file=debugfile)
	print("cur chal: "+str(challenge), file=debugfile)

	print("Waiting \'for\' prv")
	ackByte = b'\x61'
	readyByte = b'\x00'
	echo = b'\xff'
	
	readyByte = ser.read()

	while readyByte != ackByte:	
		readyByte = ser.read()
		print(readyByte)
	ser.write(ackByte)

	print(" ")
	print("======================================================================")
	print(printIter[report_num%4])
	# print("")

	#######-----------------------------------------
	####### STEPS 1-3
	start = time.perf_counter()
	## Read Attestation Response (3)
	print("", file=debugfile)
	print("---- (3) Reading ACFA Report from Prv ----", file=debugfile)
	# Get MAC
	prv_mac = ser.read(32)
	print("prv_mac: "+str(prv_mac)+" ("+str(type(prv_mac))+")", file=debugfile)
	# Get metadata
	prv_meta = ser.read(METADATA_SIZE)
	print("prv_meta: "+str(prv_meta)+" ("+str(type(prv_meta))+")", file=debugfile)
	# extract log_ptr from metadata
	prv_log_ptr_data = prv_meta[METADATA_SIZE-2:]
	prv_log_ptr = 256*prv_log_ptr_data[1]+prv_log_ptr_data[0]

	# update local metadata with log_ptr
	metadata = []
	for i in range(0, METADATA_SIZE):
		metadata.append(prv_meta[i])
	print("metadata: "+str([x.to_bytes(1, byteorder="big") for x in metadata]), file=debugfile)
	print("prv_log_ptr: "+str(prv_log_ptr)+" ("+str(type(prv_log_ptr))+")", file=debugfile)

	# Get cflog
	## use log pointer value from metadata to read cflog
	log_size = prv_log_ptr*2
	# log_size = max_log_size
	prv_cflog = ser.read(log_size)
	# format_cflog = prv_cflog[10:]+prv_cflog[:10]
	print("prv_cflog: "+str(prv_cflog)+" ("+str(type(prv_cflog))+")", file=debugfile)
	print(log_size, file=debugfile)
	print(len(prv_cflog), file=debugfile)
	
	stop = time.perf_counter()
	time_recv_resp = stop-start
	######-----------------------------------------

	######-----------------------------------------	
	###### STEP 4: Verify Message
	
	###### 4a: VERIFY CF-LOG
	start = time.perf_counter()	
	
	if log_size == len(prv_cflog):
		parse_cflog_from_serial(report_num, prv_cflog, prv_log_ptr, debugfile)
		cflog = parse_cflog(APP_LOGS_PATH+str(report_num)+".cflog")
		
		cfg = load(CFG_FILE_PATH)

		cfg = set_cfg_head(cfg, cflog_start_addr)

		valid_cflog, current_node, offending_node, last = verify(cfg, cflog)

		cflog_start_addr = current_node.start_addr

		# valid_cflog, sim_idx, last = vrf_log(report_num, sim_idx)
	else:
		print("CFLog sizes do not match")
		valid_cflog = 0

	stop = time.perf_counter()
	time_cflog = stop-start
	
	print(logMessage[valid_cflog])
	if not valid_cflog:
		print("----------------------------------------------------------------")
		print(" ")
		print("INVALID CF-LOG -- Offending Log Entry: "+str(offending_node)+"Current CFG Node: Branch Source: "+str(current_node.end_addr)+", Possible Destinations: "+str(current_node.successors))
		print(" ")
	print("----------------------------------------------------------------")

	##### 4b: VERIFY HMAC
	print("", file=debugfile)
	print("---- (4) Verify ACFA Report ----", file=debugfile)
	start = time.perf_counter()
	print("-- Comparing MACs", file=debugfile)
	#------- produce expected mac
	print("-- hmac(k,", file=debugfile)
	print("--      pmem,", file=debugfile)
	pmem_hmac = load(HMAC_PMEM_FILE_PATH)
	tmp = pmem_hmac
	
	print("--      chal,", file=debugfile)
	tmp = hmac.new(tmp, msg=challenge, digestmod=hashlib.sha256).digest()

	print("--      metadata,", file=debugfile)
	tmp = hmac.new(tmp, msg=prv_meta, digestmod=hashlib.sha256).digest()

	print("--      cflog", file=debugfile)
	tmp = hmac.new(tmp, msg=prv_cflog, digestmod=hashlib.sha256).digest()
	
	print("--      )", file=debugfile)
	mac = tmp

	print("Expected MAC: "+str(mac), file=debugfile)
	#-------

	print("mac   prv_mac", file=debugfile)
	for j in range(0, key_size):
		print(str(mac[j].to_bytes(1,'big'))+"   "+str(prv_mac[j].to_bytes(1,'big')), file=debugfile)

	vrf = key_size
	for i in range(0, key_size):
		# print(str(prv_mac[i])+" "+str(prv_mac[i]))
		if prv_mac[i] != mac[i]:
			print("False at i="+str(i), file=debugfile)
			print("mac[i]="+str(mac[i]), file=debugfile)	
			print("prv_mac[i]="+str(prv_mac[i]), file=debugfile)
			break
		else:
			vrf = vrf-1

	valid_mac = 1
	if vrf == 0:
		print("-------- Pass Verification (app=1)")
		print("Pass Verification (app=1)", file=debugfile)
	else:
		print("--------  Failed Verification (app=0)")
		print("Failed Verification (app=0)", file=debugfile)
		valid_mac =0
	stop = time.perf_counter()
	time_cmp_vrf_mac = stop-start

	print(macMessage[valid_mac])
	print(" ")
	print("----------------------------------------------------------------")
	print(verifyMessage[valid_mac and valid_cflog])
	print(" ")
	print("----------------------------------------------------------------")
	######-----------------------------------------	

	######-----------------------------------------	
	###### STEP 5: GENERATE RESPONSE (App, Chal', AER_min, AER_max, Auth)
	## In this example, AER_min/AER_max are constants
	print("")
	print("---- (5) Generate Chal' and Auth ----", file=debugfile)
	start = time.perf_counter()
	
	## Generate App
	app = (valid_mac and valid_cflog).to_bytes(1, byteorder="big")

	## Generate new Challenge {chal'}
	new_chal = get_next_challenge(challenge, chal_size, report_num)

	## Generate Auth token
	auth = hmac.new(key, msg=new_chal, digestmod=hashlib.sha256).digest()

	auth = hmac.new(auth, msg=aermin, digestmod=hashlib.sha256).digest()

	auth = hmac.new(auth, msg=aermax, digestmod=hashlib.sha256).digest()

	auth = hmac.new(auth, msg=app, digestmod=hashlib.sha256).digest()
	stop = time.perf_counter()
	time_gen_resp = stop-start
	print("------------------- Generate Chal' and Auth --------------------")
	print("-------- Chal' = Chal + 1")
	print("-------- AER_min = "+hex(int.from_bytes(aermin, byteorder='big')))
	print("-------- AER_max = "+hex(int.from_bytes(aermax, byteorder='big')))
	print("-------- Auth = HMAC(k, Chal' AER_min, AER_max, app)")
	######-----------------------------------------	

	######-----------------------------------------	
	###### STEP 5: SEND ACFA RESPONSE
	print(" ")
	print("---------------- Deliver ACFA response to Prv ------------------")
	print("-------- ACFA Response: (app, Chal', AER_min, AER_max, Auth)")
	print("", file=debugfile)
	print("---- (6) Send ACFA response ----", file=debugfile)
	start = time.perf_counter()
	## app
	ser.write(app)
	echo = ser.read(1)#.encode('hex')
	print("echo (app): "+str(echo), file=debugfile)
	
	print("new_chal: "+str(new_chal), file=debugfile)

	ser.write(new_chal)
	prv_chal = ser.read(32)#.encode('hex')
	print("echo (prv_chal): ", file=debugfile)
	print(str(prv_chal)+" ("+str(type(prv_chal))+")", file=debugfile)
	challenge = new_chal
	
	ser.write(aermin)
	echo = ser.read(2)
	print("echo (aermin): "+str(echo)+" ("+str(type(echo))+")", file=debugfile)
	print("expected (aermin) "+str((aermin)), file=debugfile)
	print("", file=debugfile)

	ser.write(aermax)
	echo = ser.read(2)
	print("echo (aermax): "+str(echo)+" ("+str(type(echo))+")", file=debugfile)
	print("expected (aermax) "+str((aermax)), file=debugfile)
	print("", file=debugfile)

	print("auth: "+str(auth), file=debugfile)
	ser.write(auth)
	echo = ser.read(chal_size)
	print("echo (auth): "+str(echo)+" ("+str(type(echo))+")", file=debugfile)
	print("expected (auth) "+str(auth), file=debugfile)
	print("", file=debugfile)

	stop = time.perf_counter()
	time_send_resp = stop-start
	time_gen_send_resp = time_gen_resp+time_send_resp
	######-----------------------------------------	

	######-----------------------------------------	
	###### STEP 7-9 -- All on Prv side. 
	######     Echo data to verify correctness and know Prv actions
	### Step 7 -- Prv check Auth token is authentic
	### Step 8 -- TCB-Heal is not executed when valid
	### Step 9 -- Resume Execution
	print(" ")
	print("---------------- Wait for Prv to authenticate ------------------")	
	start = time.perf_counter()
	## Read prv auth, echo back
	prv_auth = ser.read(chal_size)
	print("prv auth: ", file=debugfile)
	print(str(prv_auth)+" ("+str(type(prv_auth))+")", file=debugfile)
	ser.write(prv_auth)
	if prv_auth == auth:
		print("-------- Prv ACCEPETS response from Vrf")
		print("Prv ACCEPTS response from Vrf", file=debugfile)
	else:
		print("-------- Prv REJECTS response from Vrf")
		print("Prv REJECTS response from Vrf", file=debugfile)

	#### Read 'out' from prv
	out = ser.read(1)
	print("out: "+str(out), file=debugfile)

	ser.write(out)
	stop = time.perf_counter()
	time_closing_steps = stop-start
	
	out = int.from_bytes(out, byteorder='big')
	app = int.from_bytes(app, byteorder='big')
	idx = out*(out+app)
	
	print(prvnextMessage[idx])
	print(" ")

	######-----------------------------------------	

	#####--------------------------------------
	if app == 1:
		##### DEBUGS -- not part of core protocol & not timed
		# debug old challenge
		echo = ser.read(chal_size)
		print("echo old (*(CHAL_BASE)): "+str(echo)+" ("+str(type(echo))+")", file=debugfile)
		print("", file=debugfile)
		# debug new challenge
		echo = ser.read(chal_size)
		print("echo (*(CHAL_BASE)): "+str(echo)+" ("+str(type(echo))+")", file=debugfile)
		print("expected (*(CHAL_BASE)): "+str(new_chal), file=debugfile)

		echo = ser.read(16)
		print("echo (pmem[0:15]): "+str(echo)+" ("+str(type(echo))+")", file=debugfile)
		print("", file=debugfile)
	#####--------------------------------------

	#####--------------------------------------
	##### Print Timing
	print("------------------- ROUND TIMING (S) ---------------------------", file=debugfile)
	print("Steps 1-3:\tReceive initial response (P --> V): "+str(time_recv_resp), file=debugfile)
	print("   Step 4:\tVrf runs verification: "+str(time_cflog+time_cmp_vrf_mac), file=debugfile)
	print("\t\t--Parse & verify CF-Log: "+str(time_cflog), file=debugfile)
	print("\t\t--Verify hmac: "+str(time_cmp_vrf_mac), file=debugfile)
	print("   Step 5:\tVrf Generate & response : "+str(time_gen_resp), file=debugfile)
	print("   Step 6:\tVrf Send response (V --> P): "+str(time_send_resp), file=debugfile)

	print("Steps 7-9:\tPrv authenticate and decide next action: "+str(time_closing_steps), file=debugfile)
	elapsed = time_recv_resp+time_cflog+time_cmp_vrf_mac+time_gen_send_resp
	print("Elapsed time: "+str(elapsed), file=debugfile)
	print("last="+str(last), file=debugfile)
	print("----------------------------------------------------------------", file=debugfile)
	print("======================================================================")
	
	report_num += 1
	total_time += elapsed
	total_s4 = time_cflog+time_cmp_vrf_mac

	# Append round data to the list [step 1-3 time, step 4 time, step 5 time, step 6 time, step 7-9 time]
	runtime_rounds.append([time_recv_resp, total_s4, time_gen_resp, time_send_resp, time_closing_steps])
	print(" ", file=debugfile)
	#####--------------------------------------



print("--------------------------------------------------", file=debugfile)
print("Average Protocol Run Time ("+str(report_num)+" reports)", file=debugfile)

print("Round | Steps 1-3 | Step 4 | Step 5 | Step 6 | Step 7-9", file=debugfile)
for i in range(0, len(runtime_rounds)):
	print("%d   " % i, end='', file=debugfile)
	for j in range(0, len(runtime_rounds[i])):
		print("%s   " % str(runtime_rounds[i][j]), end='', file=debugfile)
	print("", file=debugfile)
print("--------------------------------------------------", file=debugfile)
print(" ", file=debugfile)
print("--------------------------------------------------")
print("Exit condition: ")
if not app:
	print("Prv shutdown due to TCB-Heal")
else:
	print("Prv completed execution of AER")
print("--------------------------------------------------")

