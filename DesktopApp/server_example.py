# File: server_example.py
# Description: Example code to show a Huzzah32 connected using Wi-Fi as a server
#              when communicating over a network socket
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import network
import socket
from libs.iot_app import IoTApp

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
        # The convenience method connect_to_wifi() is available in the IoTApp class, it
        # requires that you pass a 4-tuple with the SSID of Wi-Fi router, the passkey
        # associated with this SSID (or "" if this is an open router), a boolean flag
        # that controls if the connection should be made immediately and finally a time
        # in milliseconds within which the connection must be made or it will time out,
        # this wait time can be 0 or less in which case there is an indefinite wait, i.e.
        # the connection is attempt forever until either it connects or you abort the run
        # of the script, this 4-tuple is passed to the connect_to_wifi() methid through
        # the parameter named wifi_settings
        wifi_config = ("DCETLocalVOIP", "", True, 0)  # Wait time of 0 means keep attempting
                                                      # to connect
        
        # Display an OLED message to state that connection is being attempted
        self.oled_clear()
        self.oled_text("Attempt connect", 0, 10)
        self.oled_display()

        # Once a connection has been made then the detials of how the connection was set up
        # and the resulting WLAN object instance are available in the properties:-
        #
        #       self.wifi
        #       self.ssid
        #       self.passkey
        #       self.auto_connect
        #       self.wait_time
        # 
        # These are all set within the connect_to_wifi() method (or left to their current
        # settings if no wifi_setting parameter is used
        self.connect_to_wifi(wifi_settings=wifi_config)

        # Make note of the IP address allocated by the Wi-Fi router, this is achieved by use
        # of the ifconfig() method of the WLAN object which returns a 4-tuple with details of
        # IP address, subnet mask, gateway and DNS server from the Wi-Fi router so to get at
        # the IP address use the first entry in this tuple
        ip_address = self.wifi.ifconfig()[0]  # First tuple entry is IP address

        # Display message to state that WLAN has connected and also show the IP address
        # allocated by the Wi-Fi router
        self.oled_clear()
        self.oled_text("IP Address:", 0, 10)
        self.oled_text("{0}".format(ip_address), 0, 20)
        self.oled_display()

        # Create a server socket using the current IP address of the connection and on port
        # number 2350, this is done by the socket's bind() method
        sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sckt.bind((ip_address, 2350))  # Note: passed in as 2-tuple here
        sckt.listen(5)  # Listen for clients to connect to this server (upto 5 at a time)
        
        # Wait until a client tries to connect, accept this connection and then send a message
        # to that client, repeat this forever, to abort the server you will have to remove the
        # USB power to the Huzzah32
        while True:
            client_sckt, client_ip_address = sckt.accept()  # When a client tries to connect
                                                            # then accept it, recording the
                                                            # socket created for this client
                                                            # and the client IP address
                                                            
            # Can only send byte stream on the socket so convert (encode) the message as string
            # into a stream of bytes and send that
            msg_as_string = "I'm connected!!!"
            msg_as_bytes = bytes(msg_as_string, "utf-8")
            client_sckt.send(msg_as_bytes)
        
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
    #   name: "Server Example", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="Server Example", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
