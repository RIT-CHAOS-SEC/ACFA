from dataclasses import dataclass,field
from typing import List
from sys import stdout
from utils import *
import time 

# Definitions
SUPPORTED_ARCHITECTURES = ['elf32-msp430','armv8-m33']

TEXT_PATTERN = ['Disassembly of section .text:',
                'Disassembly of section']

NODE_TYPES = ['cond','uncond','call','ret']

class bcolors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    END = '\033[0m'


class AssemblyInstruction:
    def __init__(self,addr,instr,arg,comment=None,prev_addr=None):
        self.addr        = addr
        self.instr       = instr
        self.arg         = arg 
        self.comment     = comment
        self.prev_addr   = prev_addr

    def __repr__(self) -> str:
        string = ''
        string += f'{self.addr} {self.instr} {self.arg}'
        return string
        
    def update(self, instr, arg):
        self.instr       = instr
        self.arg         = arg 

    def reconstruct(self):
        ### reconstruct into a string thats readble by MSProbe
        return f'{self.instr} {self.arg}'
    
class AssemblyFunction:
    def __init__(self,start_addr,end_addr,instrs):
        self.start_addr = start_addr # start addr of the function
        self.end_addr   = end_addr # end addr of the function
        self.instr_list     = instrs # list of instrs in the function
        self.return_node = None

    def __repr__(self) -> str:
        string = ''
        string += f'Start Address: {self.start_addr} End Address: {self.end_addr}'
        return string+'\n'

# Data Structures

class CFLogNode:
    def __init__(self, src_addr, dest_addr, loop_count=None):
        self.src_addr     = src_addr
        self.dest_addr    = dest_addr 
        self.loop_count   = loop_count      

    def __repr__(self) -> str:
        string = ''
        string += f'src: {self.src_addr}\tdest: {self.dest_addr}\tloop_count: {self.loop_count}'
        return string+'\n'

class CFGNode:
    def __init__(self, start_addr, end_addr):
        self.start_addr     = start_addr
        self.end_addr       = end_addr
        self.type           = None
        self.instrs         = 0
        self.instr_addrs    = []
        self.successors     = []  
        self.parents        = []
        self.adj_instr      = None
        self.definitions    = {}        

    def __repr__(self) -> str:
        string = ''
        string += f'Start Address: {self.start_addr}\tEnd Address: {self.end_addr}\tType: {self.type}\t# of Instructions: {self.instrs}\tAdjacent Address: {self.adj_instr}\n'
        #string += f'Instruction List: {self.instr_addrs}\n'
        string += f'Successors: {self.successors}\n'
        string += f'Parents: {self.parents}\n'
        return string+'\n\n'

    def add_successor(self,node):
        self.successors.append(node)

    def add_instruction(self, instr_addr):
        self.instr_addrs.append(instr_addr)
        self.instrs += 1

    def printNode(self, file=stdout):
        print("start_addr: "+str(self.start_addr), file=file)
        print("end_addr: "+str(self.end_addr), file=file)
        print("successors: "+str(self.successors), file=file)
        print("parents: "+str(self.parents), file=file)
        print("type: "+str(self.type), file=file)
        print("adj_instr: "+str(self.adj_instr), file=file)

class CFG:
    def __init__(self):
        self.head = None
        self.nodes = {} #node start addr is key, node obj is value
        self.func_nodes = {}
        self.num_nodes = 0 #number of nodes in the node dictionary
        self.label_addr_map = {}
        self.arch = None
        self.indr_calls = []
        self.indr_jumps = []
        self.loop_nodes = []

    #Currently just prints all nodes, not just successors of cfg.head
    def __repr__(self)-> str:
        string = ''
        if self.num_nodes > 0:
            string += f'Total # of nodes: {self.num_nodes}\n'
            print(self.nodes)
        else:
            string += 'Empty CFG'

        return string+'\n\n'

    # Method to add a node to the CFG's dictionary of nodes
    def add_node(self,node,func_addr):
        # add node to dict of all nodes
        self.nodes[node.start_addr] = node
        # Add node to function nodes if there is >1 node
        # self.func_nodes[func_addr] = [self.nodes[func_addr]]
        # if node.start_addr != func_addr:
        #     self.func_nodes[func_addr].append(node)

        # Increment the number of nodes
        self.num_nodes += 1

    def get_node(self,instr_addr):
        #retursn the node's start addr that contains an instruction (specified by instr_addr)
        for node_addr in self.nodes.keys():
            node = self.nodes[node_addr]
            if int(node.start_addr, 16) <= int(instr_addr, 16) <= int(node.end_addr, 16):
                return node.start_addr
        return None #couldn't find it for some reason

class Patch:
    def __init__(self, addr):
        self.addr = addr
        self.instr = []
        self.bin = []
        self.bytes = b''
        self.hex = []
        self.type = 0 #0 = new code, 1 = update node
        self.mode = 0 #0 ASM only, 1 BIN

    def __repr__(self)-> str:
        string = f"addr: {self.addr}\n"
        for i in range(0, len(self.instr)):
            string += f"({self.instr[i].prev_addr}) {self.instr[i]}\n"
        return string+'\n'

class PatchGenerator:
    def __init__(self, base):
        try:
            self.base = int(base,16)
        except TypeError:
            self.base = base
        self.patches = {}
        self.total_patches = 0
        self.new_targets = []

    def __repr__(self)-> str:
        string = f'Total patches: {self.total_patches}\n'
        string += f'Patches: {self.total_patches}\n'
        string += f'Base: {hex(self.base)}\n'
        for addr in self.patches.keys():
            patch = self.patches[addr]
            
            string += f'{patch}'
            # string += f"addr: {hex(patch['addr'])}\n"
            # for inst in patch['instr']:
                # string += str(inst)+'\n'
            string += '\n'

        return string+'\n'

    def dump_patch_bin(self):
        count = 0
        for addr, patches in self.patches.items():
            f = open(f"./objs/patch{count}.bin", "wb")
            # print(f"Writing {patches.bytes} to ./objs/patch{count}.bin")
            f.write(patches.bytes)
            f.close()
            count += 1

class HashSets():
    def __init__(self):
        self.valid_program_hashes = [] #valid hashes of the entire program execution
        self.loop_start_hash_value_mapping = {} # maps a loop start addr to the valid hash chain values entering the loop
        self.loop_path_hashes = {} # loop start addresses and valid hashes of their internal branching
        self.loop_paths = {} # 