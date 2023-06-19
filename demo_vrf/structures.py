from dataclasses import dataclass,field

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
    def __init__(self,addr,instr,arg,comment):
        self.addr           = addr
        self.instr       = instr
        self.arg          = arg 
        self.comment           = comment

    def __repr__(self) -> str:
        string = ''
        string += f'Address: {self.addr} Instruction: {self.instr} Argument: {self.arg} Comment: {self.comment}'
        return string+'\n'
    
class AssemblyFunction:
    def __init__(self,start_addr,end_addr,instrs):
        self.start_addr = start_addr # start addr of the function
        self.end_addr   = end_addr # end addr of the function
        self.instr_list     = instrs # list of instrs in the function

    def __repr__(self) -> str:
        string = ''
        string += f'Start Address: {self.start_addr} End Address: {self.end_addr}'
        return string+'\n'

# Data Structures

class CFLogNode:
    def __init__(self, src_addr, dest_addr):
        self.src_addr     = src_addr
        self.dest_addr    = dest_addr 
        self.loop_count   = None      

    def __repr__(self) -> str:
        string = ''
        string += f'Source Address: {self.src_addr}\tDestination Address: {self.dest_addr}'
        return string+'\n'

class CFGNode:
    def __init__(self, start_addr, end_addr):
        self.start_addr     = start_addr
        self.end_addr       = end_addr
        self.type           = None
        self.instrs         = 0
        self.instr_addrs    = []
        self.successors     = []  
        self.adj_instr      = None        

    def __repr__(self) -> str:
        string = ''
        string += f'Start Address: {self.start_addr}\tEnd Address: {self.end_addr}\tType: {self.type}\t# of Instructions: {self.instrs}\tAdjacent Address: {self.adj_instr}'
        #string += f'Instruction List: {self.instr_addrs}\n'
        string += f'Successors: {self.successors}\n'
        return string+'\n\n'

    def add_successor(self,node):
        self.successors.append(node)

    def add_instruction(self, instr_addr):
        self.instr_addrs.append(instr_addr)
        self.instrs += 1

class CFG:
    def __init__(self):
        self.head               = None
        self.nodes              = {} #node start addr is key, node obj is value
        self.func_nodes     = {}
        self.num_nodes    = 0 #number of nodes in the node dictionary
        self.label_addr_map = {}

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
        self.func_nodes[func_addr] = [self.nodes[func_addr]]
        if node.start_addr != func_addr:
            self.func_nodes[func_addr].append(node)
        # Increment the number of nodes
        self.num_nodes += 1