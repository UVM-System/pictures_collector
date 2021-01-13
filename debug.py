#!/usr/bin/python3
import time
import serial
import json
import os
this_file_path = os.path.abspath(os.path.dirname(__file__))
def read_json(filename):
    with open(filename,"r") as file_handler:
        arg_handler = json.load(file_handler)
    return arg_handler

def save_json(arg_handler,filename):
    with open(filename,'w') as f:
        json.dump(arg_handler,f, indent=2)

def init_serials(arg_handler):
    serial_ports = arg_handler["serialPorts"]
    serial_handlers = []
    for port_str in serial_ports:
        serial_handler = serial.Serial(port_str,9600,timeout=0.5)
        serial_handlers.append(serial_handler)
    return serial_handlers

def init():
    state_handler = read_json(os.path.join(this_file_path,"states.json"))
    arg_handler = read_json(os.path.join(this_file_path,"args.json"))
    serial_handlers = init_serials(arg_handler)
    return serial_handlers

def main():
    serial_handlers = init()
    while True:
        input_str = input("input the char:\n")
        if len(input_str)==1:
            for serial_handler in serial_handlers:
                serial_handler.write(bytes(input_str, encoding = "utf8"))
        if input_str=="exit":
           return
if __name__=="__main__":
    main()
        
    
