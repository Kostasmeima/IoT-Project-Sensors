# File: mqtt_sub_simulated.py
# Description: Example code showing use of the simulated ESP32 MicroPython application
#              code with an MQTT subscriber
# Author: Chris Knowles, University of Sunderland
# Date: Apr 2020

# Imports
import random
from time import sleep
from libs.iot_app import IoTApp
        
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
    MQTT_ADDR = "broker.hivemq.com"  # DNS of the public MQTT broker
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
    MQTT_TOPIC_1 = "uos/cet235-00/temperature/value"  # Topic name for published temperature
    MQTT_TOPIC_2 = "uos/cet235-00/time/value"  # Topic name for published current time
        
    def init(self):
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
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
            # Register with the MQTT broker and link the method mqtt_callback() as the callback
            # when messages are recieved
            self.register_to_mqtt(server=self.MQTT_ADDR, port=self.MQTT_PORT,
                                  sub_callback=self.mqtt_callback)
            # Subscribe to topic "uos/cet235-00/temperature/value"
            self.mqtt_client.subscribe(self.MQTT_TOPIC_1)

            # Subscribe to topic "uos/cet235-00/time/value"
            self.mqtt_client.subscribe(self.MQTT_TOPIC_2)

            self.oled_clear()
            self.oled_display()
        else:
            self.wifi_msg = "No WIFI"
            self.oled_clear()
            self.oled_display()

        # These will hold the most recently received temperatures and times from the relevant MQTT
        # subscriptions, initially a "--------" string until a value for each is received
        self.temperature_str = "--------"
        self.time_str = "--------"

    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        self.oled_clear()
        self.oled_text(self.wifi_msg, 0, 0)
        self.oled_text("Time: {0}".format(self.time_str), 0, 10)
        self.oled_text("Temp: {0}".format(self.temperature_str), 0, 20)
        self.oled_display()

        if self.is_wifi_connected():
            # Check for any messages received from the MQTT broker, note this is a non-blocking
            # operation so if no messages are currently present the loop() method continues
            self.mqtt_client.check_msg()
        
        sleep(0.1)
        
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

    def mqtt_callback(self, topic, msg):
        """
        MQTT callback method, note how the topic is checked to determine how the received
        message from the MQTT broker should be handled, you could also base the operation
        of this callback method on the value of the received message, either way is
        acceptable
        """
        # Note: msg is a list of bytes so you need to convert these into a proper string
        # using the .decode("utf-8") method
        if topic == self.MQTT_TOPIC_1:
            self.temperature_str = "{0}c".format(str(msg.decode("utf-8")))

        if topic == self.MQTT_TOPIC_2:
            self.time_str = str(msg.decode('utf-8'))

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
    #   name: "MQTT Sub Sim", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="MQTT Sub Sim", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
