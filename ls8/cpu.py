"""CPU functionality."""
import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.running = True
        self.ram = [0]*256
        self.reg = [0]*8
        self.reg[7] = 0xF4
        self.PC = 0
        self.FL = 0
        self.IR = None

        self.branch_table = {}

        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        PUSH = 0b01000101
        POP = 0b01000110
        RET = 0b00010001
        CALL = 0b01010000
        # ALU
        MUL = 0b10100010
        ADD = 0b10100000

        self.branch_table[LDI] = lambda mar, mdr: self.ldi(mar, mdr)
        self.branch_table[PRN] = lambda mar, __: self.prn(mar)
        self.branch_table[HLT] = lambda _, __: self.hlt()
        self.branch_table[MUL] = lambda mar, mdr: self.mul(mar, mdr)
        self.branch_table[PUSH] = lambda mar, __: self.push(mar)
        self.branch_table[POP] = lambda mar, __: self.pop(mar)
        self.branch_table[RET] = lambda _, __: self.ret()
        self.branch_table[CALL] = lambda mar, __: self.call(mar)
        self.branch_table[ADD] = lambda mar, mdr: self.add(mar, mdr)

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        # address = 0
        # if len(sys.argv) != 2:
        #     sys.exit(1)
        # try:
        #     with open(sys.argv[1]) as f:
        #         for line in f:
        #             comment_split = line.split("#")
        #             num = comment_split[0].strip()
        #             if num == '':
        #                 continue
        #             value = int(num, 2)
        #             self.ram[address] = value
        #             address += 1
        # except FileNotFoundError:
        #     sys.exit(2)
        #     address = 0
        address = 0
        instructions = [
                        0b10000010,  # LDI R1,MULT2PRINT
                        0b00000001,
                        0b00011000,
                        0b10000010,  # LDI R0,10
                        0b00000000,
                        0b00001010,
                        0b01010000,  # CALL R1
                        0b00000001,
                        0b10000010,  # LDI R0,15
                        0b00000000,
                        0b00001111,
                        0b01010000,  # CALL R1
                        0b00000001,
                        0b10000010,  # LDI R0,18
                        0b00000000,
                        0b00010010,
                        0b01010000,  # CALL R1
                        0b00000001,
                        0b10000010,  # LDI R0,30
                        0b00000000,
                        0b00011110,
                        0b01010000,  # CALL R1
                        0b00000001,
                        0b00000001,  # HLT
                        # MULT2PRINT (address 24):
                        0b10100000,  # ADD R0,R0
                        0b00000000,
                        0b00000000,
                        0b01000111,  # PRN R0
                        0b00000000,
                        0b00010001,  # RET
                        ]
        for line in instructions:
            self.ram[address] = line
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU branchs."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU branch")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.PC,
            # self.fl,
            # self.ie,
            self.ram_read(self.PC),
            self.ram_read(self.PC + 1),
            self.ram_read(self.PC + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        while self.running:
            self.IR = self.ram_read(self.PC)
            operand_a = self.ram_read(self.PC+1)
            operand_b = self.ram_read(self.PC+2)
            self.PC += (self.IR >> 6)+1
            self.branch_table[self.IR](operand_a, operand_b)

    def ldi(self, mar, mdr):
        self.reg[mar] = mdr

    def hlt(self):
        self.running = False
        sys.exit()

    def prn(self, mar):
        print(self.reg[mar])

    def mul(self, mar, mdr):
        self.alu("MUL", mar, mdr)

    def push(self, mar):
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.reg[mar])

    def pop(self, mar):
        self.ldi(mar, self.ram[self.reg[7]])
        self.reg[7] += 1

    def add(self, mar, mdr):
        self.alu("ADD", mar, mdr)

    def ret(self):
        self.PC = self.ram[self.reg[7]]
        self.reg[7] += 1

    def call(self, mar):
        self.reg[7] -= 1
        self.ram_write(self.reg[7], self.PC)
        self.PC = self.reg[mar]
