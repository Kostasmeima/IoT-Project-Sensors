# File: ntp_simulated.py
# Description: Example code for updating a simulated RTC in simulated ESP32 MicroPython application code
# Author: Chris Knowles, University of Sunderland
# Date: Apr 2020

# Imports
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
    AP_SSID = "DCETLocalVOIP"
    AP_PSWD = ""
    AP_TOUT = 5000
    NTP_ADDR = "13.86.101.172"  # IP address of time.windows.com, NTP server at Microsoft
    NTP_PORT = 123  # NTP server port number (by default this is port 123)
        
    def init(self):
        """
        The init() method is designed to contain the part of the program that initialises
        app specific properties (such as sensor devices, instance variables etc.)
        """
        self.ntp_msg = "No NTP - RTC bad"
        connect_count = 0
        # Try to connect to WiFi 5 times
        while connect_count < 5 and not self.is_wifi_connected():
            self.oled_clear()
            self.oled_text("Connect WIFI:{0}".format(connect_count + 1), 0, 0)
            self.oled_display()
            self.connect_to_wifi(wifi_settings=(self.AP_SSID, self.AP_PSWD, True, self.AP_TOUT))
            connect_count += 1
            
        if self.is_wifi_connected():
            self.ntp_msg = "NTP - RTC good"
            # Contact the NTP server and update the RTC with the correct date and time as
            # provided by this server, the method set_rtc_by_ntp() is a convenience method
            # that is implemented in the IoTApp class and therefore inherited by your own
            # application class
            self.set_rtc_by_ntp(ntp_ip=self.NTP_ADDR, ntp_port=self.NTP_PORT)
            
        else:
            # In this case the NTP server was not able to be contacted so the RTC is not
            # correct
            self.oled_clear()
            self.oled_text("No WIFI", 0, 0)
            self.oled_display()
            sleep(4)
        
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        self.oled_clear()

        # Get currently accurate date and time and display it
        yr, mn, dy, dn, hr, mi, se, ms = self.rtc.datetime()
        self.oled_text(self.ntp_msg, 0, 2)
        output = "{0} {1:02d}-{2:02d}-{3}".format(self._DAY_NAMES[dn][0:3], dy, mn, yr)
        self.oled_text(output, 0, 12)
        output = "{0:02d}:{1:02d}:{2:02d}".format(hr, mi, se)
        self.oled_text(output, 0, 22)

        self.oled_display()

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
    #   name: "NTP Sim'ed", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="NTP Sim'ed", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
