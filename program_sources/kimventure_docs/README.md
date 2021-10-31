<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/misc_figures/kimventure.jpeg?raw=true" alt="fig1" style="width: 500px;"/>

### KIM-Venture: analysis of audio tape ###

A collection of source files for the KIM-Venture game, derived from the audio tape, and a brief analysis of the audio tape content. 

The audio tape was retrieved from [Hans Otten's knowledge base](http://retro.hansotten.nl/6502-sbc/kim-1-manuals-and-software/kim-1-software/kim-venture/):

The audio tape was subsequently converted to .wav format:

<code>ffmpeg -i kimventure.m4a -ac 2 -f wav kimventure.wav</code>

Analysis of the audio content was done using the wav_to_prg.py script as follows:

<code>python ../PAL1_tools/wav_to_prg.py -i kimventure.wav -o kimventure.prg  -p --make_plots</code>

As described in the manual, the audio tape consists of 5 parts. In the specgram this is clearly shown:

<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/original_audio/diagnostic_figures/kimventure_specgram.png?raw=true" alt="fig1" style="width: 800px;"/>

The quality of the audio seems very good, as seen from the FFT analysis:

<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/original_audio/diagnostic_figures/kimventure_fft.png?raw=true" alt="fig1" style="width: 800px;"/>

The first block in the audio stream consists only of SYN characters. My first prototype conversion script couldn't pick it up though, because of a first mangled bit that resulted in a frameshift (note: horizontal axis shows time, in sec):
<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/original_audio/diagnostic_figures/kimventure8.9519_start_waves_bewaren.png?raw=true" alt="fig1" style="width: 800px;"/>

I've used this little issue to include a synchronization step in my current script to get a good lock on the SYN character and validate the leader sequence.

The four valid code blocks each show 100 SYN characters and the checksums computed match the ones reported in the byte stream. 
<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/misc_figures/byte_stream1.png?raw=true" alt="fig1" style="width: 600px;"/>

Some notable differences exist between some of the papertape circulating and the audio source; for the first block this includes the addition of two bytes in KIM-1 reserved space in the audio: 

```
diff VENTUREPPT000.TXT kimventure.ptp_0 
10,11c10,12
< ;1700D8494B90204C91354D534C4692204893334D5152449F009F08A9
< ;00000A000A

> ;1800D8494B90204C91354D534C4692204893334D5152449F009F73091D
> ;0100F0180109
> ;00000B000B
```

<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/misc_figures/byte_stream2.png?raw=true" alt="fig1" style="width: 600px;"/>

```
diff VENTUREPPT100.TXT kimventure.ptp_1
11c11
< ;1801F09500E8E0EFD0F7600000000000000000|38E90DAA4A2901A80970
---
> ;1801F09500E8E0EFD0F760700093196C196718|38E90DAA4A2901A80B90
17c17
< ;18028047A649A53E38F54C853E20EC01A5401C*E3A649CAD0DEA5450C31
---
> ;18028047A649A53E38F54C853E20EC01A54010*E3A649CAD0DEA5450C25
```
In the 2nd code block, this specifically pertains the stack space, indicated by a manually inserted '|' at location 1FF. My guess is that for creating the commercial audio tape, the code was loaded into a KIM-1 by papertape (or manually punched in?), and subsequently recorded on a master audio tape from there, thereby including what was in the stack at the time. 

The most important difference here may be the one indicated by a '\*' inserted manually here. In the pdf of the manual, the location 0x28F

<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/misc_figures/Difference_at_0x28F.png?raw=true" alt="fig1" style="width: 400px;"/>

It seems here the audio tape may be correct (?) - the PDF is really ambigious but tentatively a '0' seems more likely than a 'C'. 

<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/misc_figures/Byte_stream3.png?raw=true" alt="fig1" style="width: 600px;"/>

Further small differences in block3

```
diff VENTUREPPT1780.TXT kimventure.ptp_2
5c5
< ;0417E0024C8B0101D5
---
> ;0717E0024C8B0100000001D8
```

<img src="https://github.com/hjmegens/PAL1_tools/blob/main/program_sources/kimventure_docs/misc_figures/Byte_stream4.png?raw=true" alt="fig1" style="width: 600px;"/>
  
For the scoring code, again there stack space in the audio format is different from the PPT, but, interestingly, in the papertape there is another block of apparently reserved 0s that are filled with information in the audio, presumably this is the part that holds the result of the scoring code.

```
diff VENTURESCORERPPT100.TXT kimventure.ptp_3
10,11c10,11
< ;1801D802000000000000000000000000000000000000000000000000F3
< ;1801F00000000000000000000000000000000090D1A27CA562D0CB062A
---
> ;1801D802A90D10CAE445D0DDB54FD565F0D795658A10BBA63FB5010D48
> ;1801F09500E8E0EFD0F760700093196C19671890D1A27CA562D0CB0DBD
```

For more information on the program source and game play, see the [Github page of Mark Bush](https://github.com/markbush/KIM-Venture).


