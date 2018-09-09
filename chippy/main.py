import pygame
from . import core


SECOND = 1000         # Milliseconds in second
FPS = 60              # Frames per second
OPPF = 18             # Opcodes executed per frame


def main(fpath):
    # Initialization
    machine = core.Machine()
    machine.load_game(fpath)

    pygame.init()
    pygame.display.set_caption(machine.caption)
    screen = pygame.display.set_mode(machine.gfx.WIN_SIZE)

    # Start gameloop
    running = True
    while running:
        # Emulate chip8 cpu cycle
        if machine.keyboard.is_exit():
            break

        for _ in range(OPPF):
            pygame.time.wait(int(SECOND/FPS/OPPF))  # Slow down execution
            machine.emulate_cycle()
        machine.decrement_timers()  # unindent for reasonable reaction time

        # Poll events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            machine.keyboard.update_key_press(event)
            machine.keyboard.update_key_release(event)

        # Update graphics (sdl)
        pixel_data = machine.gfx.sdl_screen()
        pygame.surfarray.blit_array(screen, pixel_data)
        pygame.display.flip()

    # Kill everything!
    pygame.quit()

# Launch from command line
if __name__ == '__main__':
    import sys
    main(sys.argv[1])
