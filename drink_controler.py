#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
import serial
import json
import os
import cv2
import threading
import shutil
this_file_path = os.path.abspath(os.path.dirname(__file__))

DELAY_TIME = 7


def read_json(filename):
    with open(filename,"r") as file_handler:
        arg_handler = json.load(file_handler)
    return arg_handler

def save_json(arg_handler,filename):
    with open(filename,'w') as f:
        json.dump(arg_handler,f, indent=2)
    

class CapHandler(object):
    """摄像头管理者，用于打开摄像头，获取视频流"""
    def __init__(self,video_order):
        self.frame = None
        self.start = False
        self.stop = False
        self.cap_handler = cv2.VideoCapture(video_order)
        self.cap_handler.set(3,1920)
        self.cap_handler.set(4,1080)
    
    def run(self):
        while not self.stop:
            ret,frame = self.cap_handler.read()
            if ret:
               self.frame = frame 

    def startCap(self):
        self.start = True
        self.stop = False
        threadHandler = threading.Thread(target=self.run)
        threadHandler.start()
    def stop(self):
        self.stop = True
        self.start = False
    def getFrame(self):
        return self.frame


class Motor_Controler(object):
    """马达控制器，用于控制马达"""
    def __init__(self,serial_handers,instruction):        
        self.serial_handers = serial_handers
        self.instruction = instruction
        self.state = False

    def set_state(self,state):
        ''' True 是升到顶部的状态; False 是降到底部的状态'''
        assert type(state) == bool
        self.state = state
    
    def rise(self):
        if self.state==False:
            self.change_order()
            self.run_motor()
            self.state = True
            time.sleep(DELAY_TIME)
        return
    def drop(self):
        if self.state==True:
            self.change_order()
            self.run_motor()
            self.state = False
            time.sleep(DELAY_TIME)
        return
    
    def init_state(self):
        ''' 开始时，将光标移动到控制升降的位置 '''
        self.send_char(self.instruction.set,9)

    def change_order(self):
        ''' 改变升降机升降方向 '''
        self.send_char(self.instruction.add,1)

    def run_motor(self):
        ''' 启动升降机 '''
        self.send_char(self.instruction.run,1)

    def send_char(self,char,count):
        for i in range(count):
            for serial_hander in self.serial_handers:
                serial_hander.write(char)
            time.sleep(0.08)
        
        

class Instruction(object):
    '''
    控制指令，相当于四个按钮
    set_char: 右移一位
    add_char: 数字加
    sub_char: 数字减
    run_char: 启动
    '''
    def __init__(self,set_char,add_char,sub_char,run_char):
        self.set = bytes(set_char, encoding = "utf8")
        self.add = bytes(add_char, encoding = "utf8")
        self.sub = bytes(sub_char, encoding = "utf8")
        self.run = bytes(run_char, encoding = "utf8")


def init_serials(arg_handler):
    '''根据 json 文件的 'serialPorts' 属性，打开串口'''
    serial_ports = arg_handler["serialPorts"]
    serial_handlers = []
    for port_str in serial_ports:
        serial_handler = serial.Serial(port_str, 9600, timeout=0.5)
        serial_handlers.append(serial_handler)
    return serial_handlers


def init_motor_controler(arg_handler,serial_handers):
    '''初始化马达控制器， 根据 json 文件的 'instructions' 属性，初始化每个马达的指令信息（四个按钮）'''
    instruction_dict = arg_handler.get("instructions")
    motor_controler_dict ={}
    for name,instruction_list in instruction_dict.items():
        instruction_temp = Instruction(instruction_list[0],instruction_list[1],instruction_list[2],instruction_list[3])
        motor_controler = Motor_Controler(serial_handers,instruction_temp)
        motor_controler_dict.setdefault(name,motor_controler)
    return motor_controler_dict


def init():
    '''读取 json 文件，初始化所有的马达控制器，并设置其状态'''
    state_handler = read_json(os.path.join(this_file_path,"states.json"))
    arg_handler = read_json(os.path.join(this_file_path,"args.json"))
    serial_handlers = init_serials(arg_handler)
    motor_dict = init_motor_controler(arg_handler,serial_handlers)
    time.sleep(2)
    for motor_name,controler in motor_dict.items():
        controler.init_state()    # 将按钮移动到控制升降状态位
        controler.set_state(state_handler[motor_name])    # 设置升降机初始升降状态
    return motor_dict,state_handler


def save_state(motor_dict,state_handler):
    '''保存当前所有马达的升降状态'''
    for name,controler in motor_dict.items():
        state_handler[name] = controler.state
    save_json(state_handler,os.path.join(this_file_path,"states.json"))
    

def testOrder():
    '''测试'''
    motor_dict,state_handler = init()
    print("初始化成功！")
    cap = CapHandler(0)
    cap.startCap()
    img_path = os.path.join(this_file_path,"imgs/")
    format_str = "%Y-%m-%d,%H_%M_%S"
    state_order_list = read_json(os.path.join(this_file_path,'showOrder.json'))
    
    for state in state_order_list:
        for name,value in state.items():
            if motor_dict[name].state != value:
                change_state(motor_dict[name],value)
        frame = cap.getFrame()
        imagename = time.strftime(format_str,time.localtime())
        imagefilename = os.path.join(img_path,imagename+".jpg")
        cv2.imwrite(frame,imagefilename)
        save_state(motor_dict,state_handler)

def OrderWhile():
    dataPath = '/home/pi/up_and_down/data/'
    motor_dict,state_handler = init()
    productJsonPath = os.path.join(dataPath,'order/')
    if not os.path.exists(productJsonPath):
        os.mkdir(productJsonPath) 
    cap = CapHandler(0)
    cap.startCap()
    print("初始化成功！")
    img_path = os.path.join(dataPath,"imgs/")
    if not os.path.exists(img_path):
        os.mkdir(img_path)
    format_str = "%Y-%m-%d,%H_%M_%S"
    state_order_list = read_json(os.path.join(this_file_path,'showOrder.json'))
    while True:
        input_str = input("请输入指令:\ns启动\nq退出\n")
        if input_str=="s":
            for state in state_order_list:
                for name,value in state.items():
                    if motor_dict[name].state != value:
                        change_state(motor_dict[name],value)
                frame = cap.getFrame()
                time_str = time.strftime(format_str,time.localtime())
                image_file_name = os.path.join(img_path,time_str+".jpg")
                json_file_name = os.path.join(productJsonPath,time_str+".json")
                cv2.imwrite(image_file_name,frame)
                copyOrder(json_file_name)
                save_state(motor_dict,state_handler)
        if input_str=="q":
            return


def copyOrder(savefile):
    product_order_file = os.path.join(this_file_path,'product.json')
    shutil.copy(product_order_file,savefile) 
    

def change_state(controler,state):
    if state==True:
        controler.rise()
    else:
        controler.drop()
        

def main():
    motor_dict,state_handler = init()
    while True:
        input_str = input("input the char:\n")
        if input_str=="r1":
            motor_dict["motor_1"].rise()
        if input_str=="d1":
            motor_dict["motor_1"].drop()
        if input_str=="r2":
            motor_dict["motor_2"].rise()
        if input_str=="d2":
            motor_dict["motor_2"].drop()
        if input_str=="r3":
            motor_dict["motor_3"].rise()
        if input_str=="d3":
            motor_dict["motor_3"].drop()
        if input_str=="r4":
            motor_dict["motor_4"].rise()
        if input_str=="d4":
            motor_dict["motor_4"].drop()
        if input_str=="r5":
            motor_dict["motor_5"].rise()
        if input_str=="d5":
            motor_dict["motor_5"].drop()
        if input_str=="r6":
            motor_dict["motor_6"].rise()
        if input_str=="d6":
            motor_dict["motor_6"].drop()
        if input_str=="r7":
            motor_dict["motor_7"].rise()
        if input_str=="d7":
            motor_dict["motor_7"].drop()
        if input_str=="r8":
            motor_dict["motor_8"].rise()
        if input_str=="d8":
            motor_dict["motor_8"].drop()
        if input_str=="q":
            save_state(motor_dict,state_handler)
            break
        

if __name__=="__main__":
    OrderWhile()
    # testOrder()
    #  main()
