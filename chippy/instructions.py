import random


class Opcode(object):
    """CHIP8 / SCHIP opcode datatype.

    Opcodes are 16-bit ints and are generally of the form:
    'GXYN', 'GXNN' or 'GNNN'; where

    G : 4-bit opcode group id,
    X, Y : 4-bit register ids,
    NN : 8-bit constant,
    NNN: 12-bit address.

    Parameters
    ----------
    code : int or str
        A two-byte (16-bit) opcode.
    """
    _SYNUM = 4  # Total number of symbols in opcode
    _SYLENGTH = 4  # Length of opcode symbol in bits

    def __init__(self, code):
        base = 16

        if isinstance(code, str):
            code = int(code, base)

        assert (code < base**self._SYNUM) and (code >= 0), \
            "OPCODE must range between '0000'--'FFFF'."

        self.code = code

    @classmethod
    def from_pair(cls, left_int, right_int):
        return cls((left_int << cls._SYLENGTH * 2) | right_int)

    def _extract_symbol(self, shift, length):
        mask = 2 ** (length * Opcode._SYLENGTH) - 1
        shift = Opcode._SYLENGTH * shift
        return (self.code >> shift) & mask

    def as_str(self):
        shifts = range(Opcode._SYNUM)
        hex_syms = ['{:1x}'.format(self._extract_symbol(s, 1)) for s in shifts]
        return ''.join(hex_syms).upper()[::-1]

    def generate_masks(self):
        # Mask opcodes for decoding
        str_code = '_' + self.as_str()
        return set([
            str_code,
            str_code[:2] + 'M' + str_code[3:],
            str_code[:2] + 'MM' + str_code[4],
            str_code[:2] + 'MMM',
        ])

    @property
    def G(self):
        return self._extract_symbol(shift=3, length=1)

    @property
    def X(self):
        return self._extract_symbol(shift=2, length=1)

    @property
    def Y(self):
        return self._extract_symbol(shift=1, length=1)

    @property
    def N(self):
        return self._extract_symbol(shift=0, length=1)

    @property
    def NN(self):
        return self._extract_symbol(shift=0, length=2)

    @property
    def NNN(self):
        return self._extract_symbol(shift=0, length=3)


class InstructionSet(object):
    def __init__(self, opcode):
        self.opcode = opcode

    def execute(self, machine):
        opcode_masks = self.opcode.generate_masks()
        ins_id = opcode_masks.intersection(set(dir(self)))
        fun = self.__getattribute__(ins_id.pop()) if ins_id else self._NOP
        return fun(machine)

    # ===== INSTRUCTIONS ==================================================== #
    def _00E0(self, machine):  # 00E0
        machine.gfx.clear()

    def _00EE(self, machine):  # 00EE
        machine.pc = machine.stack.pop()

    def _1MMM(self, machine):  # 1NNN
        machine.pc = self.opcode.NNN

    def _2MMM(self, machine):  # 2NNN
        machine.stack.append(machine.pc)
        machine.pc = self.opcode.NNN

    def _3MMM(self, machine):  # 3XNN
        if machine.V[self.opcode.X] == self.opcode.NN:
            machine.pc += 2

    def _4MMM(self, machine):  # 4XNN
        if machine.V[self.opcode.X] != self.opcode.NN:
            machine.pc += 2

    def _5MMM(self, machine):  # 5XY0
        if machine.V[self.opcode.X] == machine.V[self.opcode.Y]:
            machine.pc += 2

    def _6MMM(self, machine):  # 6XNN
        machine.V[self.opcode.X] = self.opcode.NN

    def _7MMM(self, machine):  # 7XNN
        machine.V[self.opcode.X] += self.opcode.NN

    def _8MM0(self, machine):  # 8XY0
        machine.V[self.opcode.X] = machine.V[self.opcode.Y]

    def _8MM1(self, machine):  # 8XY1
        machine.V[self.opcode.X] |= machine.V[self.opcode.Y]
        machine.V[0xF] = 0

    def _8MM2(self, machine):  # 8XY2
        machine.V[self.opcode.X] &= machine.V[self.opcode.Y]
        machine.V[0xF] = 0

    def _8MM3(self, machine):  # 8XY3
        machine.V[self.opcode.X] ^= machine.V[self.opcode.Y]
        machine.V[0xF] = 0

    def _8MM4(self, machine):  # 8XY4
        vf_check = machine.V[self.opcode.Y] > (0xFF - machine.V[self.opcode.X])
        if vf_check:
            machine.V[0xF] = 1
            overflow = (0xFF - machine.V[self.opcode.Y]) + 1
            machine.V[self.opcode.X] -= overflow
        else:
            machine.V[0xF] = 0
            machine.V[self.opcode.X] += machine.V[self.opcode.Y]

    def _8MM5(self, machine):  # 8XY5
        vf_check = machine.V[self.opcode.X] < machine.V[self.opcode.Y]
        if vf_check:
            machine.V[0xF] = 0
            overflow = (0xFF - machine.V[self.opcode.Y]) + 1
            machine.V[self.opcode.X] += overflow
        else:
            machine.V[0xF] = 1
            machine.V[self.opcode.X] -= machine.V[self.opcode.Y]

    def _8MM6(self, machine):  # 8XY6
        machine.V[0xF] = machine.V[self.opcode.X] & 0x1
        machine.V[self.opcode.X] >>= 1

    def _8MM7(self, machine):  # 8XY7
        vf_check = machine.V[self.opcode.Y] < machine.V[self.opcode.X]
        if vf_check:
            machine.V[0xF] = 0
            overflow = (0xFF - machine.V[self.opcode.X]) + 1
            machine.V[self.opcode.X] = machine.V[self.opcode.Y] + overflow
        else:
            machine.V[0xF] = 1
            machine.V[self.opcode.X] = (
                machine.V[self.opcode.Y] - machine.V[self.opcode.X]
            )

    def _8MME(self, machine):  # 8XYE
        machine.V[0xF] = machine.V[self.opcode.X] >> 7
        machine.V[self.opcode.X] <<= 1

    def _9MMM(self, machine):  # 9XY0
        if machine.V[self.opcode.X] != machine.V[self.opcode.Y]:
            machine.pc += 2

    def _AMMM(self, machine):  # ANNN
        machine.I = self.opcode.NNN

    def _BMMM(self, machine):  # BNNN
        machine.pc = machine.V[0x0] + self.opcode.NNN

    def _CMMM(self, machine):  # CXNN
        machine.V[self.opcode.X] = random.randint(0, 255) & self.opcode.NN

    def _DMMM(self, machine):  # DXYN
        img = machine.memory[machine.I:machine.I + self.opcode.N]
        machine.gfx.draw_sprite(
            img, machine.V[self.opcode.X], machine.V[self.opcode.Y]
        )
        machine.V[0xF] = 1 if machine.gfx.collision_flag else 0

    def _EM9E(self, machine):  # EX9E
        if machine.keyboard.state[machine.V[self.opcode.X]] == 1:
            machine.pc += 2

    def _EMA1(self, machine):  # EXA1
        if machine.keyboard.state[machine.V[self.opcode.X]] == 0:
            machine.pc += 2

    def _FM07(self, machine):  # FX07
        machine.V[self.opcode.X] = machine.delay_timer

    def _FM0A(self, machine):  # FX0A
        machine.V[self.opcode.X] = machine.keyboard.get_active_key()

    def _FM15(self, machine):  # FX15
        machine.delay_timer = machine.V[self.opcode.X]

    def _FM18(self, machine):  # FX18
        machine.sound_timer = machine.V[self.opcode.X]

    def _FM1E(self, machine):  # FX1E
        vf_check = machine.I > (0xFFF - machine.V[self.opcode.X])
        if vf_check:
            machine.V[0xF] = 1
            overflow = (0xFFF - machine.V[self.opcode.X]) + 1
            machine.I -= overflow
        else:
            machine.V[0xF] = 0
            machine.I += machine.V[self.opcode.X]

    def _FM29(self, machine):  # FX29
        machine.I = machine.V[self.opcode.X] * 0x5
        # Note: sprites are stored as 4x5 hex font characters (0-F)

    def _FM33(self, machine):  # FX33
        machine.memory[machine.I] = machine.V[self.opcode.X] // 100
        machine.memory[machine.I + 1] = (machine.V[self.opcode.X] // 10) % 10
        machine.memory[machine.I + 2] = (machine.V[self.opcode.X] % 100) % 10

    def _FM55(self, machine):  # FX55
        reg_range = slice(0, self.opcode.X + 1)
        mem_range = slice(machine.I, machine.I + self.opcode.X + 1)
        machine.memory[mem_range] = machine.V[reg_range]

    def _FM65(self, machine):  # FX65
        reg_range = slice(0, self.opcode.X + 1)
        mem_range = slice(machine.I, machine.I + self.opcode.X + 1)
        machine.V[reg_range] = machine.memory[mem_range]

    def _NOP(self, machine):  # Unknown Code
        print("Unknown code: {}".format(self.opcode.as_str()))
        print("Calling PC: {}".format(machine.pc - 2))
