# File: rtc_example.py
# Description: Example to use the Huzzah32's real-time clock (RTC)
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

# Imports
from iot_app import IoTApp
from machine import RTC  # Real-time clock class is in the machine module

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
        # Instantiate a real-time clock object instance using the date and time:-
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
        self.real_time_clock = RTC()
        self.real_time_clock.datetime((2018, 12, 31, 0, 23, 59, 55, 0))
        #self.rtc.datetime((2018, 12, 31, 0, 23, 59, 55, 0))  # Alternative approach
        
        # The IoTApp class does already have an instance of the RTC class assigned to the
        # property self.rtc and that can be used in place of an RTC instance you instantiated
        # yourself, the above line then becomes:-
        #
        #    self.rtc.datetime((2018, 12, 31, 0, 23, 59, 55, 0))
        #
        # and then use this property whenever you need access to the real-time clock
        
        # Provide a list of day names to use in place of the day number
        self.day_names = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        
        # The IoTApp class also provides a static property that contains the full names of 
        # each day, to access this use:-
        #
        #   IoTApp._DAY_NAMES
        #
        # index this with the current day number to get the actual day name, so to get the
        # name of day number 4 (Friday) use:-
        #
        #   IoTApp._DAY_NAMES[4]
        #
        # and to get the day name as only the first 3 characters (i.e. Fri in this example)
        # use the following:
        #
        #   IoTApp._DAY_NAMES[4][:3]
        #
        # try this and the use of the self.rtc property in this example code

    
    def loop(self):
        """
        The loop() method is called after the init() method and is designed to contain
        the part of the program which continues to execute until the finished property
        is set to True
        """
        # Display the current date and time taken from the RTC instance, the datetime()
        # method of the RTC class returns the current date and time as a tuple
        now = self.real_time_clock.datetime()
        #now = self.rtc.datetime()  # Alternative approach
        
        year = now[0]
        month = now[1]
        day = now[2]
        day_number = now[3]
        day_name = self.day_names[day_number]
        #day_name = IoTApp._DAY_NAMES[day_number][:3]  # Alternative approach
        hour = now[4]
        minute = now[5]
        second = now[6]
        microsecond = now[7]
        
        # Format strings to hold the current date and the current time
        date_str = "{0}/{1}/{2} - {3}".format(day, month, year, day_name)
        time_str = "{0}:{1}:{2}:{3}".format(hour, minute, second, microsecond)
        
        # Display the current date and time on the OLED screen, with the preselected
        # date and time the clock will tick over to a new year, month, day, hour and
        # minute after 5 seconds (so watch carefully!)
        self.oled_clear()
        self.oled_text(date_str, 0, 4)
        self.oled_text(time_str, 0, 14)
        self.oled_display()
    
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
    #   name: "RTC Example", this should be a maximum of 14 characters else it is truncated
    #   has_oled_board: set to True as you are using the OLED FeatherWing
    #   finish_button: set to "C" which designates Button C on the OLED FeatherWing as the
    #                  button that sets finished property to True
    #   start_verbose: set to True and the OLED FeatherWing will display a message as it
    #                  starts up the program
    #
    app = MainApp(name="RTC Example", has_oled_board=True, finish_button="C", start_verbose=True)
    
    # Run the app
    app.run()

# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
