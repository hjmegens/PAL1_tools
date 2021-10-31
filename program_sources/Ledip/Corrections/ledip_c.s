;**********************************************
;**                                          **
;**  LEDIP (Line Editor Program)             **
;**  Version 4K                              **
;**  Copyright 1978 by Kiumi Akingbehin      **
;**                                          **
;**********************************************

; Zero Page Scratchpad memory
	ASCBUM .equ $e2
	ASCBU3 .equ $e1
	ASCBU2 .equ $e0
	ASCBUL .equ $df
	HEXBUH .equ $de
	HEXBUL .equ $dd
	STADH  .equ $dc
	STADL  .equ $db
	LOCCH  .equ $da
	LOCCL  .equ $d9
	TEMPR  .equ $d8
	CHCC   .equ $d7
	MBEGH  .equ $d6
	MBEGL  .equ $d5
	MENDH  .equ $d4
	MENDL  .equ $d3
	MDESH  .equ $d2
	MDESL  .equ $d1
	
	.org  $2000
	
CSTAT	cld
		jsr CRLF
		jsr CRLF
		ldy #$ee

CSTATL 	lda STADO - $ee,y
		jsr OUTCH
		iny 
		bne CSTATL

RSTAD 	jsr RDASC
		jsr HCHK4
		bcs RSTADL
		jsr CRLF
		lda #'H'
		jsr OUTCH
		lda #$21
		jsr OUTCH
		jmp CSTAT

RSTADL 	jsr CVAH
		jsr CRLF
		lda HEXBUL
		sta STADL
		sta LOCCL
		lda HEXBUH
		sta STADH
		sta LOCCH

WSTAT 	cld
		lda #2
		sta CHCC
		jsr CRLF
		lda #$2f
		jsr OUTCH
		jsr RDASC
		jsr DCHK4
		bcs AL8
		jmp CMHD

AL8 	jsr CVAH
		lda HEXBUL
		ldy #1
		sta (LOCCL),y
		cmp (LOCCL),y
		beq AL3
	
AL4 	jmp INVM2

AL3 	lda HEXBUH
		iny
		sta (LOCCL),y
		cmp (LOCCL),y
		bne AL4
		jsr SPACE

RVASC 	jsr GETCH
		cmp #$08
		bne RVASC1
		lda CHCC
		cmp #2
		beq RVASC
		dec CHCC
		bne RVASC
	
RVASC1 	inc CHCC
		bne RVASC2
	
INVL 	jsr CRLF
		lda #'L'
		jsr OUTCH
		lda #$21
		jsr OUTCH
		jmp WSTAT

RVASC2 	cmp #$0D
		beq RVASC4
		ldy CHCC
		sta (LOCCL),y
		cmp (LOCCL),y
	
AL2 	bne AL4
		beq RVASC

RVASC4 	lda CHCC
		cmp #3
		bne LADJ
	
LDEL 	jsr HEXST

LDEL1 	jsr CMPHL
		beq AL10
		jsr LNCHK
		bcs AL7

AL10 	jmp WSTAT

AL7 	beq LDEL2
		jsr INCHB
		jmp LDEL1
	
LDEL2 	ldy #0
		lda (HEXBUL),y
		sta TEMPR
		jsr MOV3
		jsr LSTLC
		beq LDEL3
		jsr MOV4
		jsr MOVMB
	
LDEL3 	jsr DCLC
		jmp WSTAT
	
LADJ 	lda CHCC
		ldy #0
		sta (LOCCL),y
		cmp (LOCCL),y
		bne AL2
		jsr HEXST

LADJ1 	jsr CMPHL
		bne LADJ2
		jsr INCLC
		jmp WSTAT

LADJ2 	jsr LNCHK
		bcs AL9
		jmp LINS

AL9 	beq CMPLL
		jsr INCHB
		jmp LADJ1

CMPLL 	ldx #0
		lda (LOCCL,x)
		cmp (HEXBUL,x)
		beq LADJ3
		bcs LADJ4
		bcc LADJ5 

LADJ3 	jsr MOV1
		jsr MOVMB
		jmp WSTAT
	
LADJ4 	ldx #0
		lda (LOCCL,x)
		sbc (HEXBUL,x)
		sta TEMPR
		jsr MOV5
		jsr MOVMB
		jsr MOV3
		jsr LSTLC    ; was lsr
		bne LADJ46
		jsr INCLC
		jmp LADJ47

LADJ46 	jsr INCLC
		clc
		lda MENDH
		sta MDESH
		lda MENDL
		adc TEMPR
		bcc LADJ43
		inc MDESH
		beq AL6

LADJ43 	sta MDESL
		jsr MOVMR

LADJ47 	jsr MOV1
		jsr MOVMB
		ldy #0
		sec
		lda LOCCL
		sbc (LOCCL),y
		bcs LADJ44
		dec LOCCH

LADJ44  clc
		adc TEMPR
		sta LOCCL
		bcc LADJ45
		inc LOCCH
		beq AL6

LADJ45 	jmp WSTAT

AL6  	jmp INVM2

LADJ5 	sec
		ldy #0
		lda (HEXBUL),y
		sbc (LOCCL),y
		sta TEMPR
		jsr MOV3
		lda HEXBUH
		sta MDESH
		lda HEXBUL
		clc
		ldx #0       ; was lda
		adc (LOCCL,x)
		bcc LADJ51
		inc MDESH
		beq AL6

LADJ51 	sta MDESL
		jsr LSTLC
		beq LADJ52
		jsr MOVMB

LADJ52 	jsr MOV1
		jsr MOVMB
		jsr DCLC
		jmp WSTAT
	
LINS 	jsr MOV5           ; was jmp
		jsr MOVMB
		lda HEXBUL
		sta MBEGL
		lda HEXBUH
		sta MBEGH
		jsr MOV33
		jsr MOV52
		lda MDESL
		sec
		sbc #1
		bcs LINS1
		dec MDESH

LINS1 	sta MDESL
		jsr INCLC
		jsr MOVMR
		jsr MOV1
		jsr MOVMB
		jmp WSTAT

CMHD 	lda ASCBUM
		and #%11011111
		cmp #'E'
		beq EXIT
		cmp #'F'
		beq FILE
		cmp #'T'
		beq TEXT
		cmp #'L'
		beq LIST
		cmp #'C'
		beq CLEAR
		nop
		nop
		nop
		jmp INVC

EXIT 	jsr CRSEN
		lda #$20 ; was ldy
		pha 
		lda #$3C
		pha
		php
		jmp $1000

CLEAR 	jsr GETCH
		jsr CRSEN
		jmp CSTAT

FILE 	jsr CRSEN
		ldy #$ea
	
FILE1 	lda FTAB-$ea,y
		jsr OUTCH ; was omitted
		iny
		bne FILE1
		jsr CRLF
		lda STADH
		jsr OUTBYT
		lda STADL
		jsr OUTBYT
		lda #'-'
		jsr OUTCH
		lda LOCCH ; was omitted
		jsr OUTBYT ; was omitted
		lda LOCCL
		jsr OUTBYT
		
ECMD 	jmp WSTAT
	
TEXT 	jsr CRSEN
		jsr CLHS

TEXT1 	jsr CMPHL
		bne TEXT2
		jsr CRLF
		jmp WSTAT

TEXT2 	jsr DPASC
		lda #$7f
		jsr OUTCH
		jsr INCHB
		jmp TEXT1

LIST 	jsr CRSEN
		jsr HEXST

LIST1 	jsr CMPHL
		beq ECMD
		ldy #2
		lda(HEXBUL),y
		jsr OUTBYT
		dey
		lda (HEXBUL),y
		jsr OUTBYT
		jsr SPACE
		jsr DPASC
		jsr INCHB
		JMP LIST1

INVM1 	pla
		pla
INVM2 	jsr CRLF
		lda #'M'
		jsr OUTCH
		lda #$21
		jsr OUTCH
		jmp WSTAT

INVC 	jsr CRLF
		lda #'C'
		jsr OUTCH
		lda #$21
		jsr OUTCH
		jmp WSTAT

; Subroutines in alph. order

ABIAS 	cmp #$3a
		bcs  ABIAS1
		sbc #$2f
		rts

ABIAS1 	sbc #$37
		rts

CLHS 	jsr CRLF
		jsr CRLF
	
HEXST 	lda STADL
		sta HEXBUL
		lda STADH
		sta HEXBUH
		rts

CMPHL 	lda HEXBUL ; was HEXBUH
		cmp LOCCL
		bne CMPHL1
		lda HEXBUH
		cmp LOCCH
	
CMPHL1 	rts

CRSEN 	jsr GETCH
		cmp #$0d
		beq CRSEN1
		pla
		pla
		jmp INVC

CRSEN1 	jsr CRLF
		rts
	
CVAH 	ldy #2
		ldx #4

CVAH1 	lda ASCBUM-4,x
		jsr ABIAS
		asl 
		asl 
		asl 
		asl 
		sta TEMPR
		dex
		lda ASCBUM-4,x
		jsr ABIAS
		clc
		adc TEMPR
		sta HEXBUH-2,y
		dex
		dey
		bne CVAH1
		rts

DCLC 	sec
		lda LOCCL
		sbc TEMPR
		sta LOCCL
		bcs DCLC1
		dec LOCCH

DCLC1 	rts
	
DPASC 	ldy #3

DPASC1 	lda (HEXBUL),y
		jsr OUTCH
		iny
		tya
		ldx #0
		cmp (HEXBUL,x)
		bne DPASC1
		jsr CRLF
		rts

HCHK4 	ldy #$ff
		jmp CHEK1

DCHK4 	ldy #0

CHEK1 	ldx #4

CHEK2 	lda ASCBUM-4,x
		cpy #0
		beq DCHK  ; was bne

HCHK 	cmp #$47
		bcs ECHK1
		cmp #$41
		bcs ECHK2

DCHK 	cmp#$3a
		bcs ECHK1
		cmp#$30
		bcs ECHK2

ECHK1 	clc	
		rts

ECHK2 	dex
		bne CHEK2

ECHK 	rts

INCHB 	ldx #0
		lda (HEXBUL,x) ; was HEXBUH
		clc
		adc HEXBUL
		sta HEXBUL
		bcc INCHB1
		inc HEXBUH
		beq INCLC2
	
INCHB1 	rts

INCLC 	ldx #0
		lda (LOCCL,x)
		clc
		adc LOCCL
		sta LOCCL
		bcc INCLC1
		inc LOCCH
		bne INCLC1
		
INCLC2 	jmp INVM1

INCLC1 	rts

LNCHK 	ldy #2
		lda (LOCCL),y
		cmp (HEXBUL),y
		bcc LNCHK1
		beq LNCHK2
	
LNCHK1 	rts
	
LNCHK2 	dey
		lda (LOCCL),y
		cmp (HEXBUL),y
		rts

LSTLC 	lda MBEGL
		cmp LOCCL
		beq LSTLC1
		rts

LSTLC1 lda MBEGH
		cmp LOCCH
		rts

MCHEK 	lda MENDL
		cmp MBEGL
		bne ENDMC
		lda MENDH
		cmp MBEGH
	
ENDMC 	rts

MOVMB 	ldy #0
MOVM1 	lda (MBEGL),y
		sta (MDESL),y
		cmp (MDESL),y
		beq AL1
	
AL5 	jmp INVM1

AL1 	jsr MCHEK
		beq ENDM
		inc MBEGL
		bne MOVM3
		inc MBEGH

MOVM3 	inc MDESL
		bne MOVM1
		inc MDESH
		bne MOVM1
		beq AL5

ENDM 	rts

MOVMR 	ldy #0

MOVR1 	lda (MENDL),y
		sta (MDESL),y
		cmp (MDESL),y
		bne AL5
		jsr MCHEK
		beq ENDMR
		sec
		lda MENDL
		sbc #1
		sta MENDL
		bcs MOVR3
		dec MENDH
MOVR3 	sec
		lda MDESL
		sbc #1
		sta MDESL
		bcs MOVR1
		dec MDESH
		bcc MOVR1
		
ENDMR 	rts

MOV1 	jsr MOV2
		jsr MOV4
		rts

MOV2 	lda LOCCH
		sta MBEGH
		sta MENDH
		lda LOCCL
		sta MBEGL
		clc
		ldx #0
		adc (LOCCL,x)
		bcc MOV21
		inc MENDH
		bne MOV21
		pla
		pla
	
AL11 	jmp INVM1

MOV21 	sec
		sbc #1
		bcs MOV22
		dec MENDH
	
MOV22 	sta MENDL
		rts

MOV3 	lda HEXBUH
		sta MBEGH
		lda HEXBUL
		clc
		ldx #0
		adc (HEXBUL,x)
		bcc MOV31
		inc MBEGH
		beq AL11

MOV31 	sta MBEGL

MOV33 	lda LOCCH
		sta MENDH
		lda LOCCL
		sec
		sbc #1
		bcs MOV32
		dec MENDH

MOV32	sta MENDL
		rts
		
MOV4 	lda HEXBUL
		sta MDESL
		lda HEXBUH
		sta MDESH
		rts

MOV5 	jsr MOV2 

MOV52 	lda LOCCH
		sta MDESH
		ldx #0
		clc
		lda LOCCL
		adc (LOCCL,x)
		bcc MOV51
		inc MDESH
		beq AL11

MOV51 	sta MDESL
		rts

RDASC 	ldx #4

RDASC1 	jsr GETCH
		sta ASCBUM-4,x
		dex
		bne RDASC1
		rts

SAVR 	sta MBEGL
		stx MENDL
		sty MDESL
		rts

CRLF 	jsr SAVR
		jsr $1e2f
		jmp RESR
	
GETCH 	jsr SAVR
		jsr $1e5a
		jmp RESR1
	
OUTCH 	jsr SAVR
		jsr $1ea0
		jmp RESR

SPACE  	jsr SAVR
		jsr $1e9e
		jmp RESR
		
OUTBYT 	jsr SAVR         ; spotted by Hans, was jmp
		jsr $1e3b

RESR 	lda MBEGL
RESR1 	ldx MENDL ; was lda
		ldy MDESL ; was lda
		nop
		nop
		nop
		rts
		
STADO 	.byte 'STARTING ADDRESS? ' ; change to caps, add space
FTAB 	.byte '00D1-00E2'
		.byte $0d, $00, $0a, $00
		.byte '2000-249D' ; change 2490 to 249D
		
		.end
	
	
