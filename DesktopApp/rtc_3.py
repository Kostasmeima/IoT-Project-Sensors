# File: rtc_3.py
# Description: Sample code for Week 5 Task 3
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import os
from time import sleep
from iot_app import IoTApp
from bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, ENABLE_GAS_MEAS

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
        # Set the IoTApp real-time clock property using the date and time:-
        #
        #   31st December 2018 (Monday) 23:59pm and 55 seconds 0 microseconds
        #
        # Use a tuple that contains:-
        #   (year, month, day, day number, hour, minute, seconds, microseconds)
        #
        # Day number starts at Monday (day number 0), note: that the date and time can be
        # set using the method datetime() once the RTC instance has been instantiated (the
        # tuple to pass to this datetime() method is in the same form as the one described
        # above, note: default date and time is 1/1/2000 0:0:0:000000, you will see a time
        # slightly after this as it takes a few seconds for the first time to display
        self.rtc.datetime((2018, 12, 31, 0, 23, 59, 55, 0))
        
        # Instantiate a BME680 object and configure it using the obtain_sensor_bme680()
        # method
        self.obtain_sensor_bme680()
        
        # Name of the file to write to the Huzzah32's root file system
        self.file_name = "rtc_3.csv"
        
        # If the file rtc_3.csv already exists on the root of the Huzzah32's file system then
        # first remove it (otherwise it will be appended to since the file is openned using
        # the "w+" flag, use the file_exists() method to check this and then remove if
        # necessary
        if self.file_exists(self.file_name):
            os.remove(self.file_name)
        
        # Open file for appending, note you could open the file simply for writing using the
        # flag "w" but then if a file of the same name is already on the file system it will
        # always be overwritten (so be careful)
        self.file = open(self.file_name, "w+")

        # Counter to count 10 sensor data readings written to rtc_3.csv file 
        self.count = 0
    
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        # Check to see if 10 data readings have been taken, if so then finish the app and return
        # from the loop() method
        if self.count >= 100:
            self.finish()
            return
            
        self.oled_clear()

        # If sensor readings are available, read them once a second or so
        if self.sensor_bme680.get_sensor_data():
            tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius 
            pa_reading = self.sensor_bme680.data.pressure     # In Hectopascals (1 hPa = 100 Pascals)
            rh_reading = self.sensor_bme680.data.humidity     # As a percentage (ie. relative humidity)

            # The VOC gas sensor needs a short time (aorund 20-30 milliseconds) to warm up,
            # until then output a message to state it is stablising, the gas reading is provided in
            # electrical resistance (ohms) measrued across the sensor and is not very useful on its own,
            # it needs to be compared to previous readings to make any use of this value, it is included
            # here to show how to read it but you will not be directly using this data in the future
            if self.sensor_bme680.data.heat_stable:
                gr_reading = self.sensor_bme680.data.gas_resistance
            else:
                gr_reading = None
                    
            output = "{0:.2f}c, {1:.0f}hpa".format(tm_reading, pa_reading)
            self.oled_text(output, 0, 0)
               
            output = "{0:.2f}%rh".format(rh_reading)
            self.oled_text(output, 0, 10)
                
            # The VOC gas sensor needs a short time (aorund 20-30 milliseconds) to warm up,
            # until then output a message to state it is stablising
            if gr_reading:
                output = "{0:.0f}ohms".format(gr_reading)
            else:
                output = "***stablising****"            
            self.oled_text(output, 0, 20)
            
            # Write the current BME680 data to a single line in the rtc_3.csv file with each sensor value
            # as the comma separated values in the form:-
            #
            #       timestamp, temperature, pressure, humidity, gas
            #
            # timestamp is of the form:-
            #
            #       YYYY-MM-DD|hh:mm:ss
            #
            # the date and time for this timestamp is taken from the self.rtc real-time clock instance that
            # is available in the IoTApp class (and therefore also in your class)
            #
            # Note: the \n at the end of each data line string is the new line character to ensure the
            # data.csv file has each sensor data readings on separate lines, also ensure that if the gas
            # reading is None (i.e. not yet ready) then record the value 0 for this
            gr_reading = gr_reading if gr_reading else 0.0
            
            # Current date and time taken from the real-time clock
            now = self.rtc.datetime()
            year = now[0]
            month = now[1]
            day = now[2]
            hour = now[4]
            minute = now[5]
            second = now[6]

            # Format timestamp
            timestamp = "{0}-{1}-{2} , {3}:{4}:{5}".format(year, month, day, hour, minute, second)

            # Format line of data
            data_line = "{0},{1:.2f},{2:.0f},{3:.2f},{4:.0f}\n".format(timestamp, tm_reading, pa_reading,
                                                                       rh_reading, gr_reading)
            
            # Write data line to the rtc_3.csv file
            self.file.write(data_line)

            # Increment the counter if a reading is taken
            self.count += 1
                
        # Display the sensor readings on the OLED screen 
        self.oled_display()

        # Try tp take readings once every second or so
        sleep(1)
    
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # Make sure the rtc_3.csv file is closed
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
        self.sensor_bme680.set_humidity_oversample(OS_2X)
        self.sensor_bme680.set_pressure_oversample(OS_4X)
        self.sensor_bme680.set_temperature_oversample(OS_8X)
        self.sensor_bme680.set_filter(FILTER_SIZE_3)
        
        # This specifies that you wish to use the VOC gas measuring sensor, use DISABLE_GAS_MEAS
        # disable the VOC gas sensor (remember to import this value if you need it)
        self.sensor_bme680.set_gas_status(ENABLE_GAS_MEAS)

        # Up to 10 heater profiles can be configured, each with their own temperature and duration
        # eg.  
        #    sensor.set_gas_heater_profile(200, 150, nb_profile = 1)  # Set profile 1
        #    sensor.select_gas_heater_profile(1)  # Select profile 1
        # You are not using a custom profile here, just the default profile and using direct values
        # for the heater used on the gas sensor, the values provided are a good balance and are the
        # recommended settings for your work
        self.sensor_bme680.set_gas_heater_temperature(320)
        self.sensor_bme680.set_gas_heater_duration(150)
        self.sensor_bme680.select_gas_heater_profile(0)  # Default to settings given above
        
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
    #   name: "RTC 3", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="RTC 3", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
