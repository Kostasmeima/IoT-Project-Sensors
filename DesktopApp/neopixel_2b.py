# File: neopixel_2b.py
# Description: Sample code for Week 3 Task 2b 
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
from time import sleep
from machine import Pin
from neopixel import NeoPixel

def display_centre(npm, colour):
    npm[11] = colour
    npm[12] = colour
    npm[19] = colour
    npm[20] = colour
    npm.write()

# Program entrance function
def main():
    """
    Main function
    """
    # Pin 21 is connected to the NeoPixel FeatherWing via a jumper wire
    neopixel_pin = Pin(21)
    
    # Set pin 21 to be a digital output pin that is initially pulled down (off)
    neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)
    
    # Instantiate a NeoPixel obejct with the required NeoPixel FeatherWing pin, 
    # number of NeoPixels (4 x 8 = 32), bytes used for colour of each NeoPixel
    # and a timing value (keep as 1)
    npm = NeoPixel(neopixel_pin, 32, bpp=3, timing=1)
    
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
    
    # Make sure all the NeoPixels start off, this is good practice
    npm.fill((0, 0, 0))  # "black" ie. all NeoPixels switched off
    npm.write()
    
    # Flash centre colours 15 times
    for _ in range(15):    
        # Draw 4 centre NeoPixels in red (10, 0, 0)
        display_centre(npm, (10, 0, 0))
        sleep(0.3)
    
        # Draw 4 centre NeoPixels in muted white (10, 10, 10)
        display_centre(npm, (10, 10, 10))
        sleep(0.3)
    
        # Draw 4 centre NeoPixels in blue (0, 0, 10)
        display_centre(npm, (0, 0, 10))
        sleep(0.3)
    
    # Switch off all the NeoPixels, good practice before program ends
    npm.fill((0, 0, 0))
    npm.write()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
