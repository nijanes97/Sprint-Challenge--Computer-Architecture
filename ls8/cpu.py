"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256

        self.pc = self.reg[0]
        self.pointstack = 0

        self.flag = {
            'E': 0,
            'L': 0,
            'G': 0
        }

        self.commands = {
            0b00000001: self.HLT,  # 1
            0b00010001: self.ret,  # 17
            0b01000101: self.push, # 69
            0b01000110: self.pop,  # 70
            0b01000111: self.PRN,  # 71
            0b01010000: self.call, # 80
            0b01010100: self.JMP,  # 84
            0b01010101: self.JEQ,  # 85
            0b01010110: self.JNE,  # 86
            0b10000010: self.LDI,  # 130
            0b10100000: self.ADD,  # 160
            0b10100010: self.MUL,  # 162
            0b10100111: self.CMP,  # 167
        }


    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def HLT(self, operand_a, operand_b):
        return (0, False)

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        return (self.pc + 3, True)
    
    def PRN(self, operand_a, operand_b):
        print(self.reg[operand_a])
        return (self.pc + 2, True)

    def MUL(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        return (self.pc + 3, True)

    def ADD(self, operand_a, operand_b):
        self.alu("ADD", operand_a, operand_b)
        return (self.pc + 3, True)

    def CMP(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        return (self.pc + 3, True)

    def JMP(self, operand_a, operand_b):
        target = self.ram_read(self.pc + 1)
        return (self.reg[target], True)

    def JNE(self, operand_a, operand_b):
        if not self.flag['E']:
            return (self.reg[operand_a], True)
        else:
            return (self.pc + 2, True)

    def JEQ(self, operand_a, operand_b):
        if self.flag['E']:
            return (self.reg[operand_a], True)
        else:
            return (self.pc + 2, True)

    def push(self, operand_a, operand_b):
        self.pointstack += 1
        temp = self.reg[operand_a]
        self.ram_write(self.pointstack, temp)
        return (self.pc + 2, True)

    def pop(self, operand_a, operand_b):
        temp = self.ram_read(self.pointstack)
        self.reg[operand_a] = temp
        self.pointstack -= 1

        return (self.pc + 2, True)

    def call(self, operand_a, operand_b): 
        self.pointstack -= 1
        self.ram_write(self.pointstack, self.pc + 2)
        return (self.reg[operand_a], True)

    def ret(self, operand_a, operand_b):
        value = self.ram_read(self.pointstack)
        self.pointstack += 1
        return (value, True)

    def load(self):
        """Load a program into memory."""

        address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        f = open(sys.argv[1])

        for line in f:
            command = line.split('#')
            number = command[0].strip()

            if number == '' or number == '#':
                continue
            
            value = int(number, 2)
            self.ram_write(address, value)
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag['G'] = 1
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag['L'] = 1
            else:
                self.flag['E'] = 1
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            IR = self.ram[self.pc]

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if IR in self.commands:
                output = self.commands[IR](operand_a, operand_b)
                running = output[1]
                self.pc = output[0]
            else:
                print(f"Invalid Command {IR}")
                sys.exit(1)
