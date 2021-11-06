; blink.s - blink 8 LEDs on PAL-1's expansion 6532 RIOT

  .org $200         ; start at 0x200
  lda #$FF          
  sta $1701         ; set A data register to output
loop: 
  lda #$55
  sta $1700         ; output 01010101 on A data register
  jsr sec           ; wait 1 sec
  lda #$AA          
  sta $1700         ; output 10101010 on A data register
  jsr sec           ; wait 1 sec
  jmp loop          ; and back to loop

; subroutine to wait one second 
sec:
  lda #$9C          ; count back from 156
  sta $1706         ; through RIOT interval timer
  lda #0
  sta $0            ; initialize extra counter
clk:
  lda $1707         ; get timer status
  beq clk           ; check if counted back to 0 yet
  lda #$9C       
  sta $1706         ; re-initialize RIOT 64 counter register
  inc 0             ; increase extra counter by 1
  lda 0              
  cmp #$64          ; extra counter already 100?
  bne clk           ; if not, extra interval timer cycle
  rts               ; return from subroutine
