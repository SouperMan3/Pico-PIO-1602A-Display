'''  1602A display Library
    use PIO to send data and commands to display
    in 4 bit data mode.
    
    write only, user defined chars not supported
    
    STATUS:
    initial testing works
'''
 
import time
from machine import Pin
import rp2

PIO_FREQ = 100000  # 10 us per cycle
# RW always Low (write)

@rp2.asm_pio(out_init=(rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW,rp2.PIO.OUT_LOW),
             sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_RIGHT, autopull=True,
            pull_thresh=4)

def send_nyble(): # output one nyble in tx_fifo at a time
    wrap_target()
    out(pins, 4)          [4] # data to out pins
    nop()        .side(0) [2] # enable = 1 cycle
    nop()        .side(1) [2] # Toggle enable to latch = 1 cycle
    nop()        .side(0) [7]   # Latch & delay >37 us = 5 cycles
    wrap()

class Disp1602():
    """Character LCD Display."""

    LCD_CHR = 1  # Character mode
    LCD_CMD = 0  # Command mode

    # LCD RAM address for 4 display lines
    LCD_LINES = (0x80,  0xC0,  0x94,  0xD4)
    LCD_ROW_OFFSETS = (0x00, 0x40, 0x10, 0x50)

    # Command constants
    LCD_CLEAR = 0x01
    LCD_CURSORSHIFT = 0x10
    LCD_DISPLAYCONTROL = 0x08
    LCD_HOME = 0x02
    LCD_SETDDRAMADDR = 0x80
    LCD_SETCGRAMADDR = 0x40
    LCD_SETENTRYMODE = 0x04

    # Control flags
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # Move flags
    LCD_DISPLAYMOVE = 0x08
    LCD_MOVELEFT = 0x00
    LCD_MOVERIGHT = 0x04
    
    # Entry flags
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYRIGHT = 0x00
    LCD_SHIFTINC  = 0x01
    LCD_SHIFTDEC = 0x00
    
    def __init__(self, smnum, ob, sb, cmd_pin, rows=2, cols=16):
        ''' constructor for 1 x 16 lines '''
        global PIO_FREQ
        out = Pin(ob, Pin.OUT)
        side = Pin(sb, Pin.OUT)
        self.sm = rp2.StateMachine(smnum, send_nyble, freq=PIO_FREQ, out_base=out, sideset_base=side) 
        self.sm.active(1)
        self.numrows = rows
        self.numcols = cols
        self.cmd = Pin(cmd_pin, Pin.OUT)      
        self.cmd.value(self.LCD_CMD)  # start in cmd mode
      
    def begin(self):  # perform the 1602 setup
        self.cmd.value(0)  # start in cmd mode
        time.sleep_ms(400)  # startup delay
        
        # setup display to 4 bit mode
        self.sendnyble(0x03)
        time.sleep_ms(5)
        self.sendnyble(0x03)
        time.sleep_ms(1)
        self.sendnyble(0x03)
        time.sleep_ms(1)
        self.sendnyble(0x02)   # 4 bit mode
   
        self.dctl = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        self.dmode = self.LCD_ENTRYLEFT | self.LCD_SHIFTINC
        
        self.sendcmd(0x28)    # 2 line mode / 5x8 char sz
        self.sendcmd(0x08)    # display on no cursor or blink
        self.sendcmd(0x0C)
        
        self.sendcmd(0x06)
        self.clear()
        
    def sendcmd(self, inst):
        ''' 1602 expects high nyble then low nyble'''
        self.cmd.value(0)
        self.sendbyte(inst)
        
    def senddata(self, data):
        ''' send all bytes in string '''
        self.cmd.value(1)
        for d in data:
            self.sendbyte(ord(d))
    
    def sendbyte(self, byte):
        ''' must set cmd or data before calling '''

        self.sendnyble(byte >> 4)
        self.sendnyble(byte & 0x0F)
        time.sleep_us(200)

    def sendnyble(self, nyb):
        self.sm.put(nyb)
        time.sleep_us(2)
               
    def clear(self):
        """Clear and home LCD display."""
        self.sendcmd(self.LCD_CLEAR)
        time.sleep(0.05)
        
    def home(self):
        ''' return cursor to 0,0 '''
        self.sendcmd(self.LCD_HOME)
        time.sleep(0.05)
        
    def enable(self, enable=True):
        ''' enable or disable display of chars '''
        if enable:
            self.dctl |= self.LCD_DISPLAYON
        else:
            self.dctl &= ~self.LCD_DISPLAYON
        
        self.sendcmd(self.DISPLAYCONTROL | self.dctl)
        
    def message(self, message, align=0):
        ''' display text 
            align: justify > 0 white space surround
                0 = no just
                1 = left just
                2 = center
                3 = right just
                
        must be at line start to work properly '''
        if align == 1:
            message = '{0:<{1}}'.format(message, self.numcols)
        elif align == 2:
            message = '{0:^{1}}'.format(message, self.numcols)
        elif align == 3:
            message = '{0:>{1}}'.format(message, self.numcols)
            
        self.senddata(message)          
    
    def move_left(self):
        ''' cursor left 1 pos '''
        inst = self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT
        self.sendcmd(inst)
    
    def move_right(self):
        ''' cursor right 1 pos '''
        inst = self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT
        self.sendcmd(inst)
    
    def set_cursor(self, line, col):
        '''move cursor to row , col '''
        if line >= self.numrows:
            line = self.numrows - 1
        
        inst = self.LCD_SETDDRAMADDR + (self.LCD_ROW_OFFSETS[line] + (col ))
        self.sendcmd(inst)
        time.sleep_ms(1)
    
    def set_line(self, line):
        ''' move cursor to line at col 0 '''
        inst = self.LCD_ROW_OFFSETS[line] + self.LCD_SETDDRAMADDR
        self.sendcmd(inst)
        time.sleep_ms(1)
    
    def show_blink(self, show=True):
        if show:
            self.dctl |= self.LCD_BLINKON
        else:
            self.dctl &= ~self.LCD_BLINKON
            
        self.sendcmd(self.dctl | self.LCD_DISPLAYCONTROL)
        time.sleep_ms(1)          
    
    def show_underline(self, show=True):
        if show:
            self.dctl |= self.LCD_CURSORON
        else:
            self.dctl &= ~self.LCD_CURSORON
            
        self.sendcmd(self.dctl | self.LCD_DISPLAYCONTROL)
        time.sleep_ms(1)
        
    def createChar(self, charnum, chararray):
        charnum &= 0x07   # only 8 custom chars
        addr = charnum << 3
#         time.sleep(1)
        print(hex(charnum), hex(addr), hex(self.LCD_SETCGRAMADDR | addr))
        self.sendcmd(self.LCD_SETCGRAMADDR | addr)
        time.sleep_us(100)
        self.cmd.value(1)  # data mode
        for i in range(8):
            self.sendbyte(chararray[i])
            time.sleep_us(100)
        
        