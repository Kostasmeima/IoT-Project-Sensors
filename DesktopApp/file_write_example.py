# File: file_write_example.py
# Description: Example to show how to write text data to a file on the Huzzah32's
#              root file system
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import os
from time import sleep
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
        # Name of the file to write to the Huzzah32's root file system
        self.file_name = "data.csv"
        
        # If the file data.csv already exists on the root of the Huzzah32's file system then
        # first remove it (otherwise it will be appended to since the file is openned using
        # the "w+" flag, use the file_exists() method to check this and then remove if
        # necessary
        if self.file_exists(self.file_name):
            os.remove(self.file_name)
        
        # Open file for appending, note you could open the file simply for writing using the
        # flag "w" but then if a file of the same name is already on the file system it will
        # always be overwritten (so be careful)
        self.file = open(self.file_name, "w+") 

        # Counter used to provide data to write to the file
        self.count = 0
    
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        # Clear OLED screen buffer
        self.oled_clear()
        
        # Write current value of count property to file as a new text line, note the
        # use of the \n character to ensure a new line is written
        data_str = "{0}\n".format(self.count)
        self.file.write(data_str)

        # Draw current count property on OLED screen buffer
        self.oled_text("Count: {0}".format(self.count), 20, 10)
        
        # Update OLED screen
        self.oled_display()

        # Increment the counter
        self.count += 1
        
        # Delay for a second
        sleep(1)
    
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # Make sure the data.csv file is closed, if it exists
        if self.file:
            self.file.close()
        
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
    #   name: "File Write Exp", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="File Write Exp", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
