import matplotlib.pyplot as plt
from sys import stdin

def get_n_bit(int_value,n):
    binary_part=str(bin(int_value))[2:]
    bit_n=("0"*(n-len(binary_part)))+binary_part
    return (bit_n)

def get_decimal(binary):
    decimal=int(binary,2)
    return (decimal)

class Register:
    def __init__(self,name,address):
        self.name=name
        self.address=address

        self.data=0

    def store_data(self,data):
        self.data=data

    def get_binary(self):
        return (get_n_bit(self.data,16))

class FLAGS(Register):
    def __init__(self, name, address):
        super().__init__(name, address)

        self.V=0
        self.L=0
        self.G=0
        self.E=0

    def get_binary(self):
        self.binary="0"*12+str(self.V)+str(self.L)+str(self.G)+str(self.E)
        self.data=get_decimal(self.binary)
        return (self.binary)


class Simulator:
    def __init__(self):
        self.input_binaries=[]

        self.list_of_registers=[
            Register("R0","000"),
            Register("R1","001"),
            Register("R2","010"),
            Register("R3","011"),
            Register("R4","100"),
            Register("R5","101"),
            Register("R6","110"),
            FLAGS("FLAGS","111")
            ]

        self.FLAGS=self.list_of_registers[-1]

        self.graph_x=[]
        self.graph_y=[]

    def get_register(self, address):
        for a in self.list_of_registers:
            if a.address==address:
                return (a)

    def set_overflow(self,reg):        
        self.FLAGS.V=1
        reg.data%=65536

    def Type_A(self,binary,command_decimal):
        reg1=self.get_register(binary[7:10])
        reg2=self.get_register(binary[10:13])
        reg3=self.get_register(binary[13:16])

        if command_decimal==0: #Addition
            reg1.data=reg2.data+reg3.data
        elif command_decimal==1: #Subtraction
            if reg2.data<reg3.data:
                reg1.data=0
                self.set_overflow(reg1)
            else:
                reg1.data=reg2.data-reg3.data
        elif command_decimal==6: #Multiplication
            reg1.data=reg2.data*reg3.data
        elif command_decimal==10:
            reg1.data=reg2.data^reg3.data
        elif command_decimal==11:
            reg1.data=reg2.data|reg3.data
        elif command_decimal==12:
            reg1.data=reg2.data&reg3.data

        if reg1.data>65535:
            self.set_overflow(reg1)


    def Type_B(self,binary,command_decimal):
        reg1=self.get_register(binary[5:8])
        immediate=get_decimal(binary[8:])

        if command_decimal==2:
            reg1.data=immediate
        if command_decimal==8:
            reg1.data//=2**immediate
        elif command_decimal==9:
            reg1.data*=2**immediate
            reg1.data%=65536

    def Type_C(self,binary,command_decimal):
        reg1=self.get_register(binary[10:13])
        reg2=self.get_register(binary[13:16])

        if command_decimal==3:
            reg1.data=reg2.data
        elif command_decimal==7:
            self.list_of_registers[0].data==reg1.data//reg2.data
            self.list_of_registers[1].data==reg1.data%reg2.data
        elif command_decimal==13:
            reg1.data=(~reg2.data)%256
        elif command_decimal==14:
            if reg1.data<reg2.data:
                self.FLAGS.L=1
            elif reg1.data>reg2.data:
                self.FLAGS.G=1
            elif reg1.data==reg2.data:
                self.FLAGS.E=1

    def Type_D(self,binary,command_decimal):
        reg1=self.get_register(binary[5:8])
        memory_address=get_decimal(binary[8:])

        if command_decimal==4:
            reg1.data=get_decimal(self.input_binaries[memory_address])
        elif command_decimal==5:
            self.input_binaries[memory_address]=get_n_bit(reg1.data,16)

        self.graph_x.append(self.cycle)
        self.graph_y.append(memory_address)

    def Type_E(self,binary,command_decimal):
        memory_address=get_decimal(binary[8:])

        if (command_decimal==15 or (command_decimal==16 and self.FLAGS.L==1) or
            (command_decimal==17 and self.FLAGS.G==1) or
            (command_decimal==18 and self.FLAGS.E==1)):
            self.jumped=True
            self.new_PC=memory_address

    def reset_FLAGS(self):
        self.FLAGS.V=0
        self.FLAGS.L=0
        self.FLAGS.G=0
        self.FLAGS.E=0

    def get_input(self):
        while True:
            try:
                inp=input()
                if inp=="":
                    continue
                self.input_binaries.append(inp)
                if inp=="1001100000000000": #binary for halt
                    break
            except:
                break

        for a in range(len(self.input_binaries),256):
            self.input_binaries.append("0"*16)
            

    def run_functions(self, binary):
        opcode=binary[:5]
        command_decimal=get_decimal(opcode)

        if command_decimal not in (15,16,17,18):
            self.reset_FLAGS()

        if command_decimal in (0,1,6,10,11,12):
            operation=self.Type_A(binary,command_decimal)
        elif command_decimal in (2,8,9):
            operation=self.Type_B(binary,command_decimal)
        elif command_decimal in (3,7,13,14):
            operation=self.Type_C(binary,command_decimal)
        elif command_decimal in (4,5):
            operation=self.Type_D(binary,command_decimal)
        elif command_decimal in (15,16,17,18):
            operation=self.Type_E(binary,command_decimal)
        elif command_decimal == (19):
            self.halted=True

        if command_decimal not in (0,1,6,14):
            self.reset_FLAGS()

    def print_output(self):
        print (get_n_bit(self.PC,8), end=" ")# file=self.f)
        for a in self.list_of_registers:
            print (a.get_binary(), end=" ")#,file=self.f)
        print ()#file=self.f)
        
    def get_output(self):
        #self.f=open("op.txt","a")
        self.halted=False
        self.PC=0
        self.cycle=0
        while True:
            self.jumped=False
            
            self.run_functions(self.input_binaries[self.PC])
            self.print_output()

            self.graph_x.append(self.cycle)
            self.graph_y.append(self.PC)

            self.cycle+=1

            if self.jumped:
                self.PC=self.new_PC
                continue

            if self.halted:
                break

            self.PC+=1

        for binary in self.input_binaries:
            print (binary)

    def get_graph(self):
        plt.scatter(self.graph_x,self.graph_y)
        plt.xlabel("Cycle Number")
        plt.ylabel("Memory Address")
        plt.show()
            

    def run(self):
        self.get_input()
        self.get_output()
        self.get_graph()

sim=Simulator()
sim.run()
