#! C:\Users\ivanp\AppData\Local\Programs\Python\Python310\python.exe
'''
Created on November xx, 2021
Authors:    Reyes Sánchez Luis Angel    
            Rivera Orozco David
            Rosales Galindo Elias
            Tacuapan Moctezuma Edgar
'''

import re
import sys
import msvcrt
import time
import random
import os

class TB_getdata(object):
    #Properties
    #Private
    __pattern_timescale = r"^\s*timescale\s*=\s*(\w+\/\w+).*$"
    __pattern_delay = r"^\s*delay\s*=\s*(\#\d+).*$"
    __pattern_dumpvars = r"^\s*dumpvars\s*=\s*(\d+).*$"
    __pattern_cases = r"^\s*num_cases\s*=\s*(\d+).*$"
    __pattern_names = r"(\w+)"
    __pattern_in_bus = r"^\s*input\s*\[\s*(\d+)\s*:.*]\s*(\w+,?.*)[;,]"
    __pattern_in_nbus = r"^\s*input\s*(\w+,?.*)[;,]"
    __pattern_module = r"^module\s*(\w+)"
    __pattern_out_bus_nreg = r"^\s*output\s*\[\s*(\d+)\s*:.*]\s*(\w+,?.*)[;,]"   # output [1:0] q,
    __pattern_out_bus_reg = r"^\s*output\s*reg?\s*(\[\s*\d+\s*:\s*\d+\s*\])?\s+(.*)[;,]"   # output reg out,
    __pattern_out_nbus = r"^\s*output\s*(?!reg)(\w+.*)[;,]"  #   output u, v, w, output b, 
    __pattern_inst_modules = r"^\s*(?!module)(\w+)\s*\w+\s*\(.+\);"
    #Public
    conf = None
    File = None
    m = None
    timescale = None
    delay = None
    dumpvars = None
    num_cases = 0
    module_name = ''
    in_match = {}
    list_input = []
    list_input_size = []
    out_match = {}
    list_output = []
    list_output_size = []
    sv_file = None
    instantiated_modules =[]
    #Constructor
    def __init__(self, File, conf):
        self.File = File
        self.conf = conf
        self.config()
        self.inputs()
        self.module()
        self.outputs()
        self.inst_modules()
    #Member Functions
    def config(self):
        for line in open(self.conf,'r',encoding='utf8'):
            if(re.match(self.__pattern_timescale,line)):
                self.m = re.search(self.__pattern_timescale,line)
                self.timescale = self.m.group(1)
            elif(re.match(self.__pattern_delay,line)):
                self.m = re.search(self.__pattern_delay,line)
                self.delay = self.m.group(1)
            elif(re.match(self.__pattern_dumpvars,line)):
                self.m = re.search(self.__pattern_dumpvars,line)
                self.dumpvars = self.m.group(1)
            elif(re.match(self.__pattern_cases,line)):
                self.m = re.search(self.__pattern_cases,line)
                self.num_cases = int(self.m.group(1))
        #Quitar despues, solo impresion de variables
        #Checar los errores de no match
        #print(self.timescale)
        #print(self.delay)
        #print(self.dumpvars)
        #print(self.num_cases)    
    
    def inst_modules(self):
        self.sv_file = open(self.File, 'r',encoding = 'utf8')
        matches = re.finditer(self.__pattern_inst_modules, self.sv_file.read(), re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            self.instantiated_modules.append(match.group(1))
        self.instantiated_modules = list(dict.fromkeys(self.instantiated_modules))
        #print(self.instantiated_modules)

    def inputs(self):
        for line in open(self.File,'r',encoding='utf8'):
            if(re.match(self.__pattern_in_bus,line)):
                self.m = re.search(self.__pattern_in_bus,line)
                self.in_match[self.m.group(2)] = int(self.m.group(1)) + 1
            elif(re.match(self.__pattern_in_nbus,line)):
                self.m = re.search(self.__pattern_in_nbus,line)
                self.in_match[self.m.group(1)] = 1
        for key in self.in_match:
            self.m = re.findall(self.__pattern_names,key)
            for i in range(0,len(self.m)):
                self.list_input_size.append(self.in_match[key])
            if (len(self.m) != 0):
                self.list_input.extend(self.m)
        #print(self.list_input)
        #print(self.list_input_size)

    def outputs(self):
        for linea in open(self.File,'r',encoding='utf8'):
            if(re.match(self.__pattern_out_bus_nreg,linea)):
                n = re.search(self.__pattern_out_bus_nreg,linea)
                self.out_match[n.group(2)] = int(n.group(1))+1
            elif (re.match(self.__pattern_out_nbus,linea)):
                n = re.search(self.__pattern_out_nbus,linea)
                self.out_match[n.group(1)] = 1
            elif (re.match(self.__pattern_out_bus_reg,linea)):
                n = re.search(self.__pattern_out_bus_reg,linea)
                if n.group(1) is None:
                    self.out_match[n.group(2)] = int(1)
                else:
                    tamaño = re.search("\d",linea)
                    #u = n.group(1)
                    self.out_match[n.group(2)] = int(tamaño.group(0)) + 1
        for key in self.out_match:
            n = re.findall(self.__pattern_names,key)
            for x in range(0,len(n)):
                self.list_output_size.append(self.out_match[key])
            if(len(n) != 0):
                self.list_output.extend(n)
        #print(self.out_match)
        #print(self.list_output)
        #print(self.list_output_size)
    
    def module(self):
        self.sv_file = open(self.File, 'r',encoding = 'utf8')
        matches = re.finditer(self.__pattern_module, self.sv_file.read(), re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):  
            match = match.group()
        self.module_name = match.replace('module ', '')
        #print(self.module_name)

    def get_Header(self):
        return self.timescale,self.instantiated_modules,self.module_name

    def get_In_Out(self):
        return self.list_input_size,self.list_input,self.list_output_size,self.list_output

    def get_Initial_Begin(self):
        return self.dumpvars,self.num_cases,self.delay

class TB_writedata(object):
    # Properties
    # Private
    delay = None
    dumpvars = None
    timescale = None
    num_cases = None
    #clk = '#5'
    #Public
    output_File = None
    module_name = ''
    list_input = []
    list_input_size = []
    list_output = []
    list_output_size = []
    instantiated_modules =[]
    num_in=None
    num_out=None
    num_mod=None
    flag1 = False   #there are inputs
    flag2 = False   #there are outputs
    TB = None
    #Constructor
    def __init__(self,output_File):
        self.output_File = output_File
        self.TB = open(self.output_File,'w',encoding="utf8")
    #Member functions
    def Header(self,timescale,instantiated_modules,module_name):
        self.timescale = timescale
        self.instantiated_modules = instantiated_modules
        self.module_name = module_name
        self.num_mod = len(self.instantiated_modules)
        self.TB = open(self.output_File,'w',encoding="utf8")   #open the testbench file

        self.TB.write("`timescale %s\n" %self.timescale)               #write timescale

        if(self.num_mod!=0):               #see if there are any instantiated modules
            for i in range(0,self.num_mod):
                self.TB.write('`include "%s.sv"\n' %self.instantiated_modules[i]) #if so, include them

        self.TB.write("\nmodule %s_TB;\n" %self.module_name)     #write module_name_TB;

    def In_Out(self,lis_in_s,lis_in,lis_out_s,lis_out):
        self.list_input_size = lis_in_s
        self.list_input = lis_in
        self.list_output_size = lis_out_s
        self.list_output = lis_out
        #inputs
        inputs=[[] for x in range(max(self.list_input_size))]    #create a list of lists according to the max bit size value

        for j in range(0,len(self.list_input)):
            inputs[self.list_input_size[j]-1].append(self.list_input[j])

        for i in range(0,len(inputs)):
            if (inputs[i]):
                if i+1 == 1:
                    self.TB.write("  reg ")
                    for j in range(0,len(inputs[i])):
                        if(j == len(inputs[i])-1):
                            self.TB.write("%s;\n" %inputs[i][j])
                            break
                        self.TB.write("%s, " %inputs[i][j])
                else:
                    self.TB.write("  reg [%i:0] " %i)
                    for j in range(0,len(inputs[i])):
                        if(j == len(inputs[i])-1):
                            self.TB.write("%s;\n" %inputs[i][j])
                            break
                        self.TB.write("%s, " %inputs[i][j])

        #outputs
        outputs=[[] for x in range(max(self.list_output_size))]    #create a list of lists according to the max bit size value

        for j in range(0,len(self.list_output)):
            outputs[self.list_output_size[j]-1].append(self.list_output[j])

        for i in range(0,len(outputs)):
            if (outputs[i]):
                if i+1 == 1:
                    self.TB.write("  wire ")
                    for j in range(0,len(outputs[i])):
                        if(j == len(outputs[i])-1):
                            self.TB.write("%s;\n" %outputs[i][j])
                            break
                        self.TB.write("%s, " %outputs[i][j])
                else:
                    self.TB.write("  wire [%i:0] " %i)
                    for j in range(0,len(outputs[i])):
                        if(j == len(outputs[i])-1):
                            self.TB.write("%s;\n" %outputs[i][j])
                            break
                        self.TB.write("%s, " %outputs[i][j])
            
    def DUT(self):
        self.num_in = len(self.list_input)
        self.num_out = len(self.list_output)
        self.TB.write("\n  %s DUT(" %(self.module_name))   #initiate DUT

        if(self.num_in!=0):                          #check if there are inputs
            for i in range(0,self.num_in):
                if(i==self.num_in-1):                #if it is the last inputs
                    if(self.num_out!=0):             #if there are outputs, then finish the line with ,\n
                        self.TB.write(".%s(%s_TB),\n              " %(self.list_input[i],self.list_input[i]))
                        break
                    else:
                        self.TB.write(".%s(%s_TB));\n" %(self.list_input[i],self.list_input[i])) #if there are no outputs, finish line with );
                else:
                    self.TB.write(".%s(%s_TB), " %(self.list_input[i],self.list_input[i]))
        else:
            self.flag1 = True    #if there are no inputs flag1=true

        if(self.num_out!=0):                         #check if there are outputs
            for i in range(0,self.num_out):
                if(i==self.num_out-1):
                    self.TB.write(".%s(%s_TB));\n" %(self.list_output[i],self.list_output[i]))  #if it is the last output, finish line with );
                else:
                    self.TB.write(".%s(%s_TB), " %(self.list_output[i],self.list_output[i]))    #else, keep writing outputs
        else:
            self.flag2 = True    #if there are no outputs flag2=True

        if(self.flag1 and self.flag2):    #if no inputs and no outputs, then write );\n for the DUT
            self.TB.write(");\n")
    
    def Initial_Begin(self,dumpvars,num_cases,delay):
        self.dumpvars = dumpvars
        self.num_cases = num_cases
        self.delay = delay
        #write initial begin and configuration
        self.TB.write('\n  intial begin\n    $dumpfile("%s.vcd");\n    $dumpvars(%s,%s_TB);\n\n' %(self.module_name,self.dumpvars,self.module_name))
        #number of signal changes
        num_bits = sum(self.list_input_size) #num of input bits
        num_totcases = 2**num_bits      #total number of combinations
        if(num_totcases>self.num_cases):
            cases_used = self.num_cases
        else:
            cases_used = num_totcases
        in_vector = ''
        if(not self.flag1):  #if there are inputs
            for i in range(0,self.num_in): #write inputs vector and bit vector
                if(i==self.num_in-1):        #if in the last input
                    in_vector = in_vector+'%s' %(self.list_input[i]) #write only input
                else:
                    in_vector = in_vector+'%s,' %(self.list_input[i])    #else, write a comma
            self.TB.write("    {%s} = %i'b%s; %s\n" %(in_vector,num_bits,f'{0:0{num_bits}b}',self.delay))   #Case in = 0
            for i in range(0,cases_used-2):       #minus case=0 and case=max_value
                value = random.randrange(1,num_totcases-2)
                self.TB.write("    {%s} = %i'b%s; %s\n" %(in_vector,num_bits,f'{value:0{num_bits}b}',self.delay))     #random cases
            self.TB.write("    {%s} = %i'b%s; %s\n" %(in_vector,num_bits,f'{num_totcases-1:0{num_bits}b}',self.delay))   #Case in = max_value
        self.TB.write('\n    $finish;\n  end\nendmodule')
        self.TB.close()
        
if __name__ == '__main__':

    start = time.time()

    print('''********************** Testbench Generator **********************''')
    output_File = "testbench.sv"
    conf = "conf.ini"
    if (len(sys.argv) == 1):
        sys.stderr.write("\n[ERROR]: No argument has been declared\n")
        print("Use the following syntax: main.py [file.sv] [output.sv] [conf.ini]")
        sys.exit(1)
    elif(len(sys.argv) == 2):   
        File = sys.argv[1]
    elif(len(sys.argv) == 3):
        File = sys.argv[1]
        output_File = sys.argv[2]
    elif(len(sys.argv) == 4):
        File = sys.argv[1]
        output_File = sys.argv[2]
        conf = sys.argv[3]

    reader = TB_getdata(File,conf)
    writer = TB_writedata(output_File)
    data = reader.get_Header()
    writer.Header(data[0],data[1],data[2])
    data = reader.get_In_Out()
    writer.In_Out(data[0],data[1],data[2],data[3])
    writer.DUT()
    data = reader.get_Initial_Begin()
    writer.Initial_Begin(data[0],data[1],data[2])
    print(f"\nTestbench generated in: {os.getcwd()}\\{output_File}")
    #End Program 
    end = time.time()
    print("\nPress a key to continue ...")
    msvcrt.getch()
    print(f"Execution Time: {end-start}")
    print(".....................................")
    print('''
Created on November 2021
Authors:    Reyes Sánchez Luis Angel    
            Rivera Orozco David
            Rosales Galindo Elias
            Tacuapan Moctezuma Edgar
''')