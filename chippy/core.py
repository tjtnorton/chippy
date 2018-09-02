import os
import numpy as np
from . import graphics
from . import keyboard
from instructions import Opcode, InstructionSet

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
]


class Machine(object):
    # Class constants
    _CAPTION = "Chip8 Emulator. Current game: {}"

    _MEMORY = 4096            # Total machine memory (bytes)
    _PC0 = 512                # Program counter start
    _REGISTERS = 16           # Number of registers

    def __init__(self):
        self.caption = Machine._CAPTION.format('None')

        self.I = np.uint16(0)              # Index register
        self.pc = np.uint16(self._PC0)     # Program counter
        self.delay_timer = np.uint16(0)    # Delay timer
        self.sound_timer = np.uint16(0)    # Sound timer

        self.memory = np.zeros(self._MEMORY, np.uint8)  # 4K Emulated memory
        self.V = np.zeros(self._REGISTERS, np.uint8)    # 8-bit registers
        self.stack = []                                 # Stack for subroutines

        # UI handling
        self.gfx = graphics.GFX()
        self.keyboard = keyboard.HexKeyboard()

    def reset(self):
        self.I = np.uint16(0)
        self.pc = np.uint16(self._PC0)
        self.delay_timer = np.uint16(0)
        self.sound_timer = np.uint16(0)
        self.stack = []
        self.V = np.zeros(self._REGISTERS, np.uint8)
        self.gfx.clear()
        self.keyboard.reset()

    def load_game(self, fname):
        self.reset()

        # Get absolute path to game
        if not os.path.isabs(fname):
            fname = os.path.join(os.getcwd(), fname)
        print(fname)

        # Determine and set game name
        current_game = os.path.basename(os.path.splitext(fname)[0])
        self.caption = Machine._CAPTION.format(current_game)

        # Determine file size
        fsize = os.path.getsize(fname)
        max_size = self._MEMORY - self._PC0
        if fsize > max_size:
            print("Game ROM must not exceed {} bytes.".format(max_size))
            return

        else:
            print("Game size = {} bytes.".format(fsize))

        # Read from file
        with open(fname, 'rb') as game_file:
            byte_data = map(ord, game_file.read())
            mem_range = slice(self._PC0, self._PC0 + len(byte_data))
            self.memory[:len(FONTSET)] = FONTSET
            self.memory[mem_range] = byte_data

    def emulate_cycle(self):
        lh_op = self.memory[self.pc]
        rh_op = self.memory[self.pc + 1]
        self.pc += 2

        opcode = Opcode.from_pair(lh_op, rh_op)  # Fetch
        instruction = InstructionSet(opcode)     # Decode
        instruction.execute(self)                # Execute

    def decrement_timers(self):
        # Update timers
        self.delay_timer -= np.uint16(self.delay_timer > 0)
        self.sound_timer -= np.uint16(self.sound_timer > 0)
        # if(self.sound_timer == 1):
        #     print('\a')
