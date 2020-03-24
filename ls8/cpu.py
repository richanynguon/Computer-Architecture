"""CPU functionality."""
import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0]*256
        self.reg = [0]*8
        self.running = True
        self.PC = 0
        self.MAR = None  # keep what address reading from
        self.MDR = None  # keeps the data
        self.IR = None
        self.operation_table = {}

        self.operation_table[LDI] = lambda mar, mdr: self.ldi(mar, mdr)
        self.operation_table[PRN] = lambda mar: self.prn(mar)
        self.operation_table[HLT] = lambda: self.hlt()
        self.operation_table[MUL] = lambda mar, mdr: self.mul(mar, mdr)

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        address = 0
        if len(sys.argv) != 2:
            sys.exit(1)
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.split("#")
                    num = comment_split[0].strip()
                    if num == '':
                        continue
                    value = int(num, 2)
                    self.ram[address] = value
                    address += 1
        except FileNotFoundError:
            sys.exit(2)
            address = 0

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL": 
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

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
            if self.IR == PRN:
                self.operation_table[self.IR](operand_a)
            elif self.IR == HLT:
                self.operation_table[self.IR]()
            else:
                self.operation_table[self.IR](operand_a, operand_b)

    def ldi(self, mar, mdr):
        self.reg[mar] = mdr
        self.PC += 3

    def hlt(self):
        self.running = False
        self.PC += 1 
        sys.exit()
   
    def prn(self, mar):
        print(self.reg[mar])
        self.PC += 2

    def mul(self, mar, mdr):
        self.alu("MUL",mar,mdr)
        self.PC +=3