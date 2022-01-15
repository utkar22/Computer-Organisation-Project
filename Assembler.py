def get_8bit(int_value):
    binary_part=str(bin(int_value))[2:]
    bit_8=("0"*(8-len(binary_part)))+binary_part
    return (bit_8)

def convert_to_decimal(binary):
    decimal=int(binary,2)
    return (decimal)

class Register:
    def __init__(self,name,address):
        self.name=name
        self.address=address

        self.data=None

    def store_data(self,data):
        self.data=data

class FLAGS(Register):
    def __init__(self, name, address):
        super().__init__(name, address)

        self.V=0
        self.L=0
        self.G=0
        self.E=0

    def get_binary(self):
        return ("0"*12+str(self.V)+str(self.L)+str(self.G)+str(self.E))


list_of_registers=[
            Register("R0","000"),
            Register("R1","001"),
            Register("R2","010"),
            Register("R3","011"),
            Register("R4","100"),
            Register("R5","101"),
            Register("R6","110"),
            FLAGS("FLAGS","111")
            ]


class Instruction():
    def get_register(self, register_name):
        for reg in list_of_registers:
            if reg.name==register_name:
                return (reg)

    


class Type_A(Instruction):
    def __init__(self, operation, reg1_name, reg2_name, reg3_name):
        self.reg1=self.get_register(reg1_name)
        self.reg2=self.get_register(reg2_name)
        self.reg3=self.get_register(reg3_name)

        if operation=="add":
            self.Addition()
        elif operation=="sub":
            self.Subtraction()
        elif operation=="mul":
            self.Multiply()
        elif operation=="xor":
            self.Exclusive_OR()
        elif operation=="or":
            self.Or()
        elif operation=="and":
            self.And()

    def Addition(self):
        self.opcode="00000"

    def Subtraction(self):
        self.opcode="00001"

    def Multiply(self):
        self.opcode="00110"

    def Exclusive_OR(self):
        self.opcode="01010"

    def Or(self):
        self.opcode="01011"

    def And(self):
        self.opcode="01100"
        
    def get_binary(self):
        return (str(self.opcode)+("0"*2)+str(self.reg1.address)+str(self.reg2.address)+str(self.reg3.address))



class Type_B(Instruction):
    def __init__(self, operation, reg1_name, immediate_int):
        self.reg1=self.get_register(reg1_name)

        self.immediate_int=int(immediate_int)
        self.immediate_value=get_8bit(self.immediate_int)

        if operation=="mov":
            self.Move()
        elif operation=="rs":
            self.Right_Shift()
        elif operation=="ls":
            self.Left_Shift()

    def Move(self):
        self.opcode="00010"

    def Right_Shift(self):
        self.opcode="01000"

    def Left_Shift(self):
        self.opcode="01001"
        
    def get_binary(self):
        return (str(self.opcode)+str(self.reg1.address)+str(self.immediate_value))


class Type_C(Instruction):
    def __init__(self, operation, reg1_name, reg2_name):
        self.reg1=self.get_register(reg1_name)
        self.reg2=self.get_register(reg2_name)

        if operation=="mov":
            self.Move()
        elif operation=="div":
            self.Divide()
        elif operation=="not":
            self.Invert()
        elif operation=="cmp":
            self.Compare()

    def Move(self):
        self.opcode="00011"

    def Divide(self):
        self.opcode="00111"

    def Invert(self):
        self.opcode="01101"

    def Compare(self):
        self.opcode="01110"
        
    def get_binary(self):
        return (str(self.opcode)+str("00000")+str(self.reg1.address)+str(self.reg2.address))


class Type_D(Instruction):
    def __init__(self, operation, reg1_name, memory_address):
        self.reg1=self.get_register(reg1_name)

        self.memory_address=memory_address

        if operation=="ld":
            self.Load()
        elif operation=="st":
            self.Store()

    def Load(self):
        self.opcode="00100"

    def Store(self):
        self.opcode="00101"

    def get_binary(self):
        return (str(self.opcode)+str(self.reg1.address)+str(self.memory_address))

class Type_E(Instruction):
    def __init__(self, operation, memory_address):
        self.memory_address=memory_address

        if operation=="jmp":
            self.Unconditional_Jump()
        elif operation=="jlt":
            self.Jump_If_Less_Than()
        elif operation=="jgt":
            self.Jump_If_Greater_Than()
        elif operation=="je":
            self.Jump_If_Equal()

    def Unconditional_Jump(self):
        self.opcode="01111"

    def Jump_If_Less_Than(self):
        self.opcode="10000"

    def Jump_If_Greater_Than(self):
        self.opcode="10001"

    def Jump_If_Equal(self):
        self.opcode="10010"

    def get_binary(self):
        return (str(self.opcode)+str("000")+str(self.memory_address))

class Type_F(Instruction):
    def __init__(self, operation):

        if operation=="hlt":
            self.Halt()

    def Halt(self):
        self.opcode="10011"
        
    def get_binary(self):
        return (str(self.opcode)+("0"*11))




class ISA:
    def __init__(self):
        self.FLAGS_register=list_of_registers[-1]
        self.usable_registers=["R0","R1","R2","R3","R4","R5","R6"]

        self.types_of_commands()

        self.list_of_errors=[]
        self.if_errors=False

        self.binaries=[]

    def types_of_commands(self):
        self.Type_A_commands=["add","sub","mul","xor","or","and"]
        self.Type_B_commands=["mov","rs","ls"]
        self.Type_C_commands=["mov","div","not","cmp"]
        self.Type_D_commands=["ld","st"]
        self.Type_E_commands=["jmp","jlt","jgt","je"]
        self.Type_F_commands=["hlt"]

        self.valid_commands=(self.Type_A_commands+self.Type_B_commands+
                             self.Type_C_commands+self.Type_D_commands+
                             self.Type_E_commands+self.Type_F_commands)

    def check_name(self, s):
        for a in s:
            if not(a.isalnum() or a=="_"):
                return (False)
        if (s in self.valid_commands) or (s=="var"):
            return (False)
        return (True)

    def add_command(self, inp_list):
        if inp_list[0][-1]==":":
            if self.check_name(inp_list[0][:-1]):
                if len(inp_list) in range(2,6) and (inp_list[1] in self.valid_commands):
                    self.labels[inp_list[0][:-1]]=inp_list[1:]
                    self.labels_binaries[inp_list[0][:-1]]=get_8bit(self.line_number)
                    self.commands.append(inp_list)
                else:
                    self.print_error("Syntax Error in Label definition.")
            else:
                self.print_error("Invalid Label Name")
        else:
            self.commands.append(inp_list)

    def store_values(self):
        self.variables=[]
        self.labels={}
        self.labels_binaries={}
        self.commands=[]

        get_variables=True
        
        self.line_number=-1
        
        while True:
            try:
                inp=input()
            except:
                break

            if inp=="":
                continue
            
            inp_list=inp.split()
            
            if get_variables:
                if inp_list[0]=="var":
                    if len(inp_list)==2:
                        if inp_list[1] not in self.variables:
                            if self.check_name(inp_list[1]):
                                self.variables.append(inp_list[1])
                            else:
                                self.print_error("Invalid Variable Name")
                        else:
                            self.print_error(f"Variable {inp_list[1]} already defined.")
                    else:
                        self.print_error("Incorrect variable syntax.")
                        break
                else:
                    self.line_number=0
                    self.add_command(inp_list)
                    get_variables=False
            else:
                self.line_number+=1
                if inp_list[0]=="var":
                    self.print_error("Variable not declared at the beginning.")
                    break
                else:
                    self.add_command(inp_list)
                if "hlt" in inp:
                    break

    def get_variable_binaries(self):
        self.variables_dict={}
        
        i=len(self.commands)
        for a in self.variables:
            self.variables_dict[a]=get_8bit(i)
            i+=1

    def print_error(self, error):
        self.if_errors=True
        if self.line_number>=0:
            self.list_of_errors.append(f"ERROR at line {self.line_number+1}: {error}")
        else:
            self.list_of_errors.append(f"ERROR: {error}")
            
    def get_operation(self, inp_list):
        command=inp_list[0]

        f=0 #Flag, to check if there is no syntax error
        operation=None

        if command=="mov":
            if len(inp_list)==3:
                if inp_list[2] in (self.usable_registers+["FLAGS"]):
                    if inp_list[1] in self.usable_registers:
                        operation=Type_C(operation=command, reg1_name=inp_list[1], reg2_name=inp_list[2])
                        f=1
                    elif inp_list[1]=="FLAGS":
                        self.print_error("Illegal use of FLAGS register.")
                    else:
                        self.print_error("Invalid Register Name")
                else:
                    if inp_list[2][0]=="$" and inp_list[2][1:].isdecimal():
                        if inp_list[1] in self.usable_registers:
                            immediate_int=int(inp_list[2][1:])
                            if 0<=immediate_int<=255:
                                operation=Type_B(operation=command, reg1_name=inp_list[1], immediate_int=immediate_int)
                                f=1
                            else:
                                self.print_error("Immediate Value out of bounds (can only be between 0 and 255")
                        elif inp_list[1]=="FLAGS":
                            self.print_error("Illegal use of FLAGS register.")
                        else:
                            self.print_error("Invalid Register Name")
                    else:
                        self.print_error("Error in Register 2 or Immediate Value")
            else:
                self.print_error("Invalid Syntax")

        elif command in self.Type_A_commands:
            if len(inp_list)==4:
                if (inp_list[1] in self.usable_registers and inp_list[2] in self.usable_registers
                    and inp_list[3] in self.usable_registers):
                    operation=Type_A(operation=command, reg1_name=inp_list[1], reg2_name=inp_list[2], reg3_name=inp_list[3])
                    f=1
                elif inp_list[1]=="FLAGS" or inp_list[2]=="FLAGS" or inp_list[3]=="FLAGS":
                    self.print_error("Illegal use of FLAGS register.")
                else:
                    self.print_error("Error in Register name.")
            else:
                self.print_error("Invalid Syntax")

        elif command in self.Type_B_commands:
            if len(inp_list)==3:
                if inp_list[1] in self.usable_registers:
                    if inp_list[2][0]=="$" and inp_list[2][1:].isdecimal():
                        immediate_int=int(inp_list[2][1:])
                        if 0<=immediate_int<=255:
                            operation=Type_B(operation=command, reg1_name=inp_list[1], immediate_int=immediate_int)
                            f=1
                        else:
                            self.print_error("Immediate Value out of bounds (can only be between 0 and 255")
                    else:
                        self.print_error("Invalid Immediate Value")
                elif inp_list[1]=="FLAGS":
                    self.print_error("Illegal use of FLAGS register.")
                else:
                    self.print_error("Invalid Register name")
            else:
                self.print_error("Invalid Syntax")

        elif command in self.Type_C_commands:
            if len(inp_list)==3:
                if (inp_list[1] in self.usable_registers and inp_list[2] in self.usable_registers):
                    operation=Type_C(operation=command, reg1_name=inp_list[1], reg2_name=inp_list[2])
                    f=1
                elif inp_list[1]=="FLAGS" or inp_list[2]=="FLAGS":
                    self.print_error("Illegal use of FLAGS register.")
                else:
                    self.print_error("Invalid Register name.")
            else:
                self.print_error("Invalid Syntax")

        elif command in self.Type_D_commands:
            if len(inp_list)==3:
                if inp_list[1] in self.usable_registers:
                    if inp_list[2] in self.variables:
                        operation=Type_D(operation=command, reg1_name=inp_list[1], memory_address=self.variables_dict[inp_list[2]])
                        f=1
                    elif inp_list[2] in self.labels:
                        self.print_error("Attempted to use Label as Variable")
                    else:
                        self.print_error("Invalid Memory Address")
                elif inp_list[1]=="FLAGS":
                    self.print_error("Illegal use of FLAGS register.")
                else:
                    self.print_error("Invalid Register name.")
            else:
                self.print_error("Invalid Syntax")

        elif command in self.Type_E_commands:
            if len(inp_list)==2:
                if inp_list[1] in self.labels:
                    operation=Type_E(operation=command, memory_address=self.labels_binaries[inp_list[1]])
                    f=1
                elif inp_list[1] in self.labels:
                        self.print_error("Attempted to use variable as label")
                else:
                    self.print_error("Invalid Memory Address")
            else:
                self.print_error("Invalid Syntax")

        elif command in self.Type_F_commands:
            if len(inp_list)==1:
                operation=Type_F(operation=command)
                self.halted=True
                f=1
            else:
                self.print_error("Invalid Syntax")

        else:
            self.print_error("Invalid Command.")

        return (operation,f)

    def get_all_binaries(self):
        self.line_number=0
        self.halted=False
        for a in self.commands:
            if self.halted==True:
                self.print_error("Commands given after program has already been halted.")
            if a[0][-1]==":":   
                operation,f=self.get_operation(a[1:])
            else:
                operation,f=self.get_operation(a)
            if f:
                self.binaries.append(operation.get_binary())
            self.line_number+=1

        if self.halted==False:
            self.line_number=-1
            self.print_error("Program not halted.")

    def print_output(self):
        if self.if_errors:
            l=self.list_of_errors
        else:
            l=self.binaries

        for a in l:
            print (a)

    def run(self):
        self.store_values()
        self.get_variable_binaries()
        self.get_all_binaries()
        self.print_output()


isa=ISA()
isa.run()
