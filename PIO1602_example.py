'''  Test program for 1602A display Library
    uses PIO to send data and commands to display
    in 4 bit data mode
    
    STATUS:
    Basic tests works - need to test custom characters
'''
 
from machine import Pin
import time
import sys
import rp2
from pio_lcd import Disp1602

# bind 4 GPIOs to PIO out an a sideset to enable
datastart = 2
enable = 6
cmd = 7  # command data pin controlled outside of PIO

# 5x8 special clock bitmap custom chars
clockmap = ( (0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01),  # c0 vline
             (0x1F, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x1F),  # c1 rev c
             (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),  # c2
             (0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x1F),  # c3
             (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1F),  # c4
             (0x1F, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),  # c5
             (0x1F, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01),  # c6
             (0x1F, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11)   # c7
             )

# select custom chars to use for line 0 and line 1
clockchar = ((0x07, 0x04),  # 0 - C7 line 0  C4 line 1
             (0x00, 0x00),  # 1 - C0 both lines
             (0x01, 0x02),  # 2 - C1 line 0 C2 line 1
             (0x01, 0x03),  # 3  ...
             (0x04, 0x00),  # 4
             (0x05, 0x03),  # 5
             (0x02, 0x04),  # 6
             (0x06, 0x00),  # 7
             (0xFF, 0x04),   # 8  note FF use Capital O for line 0
             (0x07, 0x06)   # 9
            )
    

def show_digit(dsp, col, digit):  # diplay 2 line digit at col
    global clockchar
    ch = clockchar[digit]
    # move to col on 1st line
    dsp.set_cursor(0, col)
    # show top of char
    custom = ch[0]

    if custom == 0xFF:
        dsp.message("O", 0)
    else:
        dsp.cmd.value(1)
        dsp.sendbyte(custom)
    # move to col on 2nd line
    dsp.set_cursor(1, col)
    
    # show bottom character
    custom = ch[1]
    if custom == 0xFF:
        custom = 0x4F
        dsp.message("O", 0)
    else:
        dsp.cmd.value(1)
        dsp.sendbyte(custom)
        
''' Test the 1602A device '''
def main():
    global clockmap
    disp = Disp1602(0, datastart, enable, cmd)
    
    disp.begin()
    
    # load 8 custom characters from table
    for cnum in range(8):
        disp.createChar(cnum, bytearray(clockmap[cnum]))
    
    disp.clear()
    disp.cmd.value(0)
    disp.set_line(0)
   
    disp.show_underline(True)
    disp.senddata("1234567890")
    disp.show_blink(True)
    disp.set_cursor(1, 3)
    disp.message("testingy")
    time.sleep(1)
    
    disp.clear()
    disp.show_underline(False)
    disp.show_blink(False)
#     show_digit(disp, 0, 0)
    for n in range(10):
        show_digit(disp, n, n)
#     disp.sendbyte(0x07)
    for i in range(3):
        time.sleep(1)
        disp.move_right()
        
    for i in range(3):
        time.sleep(1)
        disp.move_left()

    
if __name__ == "__main__":
    main()
        
        