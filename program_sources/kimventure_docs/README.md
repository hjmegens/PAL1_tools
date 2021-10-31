
<img src="misc_figures/kimventure.jpg" alt="fig1" style="width: 600px;"/>
Collection of source files for the KIM-Venture game, derived from the audio tape.

The audio tape was retrieved from [Hans Otten's knowledge base](http://retro.hansotten.nl/6502-sbc/kim-1-manuals-and-software/kim-1-software/kim-venture/):

The audio tape was subsequently converted to .wav format:

<code>ffmpeg -i kimventure.m4a -ac 2 -f wav kimventure.wav</code>

Analysis of the audio content was done using the wav_to_prg.py script as follows:

<code>python ../PAL1_tools/wav_to_prg.py -i kimventure.wav -o kimventure.prg  -p --make_plots</code>


