import pygame
import numpy as np


class HexKeyboard(object):
    key_map = {
        pygame.K_1: 0x1,
        pygame.K_2: 0x2,
        pygame.K_3: 0x3,
        pygame.K_4: 0xc,
        pygame.K_q: 0x4,
        pygame.K_w: 0x5,
        pygame.K_e: 0x6,
        pygame.K_r: 0xd,
        pygame.K_a: 0x7,
        pygame.K_s: 0x8,
        pygame.K_d: 0x9,
        pygame.K_f: 0xe,
        pygame.K_z: 0xa,
        pygame.K_x: 0x0,
        pygame.K_c: 0xb,
        pygame.K_v: 0xf,
    }

    def __init__(self):
        self.state = np.zeros(len(self.key_map))

    def update_key_press(self, event):
        if event.type == pygame.KEYDOWN and event.key in self.key_map:
            self.state[self.key_map[event.key]] = 1

    def update_key_release(self, event):
        if event.type == pygame.KEYUP and event.key in self.key_map:
            self.state[self.key_map[event.key]] = 0

    def get_active_key(self):
        return self.state.argmax()

    def reset(self):
        self.state = np.zeros(len(self.key_map))

    @staticmethod
    def is_exit(event):
        close = event.type == pygame.QUIT
        esc = event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE
        return close or esc

    @staticmethod
    def is_reset(event):
        return event.type == pygame.KEYUP and event.key == pygame.K_TAB

    @staticmethod
    def is_paused(event):
        return event.type == pygame.KEYUP and event.key == pygame.K_p
