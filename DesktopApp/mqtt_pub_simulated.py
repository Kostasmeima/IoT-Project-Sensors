# File: mqtt_pub_simulated.py
# Description: Example code showing use of the simulated ESP32 MicroPython application
#              code with an MQTT publisher
# Author: Chris Knowles, University of Sunderland
# Date: Apr 2020

# Imports
from time import sleep
from machine import Pin
from neopixel import NeoPixel
from libs.iot_app import IoTApp
from libs.bme680 import BME680, OS_2X, OS_4X, OS_8X, FILTER_SIZE_3, ENABLE_GAS_MEAS

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
    AP_SSID = "Cisinau2Bucurest"
    AP_PSWD = "dwswow13V!"
    AP_TOUT = 5000
    MQTT_ADDR = "broker.hivemq.com"  # DNS of the public MQTT server
    MQTT_PORT = 1883

    # Some notes on the Hive MQTT public broker: be aware that the MQTT broker used (which
    # is located at "broker.hivemq.com") is a public broker and any topic you publish on
    # will be able to be subscribed to by anyone connected to this broker, the URL for the
    # Hive MQTT public broker web site is:-
    #
    #       https://www.hivemq.com/public-mqtt-broker/
    #
    # There are a few issues to address when using this broker:-
    # 1. It is public, do not use it for sensitive information
    # 2. You need to use unique topic names to ensure you do not clash with existing topics
    #    published to on the broker, this is almost impossible to ensure since you cannot
    #    access the topics being published, however, you should be able to come up with a
    #    pseudo-unique topic name, maybe use the same as below but change the "-00" part
    #    to a number associated with yourself, it is suggested that you look down the list
    #    of people on the CET235 module Canvas entry, count down to your name and use that
    #    as your unique number, so the 8th name would be "-08" and the twentieth name would
    #    be "-20" for instance, hopefully this will prevent clashes with topic names as you
    #    work on your solutions along side all the other students on the module
    # 3. Because the Hive MQTT public broker is beyond our control, it may disappear for
    #    shutdown and maintenance, it has not done in the time it has been used but this
    #    could happen (hopefully for short periods only), that bridge will be crossed if
    #    it should happen
    MQTT_TOPIC_1 = "uos/cet235-00/temperature/value"  # Topic name for temperature published
    MQTT_TOPIC_2 = "uos/cet235-00/time/value"  # Topic name for current published
        
    def init(self):
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
        # Initialise the BME680 driver instance with the I2C bus from the ProtoRig instance and
        # with the I2C address where the BME680 device is found on the shared I2C bus (0x76 hex,
        # 118 decimal), note: the I2C object is encapsulated in an I2CAdapter object, you do
        # not need to know anything further just that some device drivers require the I2C to be
        # provided in this way
        self.sensor_bme680 = BME680(i2c=self.rig.i2c_adapter, i2c_addr=0x76)

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
        self.npm.write()

        self.time_str = ""

        self.target_indicator = "N"
        self.temperature_target = None
        self.temperature_str = ""

        self.wifi_msg = "No WIFI"
        connect_count = 0
        # Try to connect to WiFi 5 times, if unsuccessful then only try again if button A on
        # the OLED is pressed
        while connect_count < 5 and not self.is_wifi_connected():
            self.oled_clear()
            self.wifi_msg = "Connect WIFI:{0}".format(connect_count + 1) 
            self.oled_text(self.wifi_msg, 0, 0)
            self.oled_display()
            self.connect_to_wifi(wifi_settings=(self.AP_SSID, self.AP_PSWD, True, self.AP_TOUT))
            connect_count += 1
            
        if self.is_wifi_connected():
            self.wifi_msg = "WIFI"
            # Register to the MQTT broker 
            self.register_to_mqtt(server=self.MQTT_ADDR, port=self.MQTT_PORT)
        else:
            self.oled_clear()
            self.wifi_msg = "No WIFI"
            self.oled_text(self.wifi_msg, 0, 0)
            self.oled_display()
            sleep(2)
        
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        self.oled_clear()

        # If sensor readings are available, read them once a second or so
        if self.sensor_bme680.get_sensor_data(temperature_target=self.temperature_target):
            tm_reading = self.sensor_bme680.data.temperature  # In degrees Celsius

            self.temperature_str = "{0:.2f}".format(tm_reading)

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

        # Get current date and time
        yr, mn, dy, dn, hr, mi, se, ms = self.rtc.datetime()

        # Display date on OLED
        output = "{0} {1:02d}-{2:02d}-{3}".format(self._DAY_NAMES[dn][0:3], dy, mn, yr)
        self.oled_text(output, 0, 2)

        # Display time on OLED
        self.time_str = "{0:02d}:{1:02d}:{2:02d}".format(hr, mi, se)
        output = "      {0}".format(self.time_str)
        self.oled_text(output, 0, 12)

        # Display WIFI message, temperature and target indicator on OLED
        output = "{0}  T:{1}c {2}".format(self.wifi_msg, self.temperature_str, self.target_indicator)
        self.oled_text(output, 0, 22)

        self.oled_display()

        if self.is_wifi_connected():
            # Publish a "uos/cet235-00/temperature/value" topic message (which uses the recorded
            # temperature from the BME680 sensor)
            self.mqtt_client.publish(self.MQTT_TOPIC_1, self.temperature_str)

            # Publish a "uos/cet235-00/time/value" topic message (which uses the current time from
            # the RTC)
            self.mqtt_client.publish(self.MQTT_TOPIC_2, self.time_str)

        sleep(1)

    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # In this specific implementation the deint() method does nothing, only included
        # for completeness sake
        pass

    def btnA_handler(self, pin):
        """
        This method overrides the inherited btnA_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        self.target_indicator = "H"
        self.temperature_target = 35.0

    def btnB_handler(self, pin):
        """
        This method overrides the inherited btnB_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        self.target_indicator = "L"
        self.temperature_target = 20.0

    def btnC_handler(self, pin):
        """
        This method overrides the inherited btnA_handler method which is provided by
        the inherited IoTApp class, you do not need to set up the pin used for the
        OLED FeatherWing button as this is done in the IoTApp class already for you
        """
        self.target_indicator = "N"
        self.temperature_target = None

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
    #   name: "MQTT Pub Sim", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to None which designates Button C on the OLED FeatherWing as not
    #                  used so it can be programmed
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="MQTT Pub Sim", has_oled_board=True, finish_button=None, start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
