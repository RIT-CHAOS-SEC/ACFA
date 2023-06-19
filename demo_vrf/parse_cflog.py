from definitions import *

def parse_cflog_from_serial(report_num, prv_cflog, prv_log_ptr, file):
	print("----- parsing message: create "+str(report_num)+".cflog -----")
	print("----- parsing message: create "+str(report_num)+".cflog -----", file=file)

	log_size = prv_log_ptr*2 #len(prv_cflog)
	cflog = []
	i = 0
	print(len(prv_cflog), file=file)
	print(prv_log_ptr, file=file)
	while i < log_size:
		src = "{:02x}".format(prv_cflog[i+1])+"{:02x}".format(prv_cflog[i])
		# print("src = "+str(src))
		dest = "{:02x}".format(prv_cflog[i+3])+"{:02x}".format(prv_cflog[i+2])
		# print("dest = "+str(dest))

		if src[0] != '0':
			entry = src+":"+dest
		else:
			entry = ":"+src+dest
		i+=4
		cflog.append(entry)
	# cflog.append(prv_log_ptr)
	filename = APP_LOGS_PATH+str(report_num)+".cflog"

	with open(filename, 'w+') as cflog_file:
		for entry in cflog:
			print(entry, file=file)
			cflog_file.write("%s\n" % entry)
		# cflog_file.write("%s\n" % str(int(prv_log_ptr/2)))