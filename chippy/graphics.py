# Import modules
import numpy as np
import cv2 as cv


# Screen constants
WIN_WIDTH = int(640*1.25)
WIN_HEIGHT = int(320*1.25)

CHIP8_WIDTH = 64
CHIP8_HEIGHT = 32

SCHIP_WIDTH = 128
SCHIP_HEIGHT = 64


class GFX(object):
    WIN_SIZE = (WIN_WIDTH, WIN_HEIGHT)
    MAX_HEIGHT = 16
    DEPTH = 11  # Screen depth (for smoothing)
    VOTES = 5  # Screen depth (for pixel vote)
    ON_COLOUR = 0 + 50
    OFF_COLOUR = 255 - 50

    def __init__(self):
        # C8 screen parameters
        self.width = CHIP8_WIDTH
        self.height = CHIP8_HEIGHT
        self.collision_flag = False

        # Chip8 screen
        self.screen = np.zeros([self.height, self.width, GFX.DEPTH], np.uint8)
        self.weights = GFX.compute_screen_weights()

    def draw_sprite(self, img, x, y):
        height = min(len(img), GFX.MAX_HEIGHT)
        bytes_per_row = (height // GFX.MAX_HEIGHT) + 1
        dx = min(self.width - x, 8 * bytes_per_row)  # Compensate for xboundary
        dy = min(self.height - y, height)            # Compensate for yboundary

        if dx <= 0 or dy <= 0:
            return

        img_array = img.reshape([height, bytes_per_row])
        pxls = np.unpackbits(img_array, axis=1)[:dy, :dx]

        self.collision_flag = (self.screen[y:y+dy, x:x+dx, 0] & pxls).any()
        self.screen[y:y+dy, x:x+dx, 0] ^= pxls

        # Update draw buffer
        self.screen[:, :, 1:] = self.screen[:, :, :-1]

    def clear(self):
        self.screen[:, :, 0] = np.zeros([self.height, self.width], np.uint8)

    def draw(self):
        # Build screen by combining smoothing strategies - exponential and vote
        # smooth_screen = (self.screen * self.weights).sum(axis=2)
        vote_screen = np.max(self.screen[:, :, :GFX.VOTES], axis=2)
        # screen = (1 - vote_screen) * smooth_screen + vote_screen
        screen = vote_screen

        # Upscale chip8 screen to window size
        screen = cv.resize(screen, GFX.WIN_SIZE, interpolation=cv.INTER_AREA)

        # Map values to grayscale and filter sharp edges
        screen = screen * (GFX.ON_COLOUR - GFX.OFF_COLOUR) + GFX.OFF_COLOUR
        screen = cv.medianBlur(np.round(screen).astype(np.uint8), 3)

        # Update draw buffer and return new screen
        self.screen[:, :, 1:] = self.screen[:, :, :-1]
        return screen

    def set_resolution(self, resolution):
        if resolution == 'low':
            self.width = CHIP8_WIDTH
            self.height = CHIP8_HEIGHT

        elif resolution == 'high':
            self.width = SCHIP_WIDTH
            self.height = SCHIP_HEIGHT

        else:
            raise ValueError('Unknown resolution. Use either high or low.')

        # Rebuild screen
        self.screen = np.zeros([self.height, self.width, GFX.DEPTH], np.uint8)

    def scroll(self, direction, shift):
        if direction == 'down':
            self.screen[shift:, :, 0] = self.screen[:-shift, :, 0]
            self.screen[:shift, :, 0] = 0

        elif direction == 'right':
            self.screen[:, shift:, 0] = self.screen[:, :-shift, 0]
            self.screen[:, :shift, 0] = 0

        elif direction == 'left':
            self.screen[:, :-shift, 0] = self.screen[:, shift:, 0]
            self.screen[:, -shift:, 0] = 0

        else:
            raise ValueError('Unknown scroll direction')

    @staticmethod
    def compute_screen_weights():
        weights = np.arange(0, GFX.DEPTH, dtype=float)
        weights = np.exp(-weights / GFX.DEPTH**2)
        weights /= weights.sum()
        return weights.reshape(1, 1, GFX.DEPTH)
