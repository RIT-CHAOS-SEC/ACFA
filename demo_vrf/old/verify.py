from collections import deque
import argparse
from definitions import SHADOW_STACK_FILE_PATH
from structures import *
from utils import *

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
    for log_node in cflog:

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

        return False, current_node, log_node, last_cflog

    # Save the current state of the shadow stack to resume on next log slice
    dump(shadow_stack, SHADOW_STACK_FILE_PATH)

    return True, current_node, None, last_cflog

def parse_cflog(cflog_file):
    # To make this more generalized, we may need to add a delimeter
    # Between start and end address
    cflog_lines = read_file(cflog_file)

    cflog = []
    for line in cflog_lines:
        line = line.split(':')
        
        if len(line) > 1 and line[1][0] != '0': #Check if the line is a loop counter
            s = '0x' + line[0]
            d = '0x' + line[1]
            cflog.append(CFLogNode(s,d))
        else: # add loop counter value to prev LogNode
            try:
                cflog[-1].loop_count = int(line[1],16)
            except Exception as e:
                pass
            

    return cflog

def set_cfg_head(cfg, start_addr, end_addr=None):
    try: 
        cfg.head = cfg.nodes[start_addr]
    except KeyError as err:
        print(bcolors.RED + '[!] Error: Start address to verify from is not a valid node' + bcolors.END)
        exit(1)
    return cfg

def arg_parser():
    '''
    Parse the arguments of the program
    Return:
        object containing the arguments
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfgfile', metavar='N', type=str, default='cfg.pickle',
                        help='Path to input file to load serialized CFG. Default is cfg.pickle')
    parser.add_argument('--funcname', metavar='N', type=str, default='main',
                        help='Name of the function to be tracked in the attestation. Set to "main" by default.')
    parser.add_argument('--cflog', metavar='N', type=str,
                        help='File where the cflog to be attested is.')
    parser.add_argument('--startaddr', metavar='N', type=str,
                        help='Address at which to begin verification. Address MUST begin with "0x"')
    parser.add_argument('--endaddr', metavar='N', type=str,
                        help='Address at which to end verification')

    args = parser.parse_args()
    return args

def main():
    args = arg_parser()

    print("args: ")
    print(args)

    # Load and parse CFLog
    cflog = parse_cflog(args.cflog)

    # Load cfg
    cfg = load(args.cfgfile)

    # If start addr not provided, lookup addr of function (or label) instead
    if not args.startaddr:
        try:
            start_addr = cfg.label_addr_map[args.funcname]
        except KeyError:
            print(f'{bcolors.RED}[!] Error: Invalid Function Name [{args.funcname}]{bcolors.END}')
            exit(1)
    else:
        start_addr = args.startaddr

    # Set the cfg head to the start address of where we want to attest
    cfg = set_cfg_head(cfg, start_addr)

    # Verify the cflog against the CFG
    valid, current_node, offending_node, last_cflog = verify(cfg, cflog)

    if valid:
        print(bcolors.GREEN + '[+] CFLog is VALID!' + bcolors.END)
    else:
        print(bcolors.RED + '[-] CFLog is INVALID!' + bcolors.END)
        print(f'{bcolors.YELLOW}[-] Offending Log Entry: {offending_node}{bcolors.END}')

    print("Last node addr: "+str(current_node.start_addr))

if __name__ == "__main__":
    main()