# convert a .wav file for KIM-1 to binary or prg
# very much a work in progres

# import libs
import sys
import argparse
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt

# plot specgram, if --make_plots
def plot_specgram(signal_data, sampling_frequency,outfilestub):
    # Plot the signal read from wav file
    plt.figure(figsize=(16, 8), dpi=300)

    plt.title('Spectrogram of a wav file for KIM-1')
    plt.specgram(signal_data[1:],Fs=sampling_frequency,scale='dB',cmap='Spectral')
    plt.xlabel('Time')
    plt.ylim(0,5000)
    plt.ylabel('Frequency')
    plt.savefig(outfilestub + '_specgram.png')

# plot the FFT, if --make_plots
def plot_fft(sound, sampling_freq, outfilestub):
    fft_spectrum = np.fft.rfft(sound)
    freq = np.fft.rfftfreq(sound.size, d=1./sampling_freq)
    fft_spectrum_abs = np.abs(fft_spectrum)
    plt.figure(figsize=(16, 5), dpi=300)
    plt.plot(freq[freq<4500], fft_spectrum_abs[freq<4500])
    plt.xlabel("frequency, Hz")
    plt.ylabel("Amplitude, units")
    plt.ylim(0,1.1*fft_spectrum_abs[freq>1000].max())
    plt.xlim(1000,4500)
    plt.savefig(outfilestub + '_fft.png')

# output some diagnostic plot of the waveform
def plot_start(starttime,time,sound,outfilestub,title):
    newvec = (time>starttime) & (time<(starttime+0.02))
    plt.figure(figsize=(16, 5), dpi=300)
    plt.plot(time[newvec], sound[newvec])
    plt.title(title)
    plt.savefig(outfilestub + '_start_waves_short.png')

# for printed output of the content of the wav
def create_header(width):
    header = ''
    for i in range(width):
        rest = i % 10
        if rest == 0:
            header += '|'
        else:
            header += '-'
    header += '|'
    header = '    \t' + header
    return header

# return a bit based on frequency counts
def returnbit(count2400,count3700,ishyper):
    kimbit = 0
    time2400 = count2400/2400
    time3700 = count3700/3700
    # note: had to add this because for hypertape high-freq counts may 
    # be underestimated, this is something that needs further attention!
    #print(count2400,count3700)
    if ishyper and (count2400 == 1 or count3700 == 1):
        time3700 *= 2
    # compute ratio; should be 2 if binary 1; a bit more permissive, this 
    # is a critical parameter
    if time3700 > 0 and (time2400/time3700 > 1.5):
        kimbit = 1
    # this can't be zero; warning nevertheless.
    elif time3700 == 0:
        print("WARNING: potentially mangled bit!\nreturning 0 as default")
    # return single bit
    return kimbit

# compute the checksum for the code
def compute_chsum(message):
    hexsymbols = '0123456789ABCDEF'
    chsum = 0
    message_bytearray = bytearray()
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
        chsum += int(totnumchar,2)
        message_bytearray.append(int(totnumchar,2))

    return '{:04x}'.format(chsum),message_bytearray

# return data vector and sample rate from wav
def return_data_from_wav(input_file):

    wav = wavfile.read(input_file)
    samplerate = wav[0]
    data = wav[1]
    sound = ''
    # assuming mono, if stereo deciding which channel
    # note: there is a potential weakness; if mute channel
    # has still lots of noise it could be inadvertently selected
    # this needs some work to make full-proof. 
    if len(data.shape) == 2:
           maxsignal1 = data[:,0].max()
           maxsignal2 = data[:,1].max()
           if maxsignal1 >= maxsignal2:
               sound = data[:,0]
           else:
               sound = data[:,1]
    elif len(data.shape) == 1:
        sound = data
    maxsignal = sound.max()
    minsignal = sound.min()
    
    if minsignal >= 0:
        sound2 = list()
        for value in sound:
            sound2.append(value - int(0.5*maxsignal)+1)
        sound = np.array(sound2)
        minsignal = sound.min()
        maxsignal = sound.max()
    length = sound.shape[0] / samplerate # aantal seconden
    time = np.linspace(0., length, sound.shape[0])
    return sound,maxsignal,minsignal,time,samplerate

# only if debug, print stuff
def debug_timing(count2400, count3700, kimbit, cycleup):
    print("time: {:.4f}\ttime2400: {:4f}\ttime3700: {:4f}\tbit: {}".format(cycleup,count2400/(2*2400),count3700/(2*3700),kimbit))

# only if debug, print stuff
def debug_decoding(bytecounter, newbyte, hexbyte, cycleup):
    print("time: {:.4f}\tbyte {}: {}\tparity {}\tbin: {:08b}\thex: {}\tASCII: {}".format(cycleup, bytecounter, newbyte[:8][::-1], newbyte[7], int(hexbyte,16),hexbyte, chr(int(hexbyte,16))))

# make translation table for pretty printing
def make_transtable():
    transtable = dict()
    chars = '*0123456789ABCDEF/' + chr(0x16) + chr(0x4)
    symbols = '*0123456789ABCDEF/' + u'\u2416' + u'\u2404'
    for i,c in enumerate(chars):
        transtable[c] = symbols[i] 
    return transtable

# if new bit read, add it
def add_bit(totaltime,bitcounter, bytecounter, newbyte,charstring,cycleup,count2400, count3700, ishyper):
    kimbit = returnbit(count2400, count3700,ishyper)
    if debug:
        debug_timing(count2400,count3700,kimbit,cycleup)
    totaltime = totaltime + (count2400/(2400)) + (count3700/(3700))
    bitcounter += 1
    newbyte += str(kimbit)
    hexbyte='0'
    oldbyte='0'
    if bitcounter == 8:
        hexbyte = hex(int(newbyte[:7][::-1], 2))
        if debug:
            debug_decoding(bytecounter,newbyte,hexbyte,cycleup)
        charstring += chr(int(hexbyte,16))
        oldbyte = newbyte
        newbyte = ''
        bitcounter = 0
        bytecounter += 1
    return totaltime, bitcounter, bytecounter, newbyte, charstring, oldbyte

# detect leader sequence of SYN chars
def detect_leader(bytecounter, oldbyte, syncounter,bitcounter,newbyte,charstring, goodlock): 
    if bytecounter == 1 and oldbyte == '01101000' and bitcounter == 0:
        print("Succesfull lock on SYN char")
        syncounter += 1
    elif bytecounter == 1 and len(oldbyte) == 8 and oldbyte != '01101000':
        print("WARNING: first char is not SYN: {}".format(newbyte))
        print("trying to get a new lock")
        bitcounter = 7
        bytecounter -= 1 
        newbyte = oldbyte[1:]
        charstring = charstring[:-1]
    elif oldbyte == '01101000' and bitcounter == 0:
        syncounter += 1
    if syncounter > 15 and hex(int(oldbyte[::-1],2)) == '0x2a':
        print("succesful lock on leader sequence, found {:d} SYN chars".format(syncounter))
        goodlock = True
    return syncounter, bytecounter, bitcounter, newbyte, charstring, goodlock

####################
# block arguments and parsing
parser = argparse.ArgumentParser( description='Convert WAV to binary PRG for PAL-1/KIM-1')
parser.add_argument("-i", "--input", help="myrecording.wav", type=str, nargs=1)
parser.add_argument("-o", "--output", help="output PRG", type = str, default='test.prg')
parser.add_argument("-d", "--debug", help="debug", action="store_true")
parser.add_argument("-b", "--as_bin", help="output as BIN", action="store_true")
parser.add_argument("-p", "--as_prg", help="output as PRG", action="store_true")
parser.add_argument("-s", "--make_plots", help="output plots", action="store_true")
parser.add_argument("-f", "--hypertape", help="fast mode: hypertape", action="store_true")

args = parser.parse_args()

input_file = args.input[0]
output_prg = args.output
debug = args.debug
as_bin = args.as_bin
as_prg = args.as_prg
make_plots = args.make_plots
hyper = args.hypertape

if as_prg and as_bin:
    print("WARNING! (fatal): you should specify only one type of output format")
    sys.exit()
# end block args and parsing
####################

# convert wav to soundvector and samplerate
sound,maxsignal,minsignal,time,samplerate = return_data_from_wav(input_file)
if make_plots:
    plot_specgram(sound,samplerate,output_prg.split('.')[0])
    plot_fft(sound, samplerate, output_prg.split('.')[0])

# initialize a bunch of vars

count2400 = 0
count3700 = 0
newbit = 'no'
totaltime = 0
firsttime = 0
lasttime = 0
bitcounter = 0
bytecounter = 0 
newbyte = ''
charstring = ''
allshort = list()
alllong = list()
lastsignal = 0
triggerup = 0
triggerdown = 0
cycledown = 0
cycleup = -1
prevhightime = -1
cycletime = 0
syncounter = 0
allmessages = list()
goodlock = False
lastgoodpeak = 0

min3700 = 2
min2400 = 1
minfreq3700 = 3200
minfreq2400 = 2100
maxfreq2400 = 2600
maxfreq3700 = 4000
if hyper:
    min3700 = 0
    min2400 = 0
    minfreq3700 = 3100
    maxfreq2400 = 2900

# go through every timepoint in sound vector
for i,x in enumerate(sound):
    # for the time being the script uses default trigger levels
    # note: consider making this dynamic, and/or add hysteresis
    triggerlevel = 0.5
    if x > triggerlevel * maxsignal or x < triggerlevel * minsignal:
        
        if x > triggerlevel * maxsignal and triggerup == 0:
            
            cycleup = time[i]
            triggerup = 1
            triggerdown = 0

        if x < triggerlevel * maxsignal and triggerdown == 0:
            cycledown = time[i]
            triggerdown = 1
        
        lastsignal = x

        if triggerup == 1 and triggerdown == 1 and cycleup > 0: 

            if firsttime == 0:
                firsttime = time[i]
            if lasttime < time[i]:
                lasttime = time[i]

            halfcycletime = cycledown - cycleup
            cycletime = cycleup - prevhightime
            prevhightime = cycleup
            triggerup = 0
            triggerdown = 0
            hertz = (1/cycletime)
            if hyper:
                hertz = (0.5/halfcycletime)
            if debug:
                print(hertz)
            # if within high-freq signal level, and shift from low freq
            if hertz > minfreq3700 and hertz < maxfreq3700 and newbit == 'yes':
                betweengoodpeaks = lastgoodpeak - cycleup
                lastgoodpeak = cycleup
                # evaluate if sufficient good signal seen to call bit
                if count3700 > min3700 and count2400 > min2400 and betweengoodpeaks < (3*(1/2400)):

                    # add bit
                    totaltime,bitcounter, bytecounter,newbyte,charstring,oldbyte = add_bit(totaltime,bitcounter,bytecounter, newbyte,charstring, cycleup, count2400, count3700,hyper)

                    # problems locking on to SYN character are dealt with here
                    # resetting counters if necessary to get another try at next bit
                    syncounter, bytecounter, bitcounter, newbyte, charstring, goodlock = detect_leader(bytecounter, oldbyte, syncounter, bitcounter, newbyte, charstring, goodlock)
                   
                    if bitcounter == 0:
                        oldbyte = ''
                    # only if --make_plots
                    if make_plots:
                        if syncounter == 1 and bitcounter == 0:
                            offset = 9*((count2400/(2400)) + (count3700/(3700)))
                            title = 'Start first SYN'
                            plot_start(cycleup-offset,time,sound,output_prg.split('.')[0]+'{:.4f}'.format(cycleup),title)
                        # plot the start of the sequence for diagnostic purposes
                        if goodlock and len(charstring) == 101 and bitcounter == 0:
                            title='At the start of the message'
                            plot_start(cycleup,time,sound,output_prg.split('.')[0]+'{:.4f}'.format(cycleup),title)
                        
                # if not meeting proper criteria, warn for possible problems
                else:
                    print("WARNING: possible mangled/skipped bit at time {:.3f} \nor larger gap in message.".format(cycleup))
                    if debug:
                        title = 'Possible mangled/skipped bit'
                        offset = 9*((count2400/(2400)) + (count3700/(3700)))
                        plot_start(cycleup-offset,time,sound,output_prg.split('.')[0]+'{:.4f}'.format(cycleup),title)
                    if goodlock:
                        allmessages.append(charstring)
                    syncounter, bytecounter, bitcounter, newbyte, charstring,goodlock = 0,0,0,'','',False
                    
                # re-initialize counts    
                count3700 = 1
                count2400 = 0

                # re-initialize variable that keeps track of shifting from high to low freq
                newbit = 'no'
                
                # keep track of frequency in the high-pitch class  
                allshort.append(hertz)

            # if high frequency but no shift to low freq detected prior, just countup
            elif hertz > minfreq3700 and hertz < maxfreq3700:
                lastgoodpeak = cycleup
                count3700 += 1
                allshort.append(hertz)
            # if low frequency, countup, and detect shift to low freq
            elif hertz <= maxfreq2400 and hertz > minfreq2400:
                lastgoodpeak = cycleup
                newbit = 'yes'
                count2400 += 1
                alllong.append(hertz)

        prevhighlowtime = time[i]

# finish the last one
# note: for now there's a bug because the last cycle in the 2400 hz frame
# isn't counted. Since the last bit is supposed to be 0 anyway, there is 
# no consequence. But in a next version this needs to be addressed. 
totaltime,bitcounter, bytecounter, newbyte, charstring,hexbyte = add_bit(totaltime,bitcounter, bytecounter,newbyte,charstring,cycleup,count2400,count3700,hyper)

# print bytes to screen
transtable = make_transtable()
if goodlock:
    allmessages.append(charstring)

width = 60
header = create_header(width)

print("Number of messages found: {:d}".format(len(allmessages)))
for m,charstring in enumerate(allmessages):
    print('\nbytes in the .wav file:\n'+header)
    for i in range(0,len(charstring),width):
        print("{:4d}\t".format(i),end='')
        partstring = charstring[i:i+width]
        for c in partstring:
            if c in transtable.keys():
                print(transtable[c],end='')
            else:
                print('.')
        print()
    print(header.replace('|','-'))

    # get message from bytes
    message = charstring.split('*')[1]
    message = message[2:].split('/')[0]

    # write binary
    if len(allmessages) > 1:
        output_file = output_prg + '_{:d}'.format(m)
    else:
        output_file = output_prg
        
    computed_checksum,message_bytearray = compute_chsum(message)
    outbytearrayfh = open(output_file,'wb')

    if as_bin:
        outbytearrayfh.write(message_bytearray[2:])
    elif as_prg:
        outbytearrayfh.write(message_bytearray)
    else:
        print("WARNING: no output generated, specify format")
    outbytearrayfh.close()
    print('computed checksum: {}'.format(computed_checksum.upper()))

# print out some information
print("\n\nfirst signal: {:.2f}\nlast signal: {:.2f}".format(firsttime, lasttime))

print("totaltime, estimated from waves: {:.2f}".format(totaltime))

print("short pulses, estmate of hz: {:.2f}".format(np.mean(np.array(allshort))))
print("long pulses, estmate of hz: {:.2f}".format(np.mean(np.array(alllong))))
