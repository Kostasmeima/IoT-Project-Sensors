# File: ppw1_iot_sample.py
# Description: Sample code for PPW1 script to run on the IoT Prototype Rig
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import os
from time import sleep
from libs.iot_app import IoTApp
from libs.bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, ENABLE_GAS_MEAS
from neopixel import NeoPixel
from machine import Pin

# Classes
class MainApp(IoTApp):
    """
    This is your custom class that is instantiated as the main app object instance,
    it inherits from the supplied IoTApp class found in the libs/iot_app.py module
    which is copied when the Huzzah32 is prepared.
    This IoTApp in turn encapsulates an instance of the ProtoRig class (which is 
    found in libs/proto_rig.py) and exposes a number of properties of this ProtoRig
    instance so you do not have to do this yourself.
    Also, the IoTApp provides an execution loop that can be started by calling the
    run() method of the IoTApp class (which is of course inherited into your custom
    app class). All you have to do is define your program by providing implementations
    of the init(), loop() and deinit() methods.
    Looping of your program can be controlled using the finished flag property of
    your custom class.
    """
    def init(self):
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
        # Pin 21 is connected to the NeoPixel FeatherWing via a jumper wire, note: the
        # instance of pin 21 is taken from the property ProtoRig instance 
        self.neopixel_pin = self.rig.PIN_21
        
        # Set pin 21 to be a digital output pin that is initially pulled down (off)
        self.neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)
        
        # Instantiate a NeoPixel object with the required NeoPixel FeatherWing pin, 
        # number of NeoPixels (4 x 8 = 32), bytes used for colour of each NeoPixel
        # and a timing value (keep as 1)
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
        self.npm = NeoPixel(self.neopixel_pin, 32, bpp=3, timing=1)

        # Set the IoTApp real-time clock property using the date and time:-
        #
        #   5th March 2019 (Tuesday) 9:00am and 0 seconds 0 microseconds
        #
        # Use a tuple that contains:-
        #   (year, month, day, day number, hour, minute, seconds, microseconds)
        #
        # Day number starts at Monday (day number 0), note: that the date and time can be
        # set using the method datetime() once the RTC instance has been instantiated (the
        # tuple to pass to this datetime() method is in the same form as the one described
        # above, note: default date and time is 1/1/2000 0:0:0:000000, you will see a time
        # slightly after this as it takes a few seconds for the first time to display
        self.rtc.datetime((2019, 3, 5, 1, 9, 0, 0, 0))
        
        # Instantiate a BME680 object and configure it using the obtain_sensor_bme680()
        # method
        self.obtain_sensor_bme680()
        
        # Name of the file to write to the Huzzah32's root file system
        self.file_name = "access_data.csv"
        
        # If the file access_data.csv already exists on the root of the Huzzah32's file system then
        # first remove it (otherwise it will be appended to since the file is openned using
        # the "w+" flag, use the file_exists() method to check this and then remove if
        # necessary
        if self.file_exists(self.file_name):
            os.remove(self.file_name)
        
        # Open file for appending, note you could open the file simply for writing using the
        # flag "w" but then if a file of the same name is already on the file system it will
        # always be overwritten (so be careful)
        self.file = open(self.file_name, "w+")
        
        # The self.access flag is used to control the period during which an access is being undertaken 
        # in the controlled area, Flase means there is no access at this time, True is the reverse, above
        # string self.access_str is chnaged from empty to "ACCESS" for display on the OLED screen during
        # an access period, the self.warning string is changed from empty to "GREEN" when an access is
        # less than 5 seconds, to "AMBER" when after 5 seconds but less tahn 10 seconds and "RED" after
        # 10 seconds, this is also displayed on the OLED screen
        self.access = False
        self.access_str = ""
        
        # This counter is used to track the amount of time in seconds that an access period has lasted, it
        # is reset to zero at the end of any access, if the access has lasted 5 seconds or less then the
        # NeoPixel matrix shows green LEDS, if the access has lasted over 5 seconds but below 10 seconds
        # then the NeoPixel matrix shows orange/amber LEDS and if the access has lasted 10 seconds or longer
        # then the NeoPixel matrix shows red LEDs, if there is currently no access period then the NeoPixel
        # matrix has no LEDs showing
        self.count = 0

        # Use NeoPixel.fill() method sets all NeoPixels to off, uses the npm property from this
        # object instance
        self.npm.fill((0, 0, 0))
        # You must use NeoPixel.write() method when you want the matrix to change
        self.npm.write()

    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        # Clear the OLED screen buffer
        self.oled_clear()

        # If sensor readings are available, read them once a second or so
        if self.sensor_bme680.get_sensor_data():
            tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius 
            rh_reading = self.sensor_bme680.data.humidity     # As a percentage (ie. relative humidity)
                
            # Current date and time taken from the real-time clock
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]

            # If there is an access period then write the current BME680 data to a single line in the
            # access_data.csv file with each sensor value as the comma separated values in the form:-
            #
            #       timestamp, temperature, humidity
            #
            # where timestamp is of the form:-
            #
            #       YYYY-MM-DD|hh:mm:ss
            #
            # the date and time for this timestamp is taken from the self.rtc real-time clock instance that
            # is available in the IoTApp class (and therefore also in your class)
            #
            # Note: the \n at the end of each data line string is the new line character to ensure the
            # access_data.csv file has each sensor data readings on separate lines
            # 
            # Also, show the correct colour LEDs on the NeoPixel matrix depending upon how long the access
            # period has currently lasted.
            #
            # Finally, increment the self.count property to indicate that a further second of time has passed
            # during this access period
            if self.access:
                # Format timestamp
                timestamp = "{0}-{1}-{2}|{3}:{4}:{5}".format(year, month, day, hour, minute, second)

                # Format line of data
                data_line = "{0},{1:.2f},{2:.2f}\n".format(timestamp, tm_reading, rh_reading)
            
                # Write data line to the access_data.csv file
                self.file.write(data_line)
                
                # Set correct colour for NeoPixel matrix LEDS and correct access warning string
                led_colour = (0, 10, 0)  # Assume green colour
                if self.count > 4 and self.count < 9:
                    led_colour = (10, 7, 0)  # Set colour to orange/amber
                elif self.count >= 9:
                    led_colour = (10, 0, 0)  # Set colour to red
                    
                # Show current LEDs colour on NeoPixel matrix
                self.npm.fill(led_colour)
                self.npm.write()

                # Increment seconds counter
                self.count += 1
                    
            # Display the current date, time, sensor readings and access information on the OLED screen, only
            # display access information though if an access period is currently active
            output = "{0}/{1}/{2}".format(day, month, year)
            self.oled_text(output, 0, 0)
            output = "{0}:{1}:{2}".format(hour, minute, second)
            self.oled_text(output, 0, 8)
            output = "T:{0:.2f}c H:{1:.2f}%".format(tm_reading, rh_reading)
            self.oled_text(output, 0, 16)
            if self.access:
                output = "{0}: {1}".format(self.access_str, self.count)
                self.oled_text(output, 0, 24)
                
        # Display the sensor readings on the OLED screen 
        self.oled_display()

        # Try to take readings and display once every second or so
        sleep(1)
    
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # Clear the NeoPixel matrix
        self.npm.fill((0, 0, 0))
        self.npm.write()

        # If an access period is currently active then write to the access_data.csv file that it
        # is now stopped and also the length of the access period in seconds
        if self.access:
            # Current date and time taken from the real-time clock to record as stop date and time
            # for this access period
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]
            
            date_str = "{0}/{1}/{2}".format(day, month, year)
            time_str = "{0}:{1}:{2}".format(hour, minute, second)

            # Write to file, note: self.count is approximately the number of seconds that this access
            # period lasted
            self.file.write("{0},{1},{2},{3}\n".format("ACCESS-STOPPED", date_str, time_str, self.count))

        # Make sure the access_data.csv file is closed
        self.file.close()
        
    def obtain_sensor_bme680(self):
        """
        Use this method to obtain an fully configured BME680 sensor object instance and have
        this assigned to the property self.sensor_bme680
        """
        # Initialise the BME680 driver instance with the I2C bus from the ProtoRig instance and
        # with the I2C address where the BME680 device is found on the shared I2C bus (0x76 hex,
        # 118 decimal), note: the I2C object is encapulated in an I2CAdapter object, you do
        # not need to know anything further just that some device drivers require the I2C to be
        # provided in this way
        self.sensor_bme680 = BME680(i2c=self.rig.i2c_adapter, i2c_addr = 0x76)
        
        # These calibration data can safely be commented out if desired, the oversampling settings
        # can be tweaked to change the balance between accuracy and noise in the data, the values
        # provided are a good balance and are the recommended settings for your work
        self.sensor_bme680.set_temperature_oversample(OS_8X)
        self.sensor_bme680.set_humidity_oversample(OS_2X)
        self.sensor_bme680.set_filter(FILTER_SIZE_3)
        
    def file_exists(self, file_name):
        """
        Returns True if the file (does not work with directories) with the supplied name
        exists in the current directory, otherwise returns False
        """
        # Get the name of all files in the current directory on the Huzzah32's file system
        # using the os.listdir() function
        file_names = os.listdir()
        
        # Return True if supplied file name is in the files list, otherwise return False
        return file_name in file_names

    def btnA_handler(self, pin):
        """
        This method overrides the inherited btnA_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        # If an access period is not currently active then write to the access_data.csv file that
        # one has started, also update access information to indicate that the access period has
        # started
        if not self.access:
            # Current date and time taken from the real-time clock to record as start date and time
            # for this access period
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]
            
            date_str = "{0}/{1}/{2}".format(day, month, year)
            time_str = "{0}:{1}:{2}".format(hour, minute, second)

            # Write to file
            self.file.write("{0},{1},{2}\n".format("ACCESS-STARTED", date_str, time_str))
        
            # Update access information
            self.access = True
            self.access_str = "ACCESS"
            self.count = 0
        
    def btnB_handler(self, pin):
        """
        This method overrides the inherited btnB_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        # If an access period is currently active then write to the access_data.csv file that it
        # is now finished and also the length of the access in seconds, also update NeoPixel matrix
        # and access information to indicate that the access period has stopped
        if self.access:
            # Current date and time taken from the real-time clock to record as stop date and time
            # for this access period
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]
            
            date_str = "{0}/{1}/{2}".format(day, month, year)
            time_str = "{0}:{1}:{2}".format(hour, minute, second)

            # Write to file, note: self.count is approximately the number of seconds that this access
            # period lasted
            self.file.write("{0},{1},{2},{3}\n".format("ACCESS-STOPPED", date_str, time_str, self.count))
        
            # Update access information
            self.access = False
            self.access_str = ""

            # Clear the NeoPixel matrix
            self.npm.fill((0, 0, 0))
            self.npm.write()
            
    def process_access_data(self):
        """
        Parse the recorded access data from the access_data.csv file and generate textual output for each access period.
        """
        access_periods = []
        current_access = None
        with open("access_data.csv", "r") as file:
            reader = csv.reader(file)
            for row in reader:
                event_type, timestamp, *data = row
                timestamp = datetime.strptime(timestamp, "%Y-%m-%d|%H:%M:%S")
                
                if event_type == "ACCESS-STARTED":
                    current_access = {"start_time": timestamp, "readings": []}
                elif event_type == "ACCESS-STOPPED" and current_access is not None:
                    current_access["end_time"] = timestamp
                    access_periods.append(current_access)
                    current_access = None
                elif current_access is not None:
                    current_access["readings"].append((timestamp, *data))
        
        for access in access_periods:
            duration = (access["end_time"] - access["start_time"]).total_seconds()
            print("Start date and time:", access["start_time"])
            print("End date and time:", access["end_time"])
            print("Approximate number of seconds:", duration)
            print("Recorded readings during the access period:")
            for reading in access["readings"]:
                print("Timestamp:", reading[0], "Temperature:", reading[1], "Humidity:", reading[2])
            print()
            

# Program entrance function
def main():
    """
    Main function, this instantiates an instance fo your custom class (where you can
    initialise your custom class instance to how you wish your app to operate) and
    then executes the run() method to get the app running
    """
    # Instantiate an instance of the custom IoTApp class (MainApp class) with the following
    # property values:-
    #
    #   name: "PPW1 Sample", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="PPW1 Sample", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
