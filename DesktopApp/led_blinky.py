# File: led_blinky.py
# Description: Hello World application of the IoT World 
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import time
from machine import Pin

# Program entrance function
def main():
    """
    Main function
    """
    # Pin that integrated LED is connected to
    led_pin = Pin(13)
    
    # Set pin to be a digital output pin with value 0
    led_pin.init(mode=Pin.OUT, value=0)

    count = 0
    while count < 5:
        # Switch on the LED pin
        led_pin.value(1)
        print("Blink on")
        
        # Sleep for 1 second
        time.sleep(1)
        
        # Switch off the LED pin
        led_pin.value(0)
        print("Blink off")

        # Sleep for 1 second
        time.sleep(1)
        
        # Increment count
        count += 1

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
