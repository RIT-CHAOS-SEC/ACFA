from definitions import *

def parse_cflog(report_num, prv_cflog, prv_log_ptr, file):
	print("----- parsing message: create "+str(report_num)+".cflog -----")
	print("----- parsing message: create "+str(report_num)+".cflog -----", file=file)

	log_size = prv_log_ptr*2 #len(prv_cflog)
	cflog = []
	i = 0
	print(len(prv_cflog), file=file)
	print(prv_log_ptr, file=file)
	if log_size == 4:
		entry = "0x{:02x}".format(prv_cflog[i+1])[2:]+"0x{:02x}".format(prv_cflog[i])[2:]
		entry += "0x{:02x}".format(prv_cflog[i+3])[2:]+"0x{:02x}".format(prv_cflog[i+2])[2:]
		cflog.append(entry)
	else:
		while i < log_size:
			entry = "0x{:02x}".format(prv_cflog[i+1])[2:]+"0x{:02x}".format(prv_cflog[i])[2:]
			entry += "0x{:02x}".format(prv_cflog[i+3])[2:]+"0x{:02x}".format(prv_cflog[i+2])[2:]
			cflog.append(entry)
			i+=4
	
	cflog.append(prv_log_ptr)
	filename = APP_LOGS_PATH+str(report_num)+".cflog"

	with open(filename, 'w+') as cflog_file:
		for entry in cflog:
			print(entry, file=file)
			cflog_file.write("%s\n" % entry)
		cflog_file.write("%s\n" % str(int(prv_log_ptr/2)))