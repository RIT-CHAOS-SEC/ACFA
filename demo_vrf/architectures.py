# Architectures
class MSP430:
    def __init__(self):
        self.return_instrs           = ['reti','ret']
        self.indr_calls              = ['']
        self.call_instrs             = ['call']
        self.unconditional_br_instrs = ['br','jmp']
        self.conditional_br_instrs   = ['jne', 'jnz', 'jeq','jz', 'jnc', 'jc', 'jn', 'jge', 'jl']
        self.type 				     = "elf32-msp430"
        self.instrumentation_handle  = "qwertyuiopasdfghjklzxcvbnm"
        self.text_base = "0xe000"
        self.patch_base = "0xe300" #default unless updated
        self.all_br_insts = self.return_instrs[:]
        self.all_br_insts += self.indr_calls[:] 
        self.all_br_insts += self.call_instrs[:]
        self.all_br_insts += self.unconditional_br_instrs[:]
        self.all_br_insts += self.conditional_br_instrs[:]
        self.regular_instr_size = 2
        self.double_instr_size = 4
        self.sp = 'r1' # what is the stack pointer in the diassembly?
        self.svr = 'r4' # not the sp, but used to make stack variables, aka 'stack variable register'

class ARMv8M33:
    def __init__(self): 
        self.return_instrs            = ['bx']
        self.indr_calls               = ['blx']
        self.call_instrs			  = ['bl']
        self.unconditional_br_instrs  = [ 'b', 'bal']
        self.conditional_br_instrs    = ['beq','bne','bhs','blo','bhi','bls','bgt','blt','bge','ble','bcs','bcc','bmi','bpl','bvs','bvc', 'cbnz', 'cbz']
        self.type 		        	  = "armv8-m33"
        self.instrumentation_handle   = "SECURE_log"
        self.text_base = "0x80401f8"
        self.patch_base = "0x8060000" # default unless updated
        self.write_instrs    = ['ldr', 'mov', 'movs']
        self.indr_tgt_reg    = 'sl'
        self.regular_instr_size = 2
        self.sp = 'sp'
        self.svr = 'r7' # not the sp, but used to make stack variables, aka 'stack variable register'

        dot_n = [inst+".n" for inst in self.conditional_br_instrs]
        dot_w = [inst+".w" for inst in self.conditional_br_instrs]
        self.conditional_br_instrs += dot_n[:] + dot_w[:]

        dot_n = [inst+".n" for inst in self.unconditional_br_instrs]
        dot_w = [inst+".w" for inst in self.unconditional_br_instrs]
        self.unconditional_br_instrs += dot_n[:] + dot_w[:]

        self.all_br_insts = self.return_instrs[:]
        self.all_br_insts += self.indr_calls[:] 
        self.all_br_insts += self.call_instrs[:]
        self.all_br_insts += self.unconditional_br_instrs[:]
        self.all_br_insts += self.conditional_br_instrs[:]

        dot_w = [inst+'.w' for inst in self.write_instrs]
        self.write_instrs += dot_w[:]
