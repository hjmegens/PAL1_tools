../VASM/vbcc/bin/vasm6502_oldstyle -Fbin -dotdir blink.s -o blink.bin -cbm-prg -L blink.lst


python ../PAL1_tools/prg_to_ptp.py -i blink.bin -o blink.ppt

#ascii-xfr -s -l 100 -c 10 blink.ppt >/dev/ttyUSB0
