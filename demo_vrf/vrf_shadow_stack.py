import angr
import sys
from angr_platforms.msp430 import arch_msp430, lift_msp430, simos_msp430
from definitions import *
import os.path
import time
########################################################################
################################## HOOK ###############################
class read_data_hook(angr.SimProcedure):
	def run(self):
		print("---------- HOOKED: read_data() --------------")

class pulseIn_hook(angr.SimProcedure):
	def run(self):
		# a = 1
		print("---------- HOOKED: pulseIn() --------------")

#----------------------------------------------------------------------#
#-------------------------- Inspection Actions ------------------------#
def log_call(state):
	print("--------------------------------")
	print("PAUSE AFTER CALL")

	cur_sp = state.callstack.stack_ptr
	top_of_stack = state.solver.eval(state.mem[cur_sp].uint16_t.resolved)
	print("stack pointer (according to callstack: "+hex(cur_sp))
	print("top of stack: "+hex(top_of_stack))
	
	block = p.factory.block(state.callstack.call_site_addr)
	block_len = block.instructions
	block_insts = block.instruction_addrs
	# print("caller block: "+str([hex(addr) for addr in block_insts]))
	call_site = block_insts[block_len-1]
	pc = state.solver.eval(state.regs.r0)
	r4 = state.solver.eval(state.regs.r4)
	## print("caller pc: "+str(hex(pc)))
	block = p.factory.block(pc)
	block_insts = block.instruction_addrs
	# print("cur block: "+str([hex(addr) for addr in block_insts]))
	call_dest = block_insts[0]
	print("---- expected CALL_SITE: "+hex(call_site)[2:])
	print("---- expected CALL_DEST: "+hex(call_dest)[2:])
	log_entry = (hex(call_site)[2:]+hex(call_dest)[2:])
	# print("expected log_entry: "+log_entry)
	# print("r4 content: "+hex(r4))

	# push onto shadow stack
	shadow_stack.append(top_of_stack)
	# size = len(shadow_stack)
	# shadow_stack[1:size] = shadow_stack[0:size-1]
	# shadow_stack[0] = top_of_stack
	print("---- Shadow stack update (after PUSH): "+str([hex(addr) for addr in shadow_stack]))
	print("--------------------------------")

def log_ret(state):
	print("--------------------------------")
	print("PAUSE AFTER RET")
	pc = state.solver.eval(state.regs.r0)
	block_insts = block.instruction_addrs
	# print("pc: "+hex(pc))
	# print("cur block: "+str([hex(addr) for addr in block_insts]))
	# print("callstack.ret_addr: "+hex(state.callstack.ret_addr))

	exp_ret = hex(state.solver.eval(shadow_stack.pop()))[2:]
	print("---- POP from shadow stack: "+exp_ret)
	print("---- Shadow stack update (after POP): "+str([hex(addr) for addr in shadow_stack]))
	pc = state.solver.eval(state.regs.r0)

	# SKIP read_data() function to avoid path explosion
	if pc in READ_DATA_RETSITES or pc in PULSEIN_RETSITES:
		print("---- Logged return addr: "+str(recv_cflog[recv_idx+4][4:]))
		recv_ret = recv_cflog[recv_idx+4][4:]
		ret_site = recv_cflog[recv_idx+4][:4]

	else: 
		print("---- Logged return addr: "+str(recv_cflog[recv_idx][4:]))
		recv_ret = recv_cflog[recv_idx][4:]
		ret_site = recv_cflog[recv_idx][:4]

	if recv_ret != exp_ret:
		valid = 0
		print("INVALID RETURN: Logged="+str(recv_ret)+" Expected="+str(exp_ret))
	else:
		valid = 1
		#print("Valid return")
#---------------------------
start = time.perf_counter()

shadow_stack = []
valid = 1

READ_DATA_MIN = 0xe126
READ_DATA_MAX = 0xe166
READ_DATA_RETSITES = [0xe0d2]

PULSEIN_MIN = 0xe18e
PULSEIN_MAX = 0xe1da
PULSEIN_RETSITES = [0xe24c]

#print("-----------------------------------")
#print("-------- SYMBOLIC EXECUTION -------")
## PROJECT
p = angr.Project("../scripts/tmp-build/"+APP_NAME+"/vrased.elf")
#print("Binary filename: "+str(p.filename))
#print("Architecture: "+str(p.arch))
#print("Entry address: "+str(hex(p.entry)))
pmem_start = p.loader.find_symbol('__watchdog_support')#'main')
main = p.loader.find_symbol('main')
acfa_exit = p.loader.find_symbol('acfa_exit')
port2 = p.loader.find_symbol('P2IN')

acfa_exit_block = p.factory.block(acfa_exit.rebased_addr)
acfa_exit_insts = []

for inst in acfa_exit_block.instruction_addrs:
	acfa_exit_insts.append(hex(inst)[2:])

# hook read_data() function
p.hook_symbol('read_data', read_data_hook())
p.hook_symbol('pulseIn', pulseIn_hook())

## Get initial state, start simulation at init state
state = p.factory.blank_state(addr=pmem_start.rebased_addr)
simgr = p.factory.simgr(state)

# Start at pmem_min and step forward until pc=main
prog_end_pc = acfa_exit.rebased_addr

# at pc=main, fetch initial cf source
pc_init = state.solver.eval(simgr.active[0].regs.r0)
pc = pc_init

block = p.factory.block(pc)
block_len = block.instructions
block_insts = block.instruction_addrs
cf_src = block_insts[block_len-1]
cf_dest = 0

prev_cf_src = 0
prev_cf_dest = 0

prev_pc = 0;
ctr = 1;
sim_cflog = []
log_index = 0

report_num = 0
report_filename = str(report_num)+".cflog"
full_filename = APP_LOGS_PATH+report_filename
last_src = "e000"

while report_num < 4:
# while os.path.exists(full_filename): #print(full_filename)
	print("-----")
	print("Starting "+report_filename)
	with open(full_filename) as cflog:
		recv_cflog = cflog.read().splitlines()
	cflog_size = int(recv_cflog[len(recv_cflog)-1])
	recv_cflog = recv_cflog[:len(recv_cflog)-1]
	#print(cflog_size)
	#print(len(recv_cflog))

	recv_idx = 1
	#print("------------ Shadow Stack for '"+full_filename+"'  ----------------")
	while recv_idx < cflog_size and last_src not in acfa_exit_insts and recv_cflog[recv_idx][4:] != TCB_MIN:
		## print(str(report_num)+"-"+str(cflog_size)+"-"+str(recv_idx))
		## print(str(last_src)+"-"+str(acfa_exit_insts))

		state.inspect.b('call', when=angr.BP_AFTER, action=log_call)
		state.inspect.b('return', when=angr.BP_AFTER, action=log_ret)

		if pc != prog_end_pc:
			simgr.step()

		pc = state.solver.eval(simgr.active[0].regs.r0)

		## print(hex(pc))

		block = p.factory.block(pc)
		
		## print("state.ip: "+hex(state.solver.eval(state.ip)))

		block_len = block.instructions
		block_insts = block.instruction_addrs
		
		## print("***** Current Block *****")
		## print(block)
		## print([hex(inst) for inst in block_insts])
		## print("*************************")

		prev_cf_dest = cf_dest
		cf_dest = block_insts[0]

		#### IF loop optimizatoin used ####
		# skip counter entries since don't use shadow stack
		counting = (cf_src == prev_cf_src and cf_dest == prev_cf_dest)
		if counting:
			## print(hex(ctr), end='\r', flush=False)
			ctr += 1
		else:
			log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
			if cf_src >= main.rebased_addr:
				## print("cf_src="+hex(cf_src)+"  main.rebased_addr="+hex(main.rebased_addr))
				recv_idx += (ctr >= 2)
				# print(hex(pc))
				
				if pc in READ_DATA_RETSITES or pc in PULSEIN_RETSITES:
					recv_idx += 4

				recv_idx += 1

				log_index += 1
			prev_cf_src = cf_src
			last_src = hex(prev_cf_src)[2:]
			cf_src = block_insts[block_len-1]
			prev_pc = pc
			ctr = 1
	
	stop = time.perf_counter()
	report_num += 1 
	report_filename = str(report_num)+".cflog"
	full_filename = APP_LOGS_PATH+report_filename

	print("Time Elapsed: "+str(stop-start))
	print("-----")