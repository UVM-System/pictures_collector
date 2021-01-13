#!/usr/bin/python3
import json
import queue
'''
利用格雷码(相邻编码只需要变一位) 生成瓶子出现的顺序:尽量减少机械上下
1. ["00", "01", "11", "10"]   
2. ["000", "010", "110", "100", "101", "111", "011", "001"]
......
'''
class GrayCode(object):
    def __init__(self):
        self.base = ["0", "1"]

    def getNext(self , prelist,z_or_one):
        output = []
        for code in prelist:
            new_code = "%s%s" % (z_or_one,code)
            output.append(new_code)
        if z_or_one == 1:
            output.reverse()

        return output

    def gray(self):
        haf1 = self.getNext(self.base, 0)
        haf2 = self.getNext(self.base, 1)
        ret = haf1 + haf2
        self.base = ret            

    def  getGray(self, n): 

        for i in range(n-1):
            self.gray()

        return self.base

def gradcode2OrderDict(code):
    order_dict = {}
    prefix = "motor_"
    for index,each_code in enumerate(code):
        name = prefix +str(index+1)
        value  = True if each_code=='1' else False
        order_dict[name] = value
    return order_dict

if __name__=="__main__":
    gray_code = GrayCode()
    gray_8_list = gray_code.getGray(8)
    ##将000000000放到最后一个位置
    top = gray_8_list.pop(0)
    gray_8_list.append(top)
    

    show_order_list = [gradcode2OrderDict(code) for code in gray_8_list]
    with open('./showOrder.json','w') as file_handler:
        file_handler.write(json.dumps(show_order_list,indent=4))
    #$print(json.dumps(show_order_list))
