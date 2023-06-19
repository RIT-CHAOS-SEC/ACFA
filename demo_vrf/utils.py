from architectures import *
from os.path import exists
import pickle

def read_file(file):
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
    lines = [x for x in lines if ("nop" not in x) and (".word" not in x)]

    return lines

def set_arch(arch):
    if arch == 'elf32-msp430':
        return MSP430() 
    elif arch == 'armv8-m33':
        return ARMv8M33() 
    else: 
        return None

def load(filename):
    f = open(filename,'rb')
    obj = pickle.load(f)
    f.close()
    return obj

def dump(obj, filename):
    filename = open(filename, 'wb')
    pickle.dump(obj, filename)
    filename.close()


def get_init_challenge(chal_size):
    challenge = []
    for i in range(0, chal_size):
        challenge.append(0)
    return challenge

def get_next_challenge(prev_chal, chal_size, report_num):
    if report_num == 0:
        new_chal = []
        for i in range(0, chal_size):
            new_chal.append((65+i).to_bytes(1,byteorder='big'))
        new_chal = b''.join(new_chal)
        return new_chal
    else:
        new_chal = (prev_chal[0]+1).to_bytes(1,byteorder='big')+prev_chal[1:]
        return new_chal

def swap_endianess(a):
    if type(a) == type(b'\x00'):
        i = 0
        swp = []
        while i < len(a):
            swp.append(a[i+1].to_bytes(1,byteorder='big'))
            swp.append(a[i].to_bytes(1,byteorder='big'))
            i += 2
        return b''.join(swp)

    if type(a) == type([]):
        i = 0
        while i < len(a):
            tmp = a[i]
            a[i] = a[i+1]
            a[i+1] = tmp
            i += 2
        return a