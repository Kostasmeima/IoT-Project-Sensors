# File: file_read_example.py
# Description: Example to show how to read text data from a file on the Huzzah32's
#              root file system
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
import os
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
        # Name of the file to read from on the Huzzah32's root file system
        self.file_name = "words.txt"
        
        # If the file word.txt does not exist on the root of the Huzzah32's file system then
        # no need to continue use the file_exists() method to check this
        if not self.file_exists(self.file_name):
            self.file = None
            self.finish()
            print("File [{0}] not found, aborting!".format(self.file_name))
            return
        
        # Open file for reading using the "r" flag
        self.file = open(self.file_name, "r") 

        # Read each line from the words.txt file (there are three, one on each line in the
        # text file, position each line in the centre of the OLED screen
        line1 = self.file.readline().replace("\r\n", "")
        line1_x = int((128 - (len(line1) * 8)) / 2)
        line2 = self.file.readline().replace("\r\n", "")
        line2_x = int((128 - (len(line2) * 8)) / 2)
        line3 = self.file.readline().replace("\r\n", "")
        line3_x = int((128 - (len(line3) * 8)) / 2)
        
        # Display these text lines on the OLED screen
        self.oled_clear()
        self.oled_text(line1, line1_x, 0)
        self.oled_text(line2, line2_x, 10)
        self.oled_text(line3, line3_x, 20)
        self.oled_display()
    
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        # Do not need to do anything during the loop() method, simply display on OLED
        # screen until button C is pressed
        pass
    
    def deinit(self):
        """
        The deinit() method is called after the loop() method has finished, is designed
        to contain the part of the program that closes down and cleans up app specific
        properties, for instance shutting down sensor devices. It can also be used to
        display final information on output devices (such as the OLED FeatherWing)
        """
        # Make sure the words.txt file is closed, if it exists
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
    #   name: "File Read Exmp", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="File Read Exmp", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
