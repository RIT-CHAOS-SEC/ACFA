from hmac_mem import *
from definitions import *
from utils import *
import time
from generate_cfg import *

chal_size = 32
challenge = get_init_challenge(chal_size)

challenge = [x.to_bytes(1,byteorder='big') for x in challenge]
challenge = b''.join(challenge)

METADATA_SIZE = 6
#####

key_size = 32

key = [0,0,0,0,0,0,0,0,
       0,0,0,0,0,0,0,0,
       0,0,0,0,0,0,0,0,
       0,0,0,0,0,0,0,0]
key = [x.to_bytes(1,byteorder='big') for x in key]
key = b''.join(key)

##### OFFLINE PHASE
# pmem_size = 0x2000-1 # 8KB
# pmem_size = 0x1000-1 # 4KB
# pmem_size = 0x0800-1 # 2KB
print("--------------------------------------------------")
print("Offline Phase")
print("--------------------------------------------------")
start = time.perf_counter()
pmem_size = 0x0400-1 # 1KB
print("\t Computing HMAC(PMEM)...")
pmem_hmac = hmac_mem(key, pmem_size)
dump(pmem_hmac, HMAC_PMEM_FILE_PATH)
print("\t\tpmem_hmac: "+str(pmem_hmac)+" "+str(type(pmem_hmac)))

print("\t Getting CFG from 'tcb.lst'...")
asm_lines = read_file("../scripts/tmp-build/demo_prv/tcb.lst")
cfg = create_cfg(set_arch("elf32-msp430"), asm_lines)
dump(cfg, CFG_FILE_PATH)
print("\t\twritten to '"+CFG_FILE_PATH+"'")

stop = time.perf_counter()
time_offline = stop-start
print("DONE: Runtime of "+str(time_offline)+"s")
print("--------------------------------------------------")

##### 