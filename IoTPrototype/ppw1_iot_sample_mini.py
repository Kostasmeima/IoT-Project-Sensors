import os
from time import sleep
from libs.iot_app import IoTApp
from libs.bme680 import BME680,OS_2X,OS_4X,OS_8X,FILTER_SIZE_3,ENABLE_GAS_MEAS
from neopixel import NeoPixel
from machine import Pin
class MainApp(IoTApp):
 def init(self):
  self.neopixel_pin=self.rig.PIN_21
  self.neopixel_pin.init(mode=Pin.OUT,pull=Pin.PULL_DOWN)
  self.npm=NeoPixel(self.neopixel_pin,32,bpp=3,timing=1)
  self.rtc.datetime((2019,3,5,1,9,0,0,0))
  self.obtain_sensor_bme680()
  self.file_name="access_data.csv"
  if self.file_exists(self.file_name):
   os.remove(self.file_name)
  self.file=open(self.file_name,"w+")
  self.access=False
  self.access_str=""
  self.warning_str=""
  self.count=0
  self.npm.fill((0,0,0))
  self.npm.write()
 def loop(self):
  self.oled_clear()
  if self.sensor_bme680.get_sensor_data():
   tm_reading=self.sensor_bme680.data.temperature 
   rh_reading=self.sensor_bme680.data.humidity 
   now=self.rtc.datetime()
   year=now[0]
   month=now[1]
   day=now[2]
   hour=now[4]
   minute=now[5]
   second=now[6]
   if self.access:
    timestamp="{0}-{1}-{2}|{3}:{4}:{5}".format(year,month,day,hour,minute,second)
    data_line="{0},{1:.2f},{2:.2f}\n".format(timestamp,tm_reading,rh_reading)
    self.file.write(data_line)
    led_colour=(0,10,0) 
    if self.count>4 and self.count<10:
     led_colour=(10,7,0) 
     self.warning_str="AMBER" 
    elif self.count>9:
     led_colour=(10,0,0) 
     self.warning_str="RED" 
    self.npm.fill(led_colour)
    self.npm.write()
    self.count+=1
   output="{0}/{1}/{2}".format(day,month,year)
   self.oled_text(output,0,0)
   output="{0}:{1}:{2}".format(hour,minute,second)
   self.oled_text(output,0,8)
   output="T:{0:.2f}c H:{1:.2f}%".format(tm_reading,rh_reading)
   self.oled_text(output,0,16)
   if self.access:
    output="{0}:{1} {2}".format(self.access_str,self.count,self.warning_str)
    self.oled_text(output,0,24)
  self.oled_display()
  sleep(1)
  import micropython
  print(micropython.mem_info())
 def deinit(self):
  self.npm.fill((0,0,0))
  self.npm.write()
  if self.access:
   self.file.write("{0},{1}".format("ACCESS-STOPPED",self.count))
  self.file.close()
 def obtain_sensor_bme680(self):
  self.sensor_bme680=BME680(i2c=self.rig.i2c_adapter,i2c_addr=0x76)
  self.sensor_bme680.set_temperature_oversample(OS_8X)
  self.sensor_bme680.set_humidity_oversample(OS_2X)
  self.sensor_bme680.set_filter(FILTER_SIZE_3)
 def file_exists(self,file_name):
  file_names=os.listdir()
  return file_name in file_names
 def btnA_handler(self,pin):
  if not self.access:
   self.file.write("{0}\n".format("ACCESS-STARTED"))
   self.access=True
   self.access_str="ACCESS"
   self.warning_str="GREEN"
   self.count=0
 def btnB_handler(self,pin):
  if self.access:
   self.file.write("{0},{1}\n".format("ACCESS-STOPPED",self.count))
   self.access=False
   self.access_str=""
   self.warning_str=""
   self.npm.fill((0,0,0))
   self.npm.write()
def main():
 app=MainApp(name="PPW1 Sample",has_oled_board=True,finish_button="C",start_verbose=True)
 app.run()
if __name__=="__main__":
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
