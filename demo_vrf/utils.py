from architectures import *
from os.path import exists
import pickle

def read_file(file, arch_type=None):
    '''
    This function receive the .s file name and read its lines.
    Return : 
        List with the lines of the assembly as strings
    '''
    #assert file.endswith('.s')
    if not(exists(file)) :
        raise NameError(f'File {file} not found !!')
    with open(file,'r') as f :
        lines = f.readlines()
    # Get rid of empty lines
    lines = [x.replace('\n','') for x in lines if x != '\n']

    # ARM: Get rid of "nop" and ".word" lines
    if arch_type == 'armv8-m33':
        lines = [x for x in lines if ("nop" not in x) and (".word" not in x)]

    return lines

def set_arch(arch):
    if arch == 'elf32-msp430':
        return MSP430() 
    elif arch == 'armv8-m33':
        return ARMv8M33() 
    else: 
        return None

def dump(obj, filename):
    filename = open(filename, 'wb')
    pickle.dump(obj, filename)
    filename.close()

def load(filename):
    f = open(filename,'rb')
    obj = pickle.load(f)
    print(f"loaded {type(obj)} from {filename}")
    f.close()
    return obj

def clean_comment(arch, comment):
    """
    This function attempts to extract a memory address from a given comment.
    """
    if arch.type == 'elf32-msp430':
        if comment is None:
            return comment
        comment = comment.split(' ')
        for c in comment:
            if '0x' in c:
                return c.strip('ghijklmnopqrstuvwyz!@#$%^&*(),<>/?.')
    # 
    elif arch.type == 'armv8-m33':
        if comment is None:
            return comment
        # comment = comment.split(' ')
        print("comment: "+str(comment))

def set_cfg_head(cfg, start_addr, end_addr=None):
    try: 
        cfg.head = cfg.nodes[start_addr]
    except KeyError as err:
        print(bcolors.RED + f'[!] Error: Start address ({start_addr}) to verify from is not a valid node' + bcolors.END)
        exit(1)
    return cfg

def conditional_print(str, file=None, flag=True):
    if flag:
        print(str, file=file)

def get_init_challenge(chal_size):
    challenge = []
    for i in range(0, chal_size):
        challenge.append(0)
    return challenge