# File: oled_buttons_example.py
# Description: User control using buttons on OLED FeatherWing 
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
from time import sleep
from machine import Pin
from neopixel import NeoPixel
from iot_app import IoTApp

        
# Globals
npm = None  # NeoPixel matrix object, used in a number of functions
count = 0   # Count to control how many times the press of Button A
            # is handled when the NeoPixel matrix is showing muted
            # white colour
            


# Handler for when Button A is pressed        
def button_a_handler(pin):
    # If the first NeoPixel is (0, 0, 0) then all NeoPixels are currently
    # off so set all NeoPixels to muted white (10, 10, 10)
    if npm[0] == (0, 0, 0):
        npm.fill((10, 10, 10))
        npm.write()

# Handler for when Button B is pressed        
def button_b_handler(pin):
    # Access global count variable
    global count
    
    # If the first NeoPixel is (10, 10, 10) then muted white is currently
    # shown on the NeoPixel matrix so set all NeoPixels to off (0, 0, 0)
    # and increment the count variable
    if npm[0] == (10, 10, 10):
        npm.fill((0, 0, 0))
        npm.write()
        count += 1

# Program entrance function
def main():
    """
    Main function
    """
    global npm
    
    # Pin 21 is connected to the NeoPixel FeatherWing via a jumper wire
    neopixel_pin = Pin(21)
    
    # Set pin 21 to be a digital output pin that is initially pulled down (off)
    neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)
    
    # Instantiate a NeoPixel obejct with the required NeoPixel FeatherWing pin, 
    # number of NeoPixels (4 x 8 = 32), bytes used for colour of each NeoPixel
    # and a timing value (keep as 1)
    
    IoTAppn = IoTApp(name="potato")
    
    npm = NeoPixel(neopixel_pin, 32, bpp=3, timing=1, app=IoTAppn)
    
    # Colours are set using a RGB channel tuple value with first element of the
    # tuple the red value (0..255), the second element the green value and the
    # third element the blue value, note: "black" uses tuple value (0, 0, 0)
    # whilst bright white use tuple value (255, 255, 255), "black" is actually
    # all NeoPixels switched off
    # 
    # *****************************************************************************
    # CAUTION - BRIGHT WHITE IS VERY BRIGHT, DO NOT LOOK DIRECTLY AT THIS FOR ANY
    # LENGTH OF TIME, PLEASE USE MUTED VALUES FOR COLOURS, USE A MAXIMUM OF 10 FOR
    # EACH COLOUR CHANNEL (THIS IS STILL QUITE BRIGHT)
    # *****************************************************************************
    #
    # Each NeoPixel can be changed using the [] indexing from 0..31, this splits
    # the matrix into 4 rows of 8 NeoPixels with the following indices:-
    #
    #      0  1  2  3  4  5  6  7
    #      8  9 10 11 12 13 14 15
    #     16 17 18 19 20 21 22 23
    #     24 25 26 27 28 29 30 31
    #
    # Note: index 0 is the NeoPixel furthest to the top left under the FeatherWing
    # text on the NeoPixel FeatherWing board
    #
    # Show red at top left, green at top right, blue at bottom left and white at
    # bottom right
    
    # Button A is connected to pin 15 on the Huzzah32 Feather, set this pin to be a
    # digital input
    button_a_pin = Pin(15)
    # Wire-up the function button_a_handler() as the interrupt handler for Button A
    #button_a_pin.irq(button_a_handler)
    
    # Button B is connected to pin 32 on the Huzzah32 Feather, set this pin to be a
    # digital input
    button_b_pin = Pin(32)
    # Wire-up the function button_b_handler() as the interrupt handler for Button B
    #button_b_pin.irq(button_b_handler)
    
    # Use NeoPixel.fill() method sets all NeoPixels to off
    npm.fill((0, 0, 0))
    # You must use NeoPixel.write() method when you want the matrix to change
    npm.write()
    
    # Run the program for 3 changes of NeoPixel matrix to show muted white
    while count < 3:
        sleep(0.1)
        
    # Colour all NeoPixels red just before exiting the program
    npm.fill((10, 0, 0))
    npm.write()

    # Wait for 2 seconds before exiting program
    sleep(2)
    
    # Switch off all the NeoPixels, good practice before program ends
    npm.fill((0, 0, 0))
    npm.write()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
