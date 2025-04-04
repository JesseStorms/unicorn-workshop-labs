# This code is the property of Mantra Information Security and is provided 
# solely for use within the x86/x64 Reverse Engineering training course or
# one of its related workshops.
# It is confidential and proprietary information and should not be distributed
# or shared with anyone else. Any unauthorized distribution, reproduction, 
# or use of this code is strictly prohibited.
#
# Mantra Information Security
# https://mantrainfosec.com
#

from unicorn import *
from unicorn.x86_const import *
import struct

def hook_mem_access(uc, access, address, size, value, user_data):
    if access == UC_MEM_WRITE:
        print(">>> Memory is being WRITE at 0x%x, data size = %u, data value = 0x%x" \
                %(address, size, value))
    else:   # READ
        print(">>> Memory is being READ at 0x%x, data size = %u" \
                %(address, size))

def hook_code(uc, address, size, user_data):
    print("[*] Current RIP: 0x{}, instruction size = 0x{}".format(address, size))
    
# Read the ELF binary
with open("01caesar", "rb") as f:
    binary = f.read()

# Set the memory address where the code will be loaded (base address)
ADDRESS = 0x100000

# Create an instance of the Unicorn Engine emulating x64
uc = Uc(UC_ARCH_X86, UC_MODE_64)

# Map memory for the code
uc.mem_map(ADDRESS, 2*1024*1024)  # 2 MB

# Write the ELF binary to the memory
uc.mem_write(ADDRESS, binary)

# Set the string and offset values in memory
input_str = b"Jxkqox Fkclojxqflk Pbzrofqv"
offset = 3
length = len(input_str)
uc.mem_write(ADDRESS + 0x4000, input_str)  # Address where input_str is stored (binary 16K, string at 17K)
uc.reg_write(UC_X86_REG_RDI, ADDRESS + 0x4000)  # Set the first argument (address of the string) / depends on the calling convention (assuming we're using SYstemV AMD64 ABI)
uc.reg_write(UC_X86_REG_RSI, offset)  # Set the second argument (offset)
uc.reg_write(UC_X86_REG_RDX, length)  # Set the third argument (length)

uc.reg_write(UC_X86_REG_RSP, ADDRESS+0x6000)  # Set the stack (RSP)

uc.hook_add(UC_HOOK_MEM_READ, hook_mem_access)
uc.hook_add(UC_HOOK_MEM_WRITE, hook_mem_access)
uc.hook_add(UC_HOOK_CODE, hook_code, None, ADDRESS + 0x1189, ADDRESS + 0x12AC)
# Emulate code execution
try:
    uc.emu_start(ADDRESS + 0x1189, ADDRESS + 0x12ac)  # Address of the caesar_cipher call / find ENDBR64 and RET
    # Read the result from memory (assuming the C program prints the result)
    result = uc.mem_read(ADDRESS + 0x4000, len(input_str)).decode("utf-8")
    print(f"Encoded string: {result}")

except UcError as e:
    print("Error: %s" % e)