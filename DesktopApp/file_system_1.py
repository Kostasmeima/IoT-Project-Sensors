# File: file_system_1.py
# Description: Sample code for Week 5 Task 1
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
        self.file_name = "image.pbm"
        
        # If the file "image.pbm" does not exist on the root of the Huzzah32's file system then
        # no need to continue use the file_exists() method to check this
        if not self.file_exists(self.file_name):
            self.file = None
            self.finish()
            print("File [{0}] not found, aborting!".format(self.file_name))
            return
        
        # Open file for reading using the "r" flag
        self.file = open(self.file_name, "r") 

        # Read each line from the "image.pbm" file (there are 32, with each line having 128
        # "bits" (i.e. 0 or 1), the 0 is a black pixel the 1 is a white pixel, read each
        # line and set pixels on the OLED screen buffer if the "bit" is value 1, once all
        # lines form the file have been read and the OLED screen buffer updated accordingly
        # display the OLED screen buffer, note: by initially clearing the OLED screen buffer
        # to all pixels black only white pixels read from the file need to be updated
        self.oled_clear()

        for y in range(32):
            line = self.file.readline().replace("\r\n", "")
            x = 0
            for bit in line:
                if bit == "1":
                    self.oled_pixel(x, y, 1)
                x += 1
                
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
        # Make sure the image.pbm file is closed, if it exists
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
    #   name: "File Sys 1", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="File Sys 1", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
