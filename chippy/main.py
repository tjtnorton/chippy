import numpy as np
import pygame
from . import core


SECOND = 1000         # Milliseconds in second
FPS = 60              # Frames per second
OPPF = 18             # Opcodes executed per frame


def _convert_to_sdl(screen):
    """Convert a 2D pixel array and to (grayscale) uint32 array."""
    screen = screen.astype(np.uint32)
    sdl_screen = screen + np.left_shift(screen, 8)
    return (screen + np.left_shift(sdl_screen, 8)).T


def main(fpath):
    # Initialization
    machine = core.Machine()
    machine.load_game(fpath)

    pygame.init()
    pygame.display.set_caption(machine.caption)
    screen = pygame.display.set_mode(machine.gfx.WIN_SIZE)

    # Start gameloop
    running = True
    paused = False
    while running:
        # Emulate chip8 cpu cycle
        if not paused:
            for _ in range(OPPF):
                pygame.time.wait(int(SECOND/FPS/OPPF))  # Slow down execution
                machine.emulate_cycle()
            machine.decrement_timers()  # unindent for reasonable reaction time

        # Poll events
        for event in pygame.event.get():
            if machine.keyboard.is_exit(event):
                running = False

            if machine.keyboard.is_reset(event):
                machine.reset()

            if machine.keyboard.is_paused(event):
                paused = ~paused

            machine.keyboard.update_key_press(event)
            machine.keyboard.update_key_release(event)

        # Update graphics (sdl)
        pixel_data = _convert_to_sdl(machine.gfx.draw())
        pygame.surfarray.blit_array(screen, pixel_data)
        pygame.display.flip()


# Launch from command line
if __name__ == '__main__':
    import sys
    main(sys.argv[1])
