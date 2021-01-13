#!/usr/bin/python3
import json
import os
this_file_path = os.path.abspath(os.path.dirname(__file__))


def read_state(filename):
    with open(filename,"r") as file_handler:
        arg_handler = json.load(file_handler)
    return arg_handler

def save_state(arg_handler,filename):
    with open(filename,'w') as f:
        json.dump(arg_handler,f, indent=2)
    

if __name__=="__main__":
    arg_handler = read_state(os.path.join(this_file_path,"args.json"))
    print(arg_handler)
    arg_handler["states"]["motor_1"] = True
    save_state(arg_handler,os.path.join(this_file_path,"args.json"))
    
    