# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 20:29:42 2023

@author: vgvac
"""


import datetime
from time import sleep

print('Welcome')
sleep(3)

passbook = ['BB235AA' , 'CK523BB' ,'FE344GK', 'RE456ZZ']

exitt= ['Exit']

password = ''

entrantdic={"Personnel ID":[] , "Entry" :[] , "Exit" : []}
log =[]

while password not in exitt :
    
    
    ct = datetime.datetime.now()
    print("current time:-", ct)
   
    password = input("Please type in your personalised key or Exit :")
    log.append((str(ct),password))

    print('Validating...')
    sleep(3)
    
    if password in passbook :
        print("Access Allowed")
        ct = datetime.datetime.now()
        entrantdic["Personnel ID"].append(password)
        entrantdic["Entry"].append(str(ct))
        entrant = [password]
        light_colour = 1
        i=0
        while i<1 :
            #Here we make all the calculations and take enviromental data
            ct = datetime.datetime.now()
            print("current time:-", ct)
            pass1 = input("If you want to exit press exit:")
            if pass1 in ['exit'] :
                confirmation = input("Please type in your personalised key :")
                if confirmation in entrant :
                    i=2
                    light_colour=0
                    ct = datetime.datetime.now()
                    print("current time:-", ct)
                    entrantdic["Exit"].append(str(ct))
                    print("Exiting...")
                    sleep(2)
                else : 
                    print("Entrance not allowed while room is occupied!") 
            else: 
                    print('Room is occupied')
                    sleep(2)
    else :
        if password not in exitt :
            ct = datetime.datetime.now()
            print("current time:-", ct)
            print("Access Denied")
        else : 
            ct = datetime.datetime.now()
            print("current time:-", ct)
            sleep(3)
            print("People entered the room:")
            print( entrantdic)
            sleep(2)
            print("Key Log")
            print(log)
            
 