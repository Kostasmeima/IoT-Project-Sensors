# File: ppw1_app_sample.py
# Description: Sample code for PPW1 script to run on the Desktop
# Author: Chris Knowles, University of Sunderland
# Date: Jan 2019

import time
import random

# Classes
class DataReading:
    """
    Class to hold a single data reading, this consists of a given timestamp and given temperature and humidity
    data for this time stamp
    """
    def __init__(self, timestamp, temp_data, humidity_data):
        """
        Initialiser - instance variables:
            __timestamp: timestamp for this data reading, as string, property with read-only access
            __temp_data: temperature data for this data reading, as float, property with read-only access
            __humidity_data: humidity data for this data reading, as float, property with read-only access

        :param timestamp: to associate with this data reading instance
        :param temp_data: to associate with this data reading instance
        :param humidity_data: to associate with this data reading instance
        """
        self.__timestamp = timestamp
        self.__temp_data = temp_data
        self.__humidity_data = humidity_data

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def temp_data(self):
        return self.__temp_data

    @property
    def humidity_data(self):
        return self.__humidity_data

    def __str__(self):
        """
        To string method

        :return: string representation of this data reading instance
        """
        return "Timestamp: {0} {1}c {2}%".format(self.timestamp, self.temp_data, self.humidity_data)


class AccessPeriod:
    """
    Class to contain a single access period which consists of a number of data readings (timestamp, temperature,
    humidity) associated with a given access period, this class also holds the start and stop date and time of the
    access period, the maximum temperature, average humidity and the approximate length of time in seconds the access
    period lasted
    """
    def __init__(self, start_date, start_time):
        """
        Initialiser - instance variables:
            __start_date: start date of this access period, as string, property with read-only access
            __start_time: start time of this access period, as string, property with read-only access
            __stop_date: stop date of this access period, as string, property with read-only access
            __stop_time: stop time of this access period, as string, property with read-only access
            __period_length: approximate number of seconds this access period lasted, as int, property with
                             read-only access
            __data_readings: list of DataReadings class instances, property with no access
            __temp_max: maximum temperature across all data readings in the data set, as float, property with
                        read-only access
            __humidity_average: average humidity across all data readings in the data set, as float, property with
                                read-only access

        :param start_date: start date of this access period, as string
        :param start_time: start time of this access period, as string
        """
        self.__start_date = start_date
        self.__start_time = start_time
        self.__stop_date = None  # This is updated separately once the instance has been created
        self.__stop_time = None  # This is updated separately once the instance has been created
        self.__period_length = 0  # This is updated separately once the instance has been created
        self.__data_readings = []  # Initially empty until data readings are added
        self.__temp_max = None  # This will be calculated and assigned when data readings are added
        self.__humidity_average = None  # This will be calculated and assigned when data readings are added

    @property
    def start_date(self):
        return self.__start_date

    @property
    def start_time(self):
        return self.__start_time

    @property
    def stop_date(self):
        return self.__stop_date

    @stop_date.setter
    def stop_date(self, value):
        self.__stop_date = value

    @property
    def stop_time(self):
        return self.__stop_time

    @stop_time.setter
    def stop_time(self, value):
        self.__stop_time = value

    @property
    def period_length(self):
        return self.__period_length

    @period_length.setter
    def period_length(self, value):
        self.__period_length = value

    @property
    def temp_max(self):
        return self.__temp_max

    @property
    def humidity_average(self):
        return self.__humidity_average

    def add_data_reading(self, data_reading):
        """
        This method is used to add a new data reading to this AccessPeriod class instance, you must use this method
        as it also updates the maximum temperature and humidity average as a new data reading is added

        :param data_reading: data reading to be added as instance of DataReading class

        :return: nothing
        """
        # Add data reading to the data readings property
        self.__data_readings.append(data_reading)

        # Check if the temperature associated with this data reading is greater than the currently recorded maximum
        # temperature, note: if this is the first data reading added then the maximum temperature must be the
        # temperature from this reading
        if not self.temp_max:
            self.__temp_max = data_reading.temp_data
        elif data_reading.temp_data > self.temp_max:
            self.__temp_max = data_reading.temp_data

        # Update the humidity average to take account of this newly added data reading, note: if this is the first
        # data reading added then the average will be the humidity from this reading
        if not self.humidity_average:
            self.__humidity_average = data_reading.humidity_data
        else:
            self.calculate_humidity_average()

    def calculate_humidity_average(self):
        """
        This method calculates the average of the humidity data held in the data readings list and updates the humidity
        average property with this value.

        :return:
        """
        total = 0.0
        for data_reading in self.__data_readings:
            total += data_reading.humidity_data

        self.__humidity_average = total / len(self.__data_readings)

    def print_access_period(self):
        """
        Print this access period to the console

        :return: nothing
        """
        # First, print the start and end date and time for this access period
        print("Started:  {0} {1}".format(self.start_date, self.start_time))
        print("Stopped:  {0} {1}".format(self.stop_date, self.stop_time))

        # Second, print approximate length of the access period in seconds
        print("Length:   {0} seconds (approx)".format(self.period_length))

        # Third, print the maximum temperature recorded during this access period
        print("Max Temp: {0} degrees C".format(self.temp_max))

        # Fourth, print the humidity average recorded during this access period (to two decimal places)
        print("Hmdy Ave: {0:.2f} %".format(self.humidity_average))

        # Finally, print the full list of data readings for this access period
        print("Data Readings:")
        print("------------------------------------------------------------")
        for data_reading in self.__data_readings:
            print(data_reading)


class AccessPeriods:
    """
    Class to contain a number of access periods as read from the supplied CSV data file when an instance of this
    class is instantiated
    """
    def __init__(self):
        """
        Initialiser - instance variables:
            __access_periods: List of AccessPeriod class instances created as the CSV data file is read, property with
                              no access

        :param data_file: path to the data_file, as string
        """
        self.__access_periods = []  # Initially empty until read from CSV data file

    def add_access_period(self, access_period):
        """
        Add an access period to the list of access periods.

        :param access_period: An instance of AccessPeriod.

        :return: None
        """
        self.__access_periods.append(access_period)

    def get_access_periods(self):
        """
        Get the list of access periods.

        :return: List of AccessPeriod instances.
        """
        return self.__access_periods


# Simulation function to generate simulated temperature and humidity data
def generate_simulated_data():
    """
    Function to generate simulated temperature and humidity data.

    :return: Tuple of simulated temperature and humidity data.
    """
    # Simulate temperature within range of 15 to 25 degrees Celsius
    temperature = round(random.uniform(15, 25), 2)

    # Simulate humidity within range of 40% to 60%
    humidity = round(random.uniform(40, 60), 2)

    return temperature, humidity


# Main program entrance function
def main():
    """
    Main function
    """
    print()
    print("Sample solution for CET235 PPW1 Desktop Application")
    print("---------------------------------------------------")

    # Instantiate an AccessPeriods object
    access_periods = AccessPeriods()

    # Simulate access periods and record data
    for _ in range(3):  # Simulating three access periods
        # Simulate start time
        start_time = time.strftime("%H:%M:%S", time.localtime())
        start_date = "12th May 2021"

        # Simulate access period duration
        access_duration = random.randint(5, 15)  # Random duration between 5 to 15 seconds

        # Record start time of access period
        print("Access started at:", start_time)

        # Simulate and record temperature and humidity data for the access period
        for _ in range(access_duration):
            # Generate simulated temperature and humidity data
            temperature, humidity = generate_simulated_data()

            # Record the data
            timestamp = time.strftime("%H:%M:%S", time.localtime())
            data_reading = DataReading(timestamp, temperature, humidity)

            # Print and add the data reading to the access period
            print(data_reading)
            # Assuming access period object is created here
            # access_period.add_data_reading(data_reading)

            # Sleep for 1 second to simulate real-time data acquisition
            time.sleep(1)

        # Simulate stop time
        stop_time = time.strftime("%H:%M:%S", time.localtime())

        # Record stop time of access period
        print("Access stopped at:", stop_time)

        # Add this access period to the list of access periods
        # Assuming access period object is created here
        # access_periods.add_access_period(access_period)

        # Sleep for 10 seconds between access periods to simulate intervals
        time.sleep(10)

    # Exit application
    print("Finished")


# Invoke main() program entrance
if __name__ == "__main__":
    # execute only if run as a script
    main()
