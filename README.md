# Pico-PIO-1602A-Display
MicroPython Library for RP2040 interface to 1602 parallel mode  display using PIO.

This Micropython library interfaces 1602 LCD display using 4 bit parallel to a Raspberry Pi PICO or
similar rp 2040 MPU.

The library implements a python class object  that the programmer uses to initialize, control and 
display text on the display.  Low level bit banging is handeled by the PIO code which is called 
by the developers application code.  No knowledge of PIO programming is required.

An example program is provided to demonstrate the creation and use of the display object and to 
demonstrate how to call object methods.  A full set of 1602 capabilities is implemented with the
exception of the read methods.  As a result, the library provides generious timings for the display
device to process the instructions.  It is my intention to implement read capabilities in future
versions to allow the busy flag reduce reliance on these timing instructions.

