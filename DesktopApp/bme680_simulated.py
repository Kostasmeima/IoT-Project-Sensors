# File: bme680_simulated.py
# Description: Example code showing use of the simulated ESP32 MicroPython application
#              code with a simulated BME680
# Author: Chris Knowles, University of Sunderland
# Date: Apr 2020

# Imports
from time import sleep
from machine import Pin
from neopixel import NeoPixel
from iot_app import IoTApp
from bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, ENABLE_GAS_MEAS
import pandas as pd
import datetime

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
        
        timer = 0
        self.timer = timer
        df = pd.DataFrame( columns= ['Temperature', 'Pressure', 'Humidity'])
        self.datapd= df
        
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
       
        # Initialise the BME680 driver instance with the I2C bus from the ProtoRig instance and
        # with the I2C address where the BME680 device is found on the shared I2C bus (0x76 hex,
        # 118 decimal), note: the I2C object is encapsulated in an I2CAdapter object, you do
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
        
        # Pin 21 is connected to the NeoPixel FeatherWing via a jumper wire, note: the
        # instance of pin 21 is taken from the property ProtoRig instance 
        self.neopixel_pin = self.rig.PIN_21
        
        # Set pin 21 to be a digital output pin that is initially pulled down (off)
        self.neopixel_pin.init(mode=Pin.OUT, pull=Pin.PULL_DOWN)
        
        # Instantiate a NeoPixel object with the required NeoPixel FeatherWing pin, 
        # number of NeoPixels (4 x 8 = 32), bytes used for colour of each NeoPixel
        # and a timing value (keep as 1)
        # THE ONLY DIFFERENCE IS app=self addition. It tells to look in the code,
        # rather than the real HW
        self.npm = NeoPixel(self.neopixel_pin, 32, bpp=3, timing=1, app=self)
        
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
         
        # Use NeoPixel.fill() method sets all NeoPixels to off, uses the npm property from this
        # object instance
        self.npm.fill((0, 0, 0))
        # You must use NeoPixel.write() method when you want the matrix to change
        # This does nothing actually, is left here from the original HW code and
        # for similarity reasons
        self.npm.write()

        self.target_indicator = "N"
        self.temperature_target = None
        self.pressure_target = None
        self.humidity_target = None
        self.gas_resistance_target = None

    def loop(self):
        
        df = self.datapd
        
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True (which in the case of this implementation is when Button C on 
        the OLED FeatherWing is pressed)
        """
        self.oled_clear()

        # If sensor readings are available, read them once a second or so
        if self.sensor_bme680.get_sensor_data(temperature_target=self.temperature_target,
                                              pressure_target=self.pressure_target,
                                              humidity_target=self.humidity_target,
                                              gas_resistance_target=self.gas_resistance_target):
            tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius
            pa_reading = self.sensor_bme680.data.pressure     # In Hectopascals (1 hPa = 100 Pascals)
            rh_reading = self.sensor_bme680.data.humidity     # As a percentage (ie. relative humidity)

            # The VOC gas sensor needs a short time (around 20-30 milliseconds) to warm up,
            # until then output a message to state it is stablising, the gas reading is provided in
            # electrical resistance (ohms) measured across the sensor and is not very useful on its own,
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
                output = "stablising"
            self.oled_text(output, 0, 20)
            
            ct = datetime.datetime.now()
            
            output = str(ct)
        
            
            self.oled_text(output, 80, 20)

            # Display current target indicator on OLED
            self.oled_text(self.target_indicator, 120, 20)
            
            
            

            # Change the colours of the NeoPixels on the NeoPixel FeatherWing to match the current
            # temperature reading from the BME680 sensor, make this quite sensitive since there
            # will only be a small change in temperature, make all blue NeoPixels equivalent to
            # a reading of 20c and all red NeoPixels equivalent to a reading of 35c, then set the
            # colour channels using the actual read temperature
            min_tm = 20
            max_tm = 35

            # Clamp actual read temperature to minimum and maximum temperature range
            if tm_reading < min_tm:
                tm_reading = min_tm
            elif tm_reading > max_tm:
                tm_reading = max_tm

            # Calculate the factor the actual temperature reading contributes to the colour channels
            tm_factor = (tm_reading - min_tm) / (max_tm - min_tm)

            # Blue channel is maximum (255) when actual temperature is at 20c, make sure this value
            # ends up an integer
            blue_channel = int(255 * (1 - tm_factor))

            # Red channel is maximum (255) when actual temperature is at 35c, make sure this value
            # ends up an integer
            red_channel = int(255 * tm_factor)

            # Use NeoPixel.fill() method to set NeoPixels to the calculated colour channels, note: the
            # green colour channel is not used (it remains 0)
            self.npm.fill((red_channel, 0, blue_channel))
            # You must use NeoPixel.write() method when you want the matrix to change
            self.npm.write()
            
            timer = self.timer
            
            if timer<11:
                self.npm[0]=(255,0,0)
            else:
                self.npm[0]=(0,255,0)
                
            # measurements
            
            df = df.append({'Temperature': tm_reading  , 'Pressure':  pa_reading , 'Humidity' : rh_reading }, ignore_index=True)
            self.datapd=df

        # Display the sensor readings on the OLED screen 
        self.oled_display()

        # Take readings once every second or so
        sleep(1)
        
        timer+=1
        
        self.timer = timer
       
     
        
    
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # Make sure the NeoPixel matrix is displaying black colour
        self.npm.fill((0, 0, 0))
        self.npm.write()
        self.datapd.to_csv(r'Datapoints.csv')
        timer = self.timer
        # opening the file in read mode
        


    def btnA_handler(self, pin):
        """
        This method overrides the inherited btnA_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        self.target_indicator = "H"
        self.temperature_target = 35.0
        self.pressure_target = 1100
        self.humidity_target = 90
        self.gas_resistance_target = 16000

    def btnB_handler(self, pin):
        """
        This method overrides the inherited btnB_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        self.target_indicator = "L"
        self.temperature_target = 20.0
        self.pressure_target = 980
        self.humidity_target = 5
        self.gas_resistance_target = 1000

    def btnC_handler(self, pin):
        """
        This method overrides the inherited btnA_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        self.target_indicator = "N"
        self.temperature_target = None
        self.pressure_target = None
        self.humidity_target = None
        self.gas_resistance_target = None

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
    #   name: "BME680 Sim'ed", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to None which designates Button C on the OLED FeatherWing as not
    #                  used so it can be programmed
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="BME680 Sim'ed", has_oled_board=True, finish_button=None, start_verbose=True)
    # Add log here!!!!!
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
    aaa=1
    
