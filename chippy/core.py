import os
import pkg_resources
import numpy as np
from .instructions import Opcode, InstructionSet
from . import graphics
from . import keyboard

FONTSET = [
    0xf0, 0x90, 0x90, 0x90, 0xf0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xf0, 0x10, 0xf0, 0x80, 0xf0,  # 2
    0xf0, 0x10, 0xf0, 0x10, 0xf0,  # 3
    0x90, 0x90, 0xf0, 0x10, 0x10,  # 4
    0xf0, 0x80, 0xf0, 0x10, 0xf0,  # 5
    0xf0, 0x80, 0xf0, 0x90, 0xf0,  # 6
    0xf0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xf0, 0x90, 0xf0, 0x90, 0xf0,  # 8
    0xf0, 0x90, 0xf0, 0x10, 0xf0,  # 9
    0xf0, 0x90, 0xf0, 0x90, 0x90,  # A
    0xe0, 0x90, 0xe0, 0x90, 0xe0,  # B
    0xf0, 0x80, 0x80, 0x80, 0xf0,  # C
    0xe0, 0x90, 0x90, 0x90, 0xe0,  # D
    0xf0, 0x80, 0xf0, 0x80, 0xf0,  # E
    0xf0, 0x80, 0xf0, 0x80, 0x80,  # F
    0x7f, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x7f,  # 0
    0x08, 0x18, 0x28, 0x08, 0x08, 0x08, 0x08, 0x08, 0x08, 0x7f,  # 1
    0x7f, 0x01, 0x01, 0x01, 0x7f, 0x40, 0x40, 0x40, 0x40, 0x7f,  # 2
    0x7f, 0x01, 0x01, 0x01, 0x7f, 0x01, 0x01, 0x01, 0x01, 0x7f,  # 3
    0x41, 0x41, 0x41, 0x41, 0x7f, 0x01, 0x01, 0x01, 0x01, 0x01,  # 4
    0x7f, 0x40, 0x40, 0x40, 0x7f, 0x01, 0x01, 0x01, 0x01, 0x7f,  # 5
    0x7f, 0x40, 0x40, 0x40, 0x7f, 0x41, 0x41, 0x41, 0x41, 0x7f,  # 6
    0x7f, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01,  # 7
    0x7f, 0x41, 0x41, 0x41, 0x7f, 0x41, 0x41, 0x41, 0x41, 0x7f,  # 8
    0x7f, 0x41, 0x41, 0x41, 0x7f, 0x01, 0x01, 0x01, 0x01, 0x7f,  # 9
]


class Machine(object):
    MEMORY = 4096            # Total machine memory (bytes)
    PC_START = 512           # Program counter start
    MAX_FILE_SIZE = 3584     # Limit on ROM size
    REGISTERS = 16           # Number of registers

    def __init__(self):
        self.game = ''                          # Game title

        self.I = np.uint16(0)                   # Index register
        self.pc = np.uint16(Machine.PC_START)   # Program counter
        self.delay_timer = np.uint16(0)         # Delay timer
        self.sound_timer = np.uint16(0)         # Sound timer

        self.memory = np.zeros(Machine.MEMORY, np.uint8)  # 4K Emulated memory
        self.V = np.zeros(Machine.REGISTERS, np.uint8)    # 8-bit registers
        self.stack = []                                 # Stack for subroutines

        # UI handling
        self.gfx = graphics.GFX()
        self.keyboard = keyboard.HexKeyboard()

    def reset(self):
        self.I = np.uint16(0)
        self.pc = np.uint16(Machine.PC_START)
        self.delay_timer = np.uint16(0)
        self.sound_timer = np.uint16(0)
        self.stack = []
        self.V = np.zeros(Machine.REGISTERS, np.uint8)
        self.gfx.clear()
        self.keyboard.reset()

    def load_game(self, game_path):
        self.reset()
        PC0 = Machine.PC_START
        MAX_FILE_SIZE = Machine.MAX_FILE_SIZE
        NUMBER_OF_FONTS = len(FONTSET)

        # Get absolute path to game
        if not os.path.isabs(game_path):
            game_path = pkg_resources.resource_filename(__name__, game_path)

        # Set game name
        self.game = os.path.basename(os.path.splitext(game_path)[0]).upper()

        # Determine file size
        file_size = os.path.getsize(game_path)
        if file_size > MAX_FILE_SIZE:
            print("ROM must not exceed {} bytes.".format(MAX_FILE_SIZE))
            return

        # Read from file
        with open(game_path, 'rb') as game_file:
            byte_data = [byte for byte in game_file.read()]
            if isinstance(byte_data[0], str):  # Python 2 check
                byte_data = map(ord, byte_data)

            self.memory[:NUMBER_OF_FONTS] = FONTSET
            self.memory[PC0:PC0 + file_size] = byte_data

    def fetch_opcode(self):
        lh_op = self.memory[self.pc]
        rh_op = self.memory[self.pc + 1]
        return Opcode.from_pair(lh_op, rh_op) 

    def emulate_cycle(self):
        if self.keyboard.is_reset():
            self.reset()

        elif self.keyboard.is_paused() or self.keyboard.is_exit():
            return

        else:
            opcode = self.fetch_opcode()             # Fetch
            self.pc += 2
            instruction = InstructionSet(opcode)     # Decode
            instruction.execute(self)                # Execute

    def decrement_timers(self):
        if self.keyboard.is_paused() or self.keyboard.is_exit():
            return

        # Update timers
        self.delay_timer -= np.uint16(self.delay_timer > 0)
        self.sound_timer -= np.uint16(self.sound_timer > 0)
        # if(self.sound_timer == 1):
        #     print('\a')
