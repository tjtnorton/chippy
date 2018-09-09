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
        pygame.K_p: 16,        # Extra Feature: Pause Emulator
        pygame.K_TAB: 17,      # Extra Feature: Reset Emulator
        pygame.K_ESCAPE: 18    # Extra Feature: Turn Off Emulator
    }

    def __init__(self):
        self.state = np.zeros(len(self.key_map), dtype=bool)

    def update_key_press(self, event):
        if event.type == pygame.KEYDOWN and event.key is pygame.K_p:
            self.set_pause()

        elif event.type == pygame.KEYDOWN and event.key in self.key_map:
            self.state[self.key_map[event.key]] = True

    def update_key_release(self, event):
        if event.type == pygame.KEYUP and event.key is pygame.K_p:
            return

        elif event.type == pygame.KEYUP and event.key in self.key_map:
            self.state[self.key_map[event.key]] = False

    def get_active_key(self):
        return self.state[:16].argmax()  # Only care about the hex keys.

    def reset(self):
        self.state = np.zeros(len(self.key_map), dtype=bool)

    def set_exit(self):
        self.state[self.key_map[pygame.K_ESCAPE]] = True

    def set_pause(self):
        pause_idx = self.key_map[pygame.K_p]
        self.state[pause_idx] = ~self.state[pause_idx]

    def is_exit(self):
        return self.state[self.key_map[pygame.K_ESCAPE]]

    def is_reset(self):
        return self.state[self.key_map[pygame.K_TAB]]

    def is_paused(self):
        return self.state[self.key_map[pygame.K_p]]
