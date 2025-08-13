from collections import deque
import pickle
from structures import *
from utils import *
import os
import time
import sys
from definitions import *

def verify(cfg, cflog):
    '''
    Function verifies whether given CFLog is valid.
    Returns True if log is valid, else returns False
    '''

    # Try to open prev. shadow_stack file
    try:
        # If intermediate report, open prevoius shadow stack state
        shadow_stack = load(SHADOW_STACK_FILE_PATH)
    except FileNotFoundError as e:
        # If first report, no file will be found. Therefore instantiate shadow stack
        shadow_stack = deque()

    last_cflog = False
    current_node = cfg.head
    log_idx = -1
    for log_node in cflog:
        log_idx += 1

        ## Valid if enter or exit from TCB
        if log_node.src_addr == "0xdffe" or log_node.dest_addr == "0xa000":
            continue

        ## If AER_done trigger
        if log_node.dest_addr == cfg.label_addr_map['acfa_exit']:
            last_cflog = True
            break

        # Src addr of log node should be the end addr (br instr) of node  
        if log_node.src_addr == current_node.end_addr: 
            if current_node.type == 'uncond' or current_node.type == 'cond':
                if log_node.dest_addr in current_node.successors:
                    current_node = cfg.nodes[log_node.dest_addr]
                    continue
            # If its a call, we need to push adj addr to shadow stack
            elif current_node.type == 'call': 
                shadow_stack.append(current_node.adj_instr)
                if log_node.dest_addr in current_node.successors:
                    current_node = cfg.nodes[log_node.dest_addr]
                    continue
            elif current_node.type == 'ret': 
                ret_addr = shadow_stack.pop()
                if log_node.dest_addr == ret_addr:
                    current_node = cfg.nodes[log_node.dest_addr]
                    continue
                else:
                    #TODO: Raise a Return Address Violation
                    pass
                    #err = raise(custom exception)

        return False, current_node, log_node, last_cflog, log_idx

    # Save the current state of the shadow stack to resume on next log slice
    dump(shadow_stack, SHADOW_STACK_FILE_PATH)

    return True, current_node, None, last_cflog, log_idx

def parse_cflog(cflog_file, arch):
    # To make this more generalized, we may need to add a delimeter
    
    with open(cflog_file,'r') as f :
        lines = f.readlines()
    cflog_lines = [x.replace('\n','') for x in lines if x != '\n']

    stop = time.time()
    
    # sizeFile = open("./logs/sizes.log", "a")
    # print(f"CFLog Size: {4*len(lines)} bytes", file=sizeFile)
    # sizeFile.close()

    cflog = []
    if arch.type == 'elf32-msp430':
        cflog_lines = cflog_lines[:-2]
        for line in cflog_lines:
            line = line.split(':')
            # print(f"Line: {line}")
            if line[0] == "dffe" or line[1] == "a000":
                continue
            elif len(line) > 1:
                if line[1][0] != '0': #Check if the line is a loop counter
                    s = '0x' + line[0]
                    d = '0x' + line[1]
                    cflog.append(CFLogNode(s,d))
                else: # add loop counter value to prev LogNode
                    cflog[-1].loop_count = int(line[1],16)
    elif arch.type == 'armv8-m33':
        for line in cflog_lines:
            if line[:4] != 'ffff': #Check if the line is a loop counter
                if 'fefffffe' not in line:
                    s = None
                    d = '0x' + line
                    cflog.append(CFLogNode(s,d))
                else:
                    # fefffffe is special char for return to SW, denotes end of cflog
                    break
            else: # add loop counter value to prev LogNode
                cflog[-1].loop_count = int(line[4:],16)
                # print(f"Setting loop_count={cflog[-1].loop_count} for entry={cflog[-1].dest_addr}")
                
    
    f = open("./logs/cflog_nodes.log", "w")
    for log_node in cflog:
        print(log_node, file=f)
    f.close()

    return cflog

def path_verifier(cfgfile, funcname, total_cflogs): 

    ## Do once
    # Load cfg
    cfg = load(cfgfile)
    asm_func_file = cfgfile.replace("cfg", "asm_func")
    # asm_funcs = load(asm_func_file)
    
    # If start addr not provided, lookup addr of function (or label) instead
    start_addr = cfg.label_addr_map[funcname]

    # Set the cfg head to the start address of where we want to attest
    cfg = set_cfg_head(cfg, start_addr)
    
    ## do per available cflog
    i = 1
    valid = True
    while valid and i < total_cflogs:
        # parse cflog
        cflog_file = f"../logs/{i}.cflog"
        print(f"Verifying {cflog_file}")
        cflog = parse_cflog(cflog_file, cfg.arch)

        # Verify the cflog against the CFG
        valid, current_node, offending_node, last_cflog, offending_cflog_index = verify(cfg, cflog)
        cfg = set_cfg_head(cfg, current_node.start_addr)
        i += 1

    if valid:
        print(bcolors.GREEN + '[+] CFLog is VALID!' + bcolors.END)
    else:
        print(bcolors.RED + '[-] CFLog is INVALID!' + bcolors.END)
        print("Offending CFLog entry: "+str(offending_cflog_index))
        print("Valid destinations: "+str(current_node.successors))
        print("Logged destination: "+str(offending_node.dest_addr))
        print("Corrupted br. Instruction: "+str(current_node.instr_addrs[-1]))
        print()

    return cfg, cflog, valid, current_node, offending_node, offending_cflog_index

if __name__ == "__main__":
    cfgfile = "./objs/cfg.bin"
    funcname = "main"
    total_cflogs = 10
    cfg, cflog, valid, current_node, offending_node, offending_cflog_index = path_verifier(cfgfile,funcname,total_cflogs)
    