import angr
import sys
import time
from angr_platforms.msp430 import arch_msp430, lift_msp430, simos_msp430
from definitions import *


class read_data_hook(angr.SimProcedure):
	def run(self):
		print("---------- IN READ_DATA_HOOK --------------")
		final_dest = self.state.callstack.ret_addr

		print("pass[] = "+str(state.memory.load(pass_symbol.rebased_addr, len(pass_buffer))))
		print("user_input[] = "+str(state.memory.load(user_input_symbol.rebased_addr, len(user_input_buffer))))
		
		pc = state.solver.eval(simgr.active[0].regs.r0)
		block = p.factory.block(pc)
		block_len = block.instructions
		block_insts = block.instruction_addrs
		print("initial block")
		print([hex(x) for x in block_insts])
		
		cf_src = block_insts[block_len-1]

		block = p.factory.block(cf_src+0x2)
		block_insts = block.instruction_addrs
		cf_dest = block_insts[7]
		block_len = block.instructions#-1
		# block_insts = block_insts[1:]
		print("while block")
		print([hex(x) for x in block_insts])
				
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)
		prev_cf_src = cf_src

		cf_src = block_insts[block_len-1]
		cf_dest = block_insts[0]
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)
		prev_cf_src = cf_src		

		# Total loops based on max index value
		c = hex(len(user_input_buffer)-1)[2:]
		l = ""
		for i in range(0, 8-len(c)):
			l += "0"
		l += c
		sim_cflog.append(l)
		print("log_entry: "+str(l))

		block = p.factory.block(block_insts[block_len-1]+0x2)
		block_len = block.instructions
		block_insts = block.instruction_addrs
		print("exit block")
		print([hex(x) for x in block_insts])

		cf_dest = block_insts[0]		
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)
		prev_cf_src = cf_src

		cf_src = block_insts[block_len-1]
		print("final cf_src: "+hex(cf_src))
		cf_dest = final_dest
		print("final cf_dest "+hex(cf_dest))
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)
		# return total
		print("---------------------------------")

class pulseIn_hook(angr.SimProcedure):
	def run(self):
		print("---------- IN PULSEIN_HOOK --------------")
		MAX_DURATION = 1000
		
		pc = state.solver.eval(simgr.active[0].regs.r0)
		block = p.factory.block(pc)
		block_len = block.instructions
		block_insts = block.instruction_addrs
		print("initial block")
		print([hex(x) for x in block_insts])
		
		cf_src = block_insts[block_len-1]
		block = p.factory.block(cf_src+0x2)
		block_len = block.instructions
		block_insts = block.instruction_addrs
		cf_dest = block_insts[block_len-2]
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)

		block_insts = block.instruction_addrs
		print("while block")
		print([hex(x) for x in block_insts])
		cf_src = block_insts[block.instructions-1]
		cf_dest = block_insts[0]
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)

		# Total loops based on MAX_DURATION value
		c = hex(MAX_DURATION)[2:]
		l = ""
		for i in range(0, 8-len(c)):
			l += "0"
		l += c
		sim_cflog.append(l)
		print("log_entry: "+str(l))

		print("exit block")
		block = p.factory.block(cf_src+0x2)
		block_len = block.instructions
		block_insts = block.instruction_addrs
		cf_dest = block_insts[0]
		print([hex(x) for x in block_insts])
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)

		final_dest = self.state.callstack.ret_addr
		cf_src = block_insts[block_len-1]
		print("final cf_src: "+hex(cf_src))
		cf_dest = final_dest
		print("final cf_dest "+hex(cf_dest))
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		print("log_entry: "+str(log_entry))
		sim_cflog.append(log_entry)
		print("----------------------------------------")

print("-----------------------------------")
print("-------- SYMBOLIC EXECUTION -------")
start = time.perf_counter()

## PROJECT
p = angr.Project("../scripts/tmp-build/"+APP_NAME+"/vrased.elf")
print("Binary filename: "+str(p.filename))
print("Architecture: "+str(p.arch))
print("Entry address: "+str(hex(p.entry)))
pmem_start = p.loader.find_symbol('__watchdog_support')#'main')
main = p.loader.find_symbol('main')
acfa_exit = p.loader.find_symbol('acfa_exit')
print("pmem_start: "+str(pmem_start))
print("acfa_exit: "+str(acfa_exit))

# Hooked function addrs constants
READ_DATA_MIN = 0xe126
READ_DATA_MAX = 0xe166
PULSEIN_MIN = 0xe18e
PULSEIN_MAX = 0xe1da

# Get last block to determine last log
acfa_exit_block = p.factory.block(acfa_exit.rebased_addr)
acfa_exit_insts = []
for inst in acfa_exit_block.instruction_addrs:
	acfa_exit_insts.append(hex(inst)[2:])

# create hooks
p.hook_symbol('read_data', read_data_hook())
p.hook_symbol('pulseIn', pulseIn_hook())

## Get initial state, start simulation at init state
state = p.factory.blank_state(addr=pmem_start.rebased_addr,add_options={angr.options.CONCRETIZE})
simgr = p.factory.simgr(state)
print("State type: "+str(type(state)))

## Get symbolic representation of input data
pass_buffer = ['a', 'b', 'c', 'd']
pass_symbol = p.loader.find_symbol('pass')
print("pass[0] symbolic addr: "+hex(pass_symbol.rebased_addr))
# print("Setting symbolic vals: ")
print("pass[] = "+str(state.memory.load(pass_symbol.rebased_addr, len(pass_buffer))))

user_input_buffer = ['a', 'b', 'c', 'd', '\r']
user_input_symbol = p.loader.find_symbol('user_input')
print("pass[0] symbolic addr: "+hex(user_input_symbol.rebased_addr))
# print("Setting symbolic vals: ")
print("user_input[] = "+str(state.memory.load(user_input_symbol.rebased_addr, len(user_input_buffer))))

# Start at pmem_min and step forward until pc=main
prog_end_pc = acfa_exit.rebased_addr

# at pc=main, fetch initial cf source
pc_init = state.solver.eval(simgr.active[0].regs.r0)
pc = pc_init
block = p.factory.block(pc)
block_len = block.instructions
block_insts = block.instruction_addrs

# initialize script variables
cf_src = block_insts[block_len-1]
cf_dest = 0
prev_cf_src = 0
prev_cf_dest = 0
prev_pc = 0;
ctr = 1;
sim_cflog = []
log_index = 0

# '''
# Iterate through graph until reached program end or unresolved branch
while len(simgr.active) == 1 and pc != prog_end_pc and block_len != 1:
	## Print for Debugging
	# print("len(simgr.active): "+str(len(simgr.active)))
	# print("pc = "+hex(pc))
	# print("prog_end_pc = "+hex(prog_end_pc))
	# print("block_len = "+str(block_len))

	if pc != prog_end_pc:
		something = simgr.step()

	print(hex(pc))
	pc = state.solver.eval(simgr.active[0].regs.r0)
	block = p.factory.block(pc)

	block_len = block.instructions
	block_insts = block.instruction_addrs

	## Print for Debugging
	# print("***** Current Block *****")
	# print([hex(x) for x in block_insts])
	# print(block)
	# print("First: "+hex(block_insts[0])+"  Last: "+hex(block_insts[block_len-1]))
	# r13 = simgr.active[0].regs.r13
	# r14 = simgr.active[0].regs.r14
	# print("r13: "+hex(state.solver.eval(r13))+" ("+str(r13)+")")
	# print("r14: "+hex(state.solver.eval(r14))+" ("+str(r14)+")")
	# cmp_val = state.memory.load(r14-0x1, 1)
	# print("-1(r14): "+hex(state.solver.eval(cmp_val))+" ("+str(cmp_val)+")")
	# # state.solver.add(simgr.active[0].regs.r14 < 0x805)
	# print("*************************")

	prev_cf_dest = cf_dest
	cf_dest = block_insts[0]

	### Create expected ACFA-CFLog entry
	if cf_src == prev_cf_src and cf_dest == prev_cf_dest:
		print(ctr)
		ctr += 1
	else:
		# print()
		if ctr > 2 :
			# create log entry for ctr and write to log
			c = hex(ctr)[2:]
			l = ""
			for i in range(0, 8-len(c)):
				l += "0"
			l += c
			if cf_src >= main.rebased_addr:
				# print("cf_src="+hex(cf_src)+"  main.rebased_addr="+hex(main.rebased_addr))
				sim_cflog[len(sim_cflog)-1]= l
				print("log_entry: "+l)
		# reset ctr
		ctr = 1

	if ctr <= 2:
		# print("pc="+hex(pc)+"  main.rebased_addr="+hex(main.rebased_addr))
		# print("pc="+hex(pc))
		print("current block: "+str([hex(addr) for addr in block_insts]))
		log_entry = (hex(cf_src)[2:]+hex(cf_dest)[2:])
		if (cf_src >= main.rebased_addr and (cf_src < READ_DATA_MIN) or cf_src > READ_DATA_MAX) and cf_src < PULSEIN_MIN or cf_src > PULSEIN_MAX:
			# print("cf_src="+hex(cf_src)+"  main.rebased_addr="+hex(main.rebased_addr))
			print("log_entry: "+log_entry)
			sim_cflog.append(log_entry)
			log_index += 1
		prev_cf_src = cf_src
		cf_src = block_insts[block_len-1]
		prev_pc = pc
		# print(str(log_index)+": (src, dest) : ("+hex(cf_src)+", "+hex(cf_dest)
			# +")   (prev_src, prev_dest): ("+hex(prev_cf_src)+", "+hex(prev_cf_dest))
		# print(str([hex(inst) for inst in block_insts]))
	
	# # UNCOMMENT FOR STEP BY STEP (press keyboard to continue)
	# if pc > 0xe03e:
	# 	a = input()

## Final block infinite end-of-program block
end_program_inst = acfa_exit_insts[len(acfa_exit_insts)-1]
print("simlog size: "+str(len(sim_cflog)))

## Stops before last block, so get info for last block
print("***** Last Blocks *****")
print(end_program_inst)
block = p.factory.block(pc)
block_len = block.instructions
block_insts = block.instruction_addrs
print([hex(x) for x in block_insts])
cf_src = block_insts[block_len-1]
log_entry = (hex(cf_src)[2:]+end_program_inst)
print("final log_entry: "+log_entry)
sim_cflog.append(log_entry)

## update exit instructions to uncompass all insts (angr is buggy)
acfa_exit_insts = acfa_exit_insts + [hex(x)[2:] for x in p.factory.block(p.loader.find_symbol('__stop_progExec__').rebased_addr).instruction_addrs]
print(acfa_exit_insts)

## Print Simulate CF-Log
print("--------- Simulated CF-Log --------")
for entry in sim_cflog:
	print(entry)
print("-----------------------------------")

## Write to 'sim.cflog'
with open('sim.cflog', 'w+') as sim_cflog_file:
	e = 0
	for entry in sim_cflog:
		# print(str(e)+": "+entry)
		sim_cflog_file.write("%s\n" % entry)
		e += 1

## Write exit insts to 'acfa_exit_insts.log'
with open('acfa_exit_insts.log', 'w+') as aei_file:
	for inst in acfa_exit_insts:
		aei_file.write("%s\n" % inst)

# '''
stop = time.perf_counter()
print("Elapsed time (s): "+str(stop-start))