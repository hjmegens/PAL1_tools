# general usage:
# if general .bin file provide start address
# python prg_to_wav.py -i VUTAPE.BIN -o vutape.wav -s 0000
# if commodore style .prg file
# python prg_to_wav.py -i first_example_first_book_of_KIM.prg -o first_example_first_book_of_KIM.wav --input_is_prg 

# import libs
import argparse
from scipy.io import wavfile
import numpy as np

# compute the checksum for the code
def compute_chsum(message):
    hexsymbols = '0123456789ABCDEF'
    chsum = 0

    #print(message)
    hexnum = -1
    for i in range(0,len(message),2):
        if message[i] not in hexsymbols:
            print("WARNING: not valid hex symbol")

        numchar1 = int('{:08b}'.format(ord(message[i]))[4:],2)
        numchar2 = int('{:08b}'.format(ord(message[i+1]))[4:],2)
        if ord(message[i]) < 0x41:
            numchar1 = '{:04b}'.format(numchar1)
        else:
            numchar1 += 9
            numchar1 = '{:04b}'.format(numchar1)
        if ord(message[i+1]) < 0x41:
            numchar2 = '{:04b}'.format(numchar2)
        else:
            numchar2 += 9
            numchar2 = '{:04b}'.format(numchar2)
    
        totnumchar = numchar1 + numchar2
        #print(message[i], message[i+1], totnumchar)
        chsum += int(totnumchar,2)

    return '{:04x}'.format(chsum)


# add 'bytes' in ascii to bitstring
def add_byte(bitstring,addchars):
    for character in addchars:
        bitstring += '{:08b}'.format(ord(character))[::-1]
    return bitstring

# check if id allowed
def check_ID(ID):
    hexsymbols = '0123456789ABCDEF'
    for character in ID:
        if character not in hexsymbols:
            print("WARNING: ID contains non hex symbols.")
    if ID == '00' or ID == 'FF':
        print("WARNING: values 0 and 0xFF are not allowed for the ID.")

# convert from byte code to ascii
def code_from_byte_to_ascii(code):
    asciicode = ''
    for byte in code:
        asciichar = '{:02x}'.format(byte)
        asciicode += asciichar.upper()
    return asciicode

def separate_code_and_start_addres(mc_bytes, is_prg, start_address):
    code = 0
    sa = 0
    if is_prg:
        code = mc_bytes[2:]
        sa = '{:04x}'.format(mc_bytes[1]*(16**2) + mc_bytes[0])
        sal = mc_bytes[0]
        sah = mc_bytes[1]
    elif (not is_prg) and (start_address != 'NA'):
        code = mc_bytes
        sa = start_address
    else:
        print("WARNING: no start address can be defined")
        code = mc_bytes
        sa = '0300'

    return (code, sa)


####################
# block arguments and parsing
parser = argparse.ArgumentParser( description='Convert binary PRG to WAV for PAL-1/KIM-1')
parser.add_argument("-i", "--input_prg_or_binary", help="myprogram.bin or myprogram.prg", type=str, nargs=1)
parser.add_argument("-b", "--bitdepth", help="currently only 16 bits supported",type=int, default=16)
parser.add_argument("-p", "--input_is_prg", help="if true no start address needed", action="store_true")
parser.add_argument("-n", "--program_name_id", help="two-character program id", type=str, default='01', nargs=1)
parser.add_argument("-s", "--start_address", help="start addres", type=str, default='NA')
parser.add_argument("-o", "--output", help="output WAV", type = str, default='out.wav')

args = parser.parse_args()

input_file = args.input_prg_or_binary[0]
is_prg = args.input_is_prg
bitdepth = args.bitdepth
ID = args.program_name_id
start_address = args.start_address
output_WAV = args.output
# end block args and parsing
####################

#open a binary file; note the code is expected to have
# two leading bytes indicating the address, in the 
# commodore 'PRG' file style
hexstringfh = open(input_file, 'rb')
hexstring = hexstringfh.read().hex()
hexstringfh.close()
mc_bytes = bytearray.fromhex(hexstring)

# generate separate code block and 
# start address
code, SA = separate_code_and_start_addres(mc_bytes, is_prg, start_address)
print("Start address: {}".format(SA))
# For now just 16 bits (32767 -32768); 
# maybe other encoding later. 
bits = bitdepth

# note that the only samplerate supported currently is 44100
# every bit, long or short, is 324 points, i.e. 7.35 ms.
oneshort = 6 * [-1*(2**(bits-1))] + 6 * [2**(bits-1)-1] 
onelong = 9 * [-1*(2**(bits-1))] + 9 * [2**(bits-1)-1]
zerobit = 18 * oneshort + 6 * onelong
onebit = 9 * oneshort + 12 * onelong

# create high and low adress byte
SAL = SA[2:]
SAH = SA[:2]
asciicode = code_from_byte_to_ascii(code)
print("asciicode: ", asciicode)
#ASCIICODE='A510A6118511861000'

# check if ID is allowed: should be hex and not include 0 or 0xFF
check_ID(ID)
print("ID is: ",ID)

# compute checksum; indeed this is a bit convoluted
# could have been done directly on the code: 
# chsumdirect = sum(mc_bytes)
# print('checksum directly from binary: {:04x}'.format(chsumdirect))
# but this script is primarily learning to understand the bits 
# and pieces of the cassette interface.

# compute checksum
chsum = compute_chsum(SAL+SAH+asciicode)
print('checksum based on ascii and back: {}'.format(chsum))

# separate low and high byte
# needs to be converted to uppercase
chsumH = chsum[:2].upper()
chsumL = chsum[2:].upper()

# set up bitstring, it starts with 100 "SYN" chars, 0x16
bitstring=100*'{:08b}'.format(0x16)[::-1]
# next is one '*' character
bitstring = add_byte(bitstring, '*')
# next is the id
bitstring = add_byte(bitstring, ID)
# then the address low byte
bitstring = add_byte(bitstring, SAL)
# followed by addres high byte
bitstring = add_byte(bitstring, SAH)
# next the code, in ascii
bitstring = add_byte(bitstring, asciicode)
# then a '/'
bitstring = add_byte(bitstring, '/')
# next the checksum low byte
bitstring = add_byte(bitstring,chsumL)
# followed by the checksum high byte
bitstring = add_byte(bitstring,chsumH)
# finally two EOT characters
bitstring= bitstring + 2 * '{:08b}'.format(0x4)[::-1]

# convert the string of bits to array
message_list = list()
for bit in bitstring:
    if bit == '1':
        message_list += onebit
    if bit == '0':
        message_list += zerobit

# define 4s worth of a no-sound leader and end in the WAV
leaderzero = 44100 * 4 * [0]
endzero = 44100 * 4 * [0]

# string everything together: 4 seconds no sound, followed by 
# the actual message, ended by 4 seconds of no-sound
total_vector = np.array(leaderzero + message_list + endzero, dtype='int'+str(bits))

# report total time of the WAV
print("WAV total time: {:.2f} seconds.".format(len(total_vector)/44100))

# write vector to WAV
wavfile.write(output_WAV, 44100, total_vector)
