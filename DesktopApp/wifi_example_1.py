# File: wifi_example_1.py
# Description: Example code to connect the Huzzah32 to the WLAN using Wi-Fi
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import network
from iot_app import IoTApp

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
        # Create the Wi-Fi instance as a WLAN station interface (i.e. will be connecting to
        # the Wi-Fi router, which is acting as a WLAN access point)
        wifi = network.WLAN(network.STA_IF)
        
        # Activate the Wi-Fi interface
        wifi.active(True)
        
        # If already connected then disconnect first
        if wifi.isconnected():
            wifi.disconnect()
        
        # Attempt to connect to the open Wi-Fi router with SSID = "DCETLocalVOIP", this is 
        # an open router so no need for a passkey, it can be left blank (the second
        # parameter), note this will loop forever until a connection is established, you will
        # have to abort the run of this script (by disconnecting the Huzzah32 from USB power)
        # if it fails to complete in a reasonable time
        wifi.connect("DCETLocalVOIP", "")

        # Display an OLED message to state that connection is being attempted
        self.oled_clear()
        self.oled_text("Attempt connect", 0, 10)
        self.oled_display()
        
        while not wifi.isconnected():  # Busy waiting for a connection
            pass
            
        # Make note of the IP address allocated by the Wi-Fi router, this is achieved by use
        # of the ifconfig() method of the WLAN object which returns a 4-tuple with details of
        # IP address, subnet mask, gateway and DNS server from the Wi-Fi router so to get at
        # the IP address use the first entry in this tuple
        ip_address = wifi.ifconfig()[0]  # First tuple entry is IP address

        # Display message to state that WLAN has connected and also show the IP address
        # allocated by the Wi-Fi router
        self.oled_clear()
        self.oled_text("Connected", 0, 10)
        self.oled_text("{0}".format(ip_address), 0, 20)
        self.oled_display()
        
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        pass
    
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
    #   name: "WiFi Example 1", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="WiFi Example 1", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
