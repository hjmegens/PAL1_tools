# usage:
# python prg_to_ptp.py -i examples_kimtape/first_example_first_book_of_KIM.prg -o first_example_first_book_of_KIM.ptp
# python prg_to_ptp.py -i examples_kimtape/VUTAPE.BIN -b -s 0 -o vutape.ptp
# python prg_to_ptp.py -i examples_kimtape/ASTEROID.BIN -b -s 200 -o asteroid.ptp
# For the PTP format see Appendix F of the KIM manual

# import libs
import argparse

def write_out(outstring, fh):
    print(outstring)
    fh.write(outstring+'\n')

####################
# block arguments and parsing
parser = argparse.ArgumentParser( description='Convert binary PRG to PTP for PAL-1/KIM-1')
parser.add_argument("-i", "--input_prg_file", help="myprogram.prg", type=str, nargs=1)
parser.add_argument("-o", "--output", help="output PTP", type = str, default='out.ptp')
parser.add_argument("-b", "--input_is_bin", help="if true start address needed", action="store_true")
parser.add_argument("-s", "--start_address", help="start addres, in hex", type=str, default='NA')

args = parser.parse_args()

input_file = args.input_prg_file[0]
output_PTP = args.output
is_bin = args.input_is_bin
sa_provided = args.start_address
# end block args and parsing
####################

#open a binary file; note the code is expected to have
# two leading bytes indicating the address, in the 
# commodore 'PRG' file style
out_ptp = open(output_PTP,'w')
hexstringfh = open(input_file, 'rb')
hexstring = hexstringfh.read().hex()
hexstringfh.close()
mc_bytes = bytearray.fromhex(hexstring)

# separate code
code = mc_bytes[2:]

# and separate startaddress
startaddress = mc_bytes[1]*(16**2) + mc_bytes[0]

# update: now able to use bin file + address provided
if is_bin:

    # don't forget to provide a valid start address if bin!
    if sa_provided != 'NA':
        code = mc_bytes
        startaddress = int(sa_provided, 16)
        if startaddress > 65535 or startaddress <0:
            print("WARNING: illegal start address provided")
    else:
        print("WARNING: invalid address or file")

# determine the number of entire lines
numrecords = len(code) // 0x18

# for each entire line do:
for i in range(numrecords):
    
    # determine the address at the start of each line
    address = startaddress + i*0x18

    # format it to ascii
    addressstring = '{:04x}'.format(address).upper()
 
    # get checksum of the 18 bytes
    chsum = 0x18 + int(addressstring[:2],16) + int(addressstring[2:],16)
    
    # report the first part of the line
    record = ';18'+addressstring

    # get the part of the code for this line
    line = code[i*0x18:i*0x18+0x18]
    
    # for every byte do:
    for byte in line:

        # increase checksum
        chsum += byte

        # add the byte, converted to asccii, to the line
        record += '{:02x}'.format(byte).upper()

    # and end the line with the line specific checksum
    record += '{:04x}'.format(chsum).upper()
    write_out(record, out_ptp)

# when all entire lines done, we are now at this address:
address = startaddress + numrecords*0x18
addressstring = '{:04x}'.format(address).upper()

# keep score for the last line
totalnumrecords = numrecords

# something remains in the last line:
if len(code) % 0x18 > 0:

    # add one to the total number of lines
    totalnumrecords += 1

    # the code remaining in the last line:
    lastline = code[(numrecords*0x18):]
    numbyteslastline = len(lastline)

    # checksum of last line
    chsum = numbyteslastline + int(addressstring[:2],16) + int(addressstring[2:],16)

    # again, report first bytes
    record = ';{:02x}'.format(numbyteslastline).upper() + addressstring

    # and then every next byte:
    for byte in lastline:

        # turn to ascii and print
        record += '{:02x}'.format(byte).upper()

        # and keep score of checksum
        chsum += byte

    # report the last line's checksum
    record += '{:04x}'.format(chsum).upper()
    write_out(record, out_ptp)
    
# last line of the papertape reports only the number of records
# zero data bytes
record = ';00'
# number of records
record += '{:04x}'.format(totalnumrecords).upper()
# checksum of the line, should be same as number of records
record += '{:04x}'.format(totalnumrecords).upper()
write_out(record, out_ptp)

# and let's not forget to close the outfile
out_ptp.close()

