#!/usr/bin/python3

import pygame
import py_retro
import sys
import os

libpath, rompath = "/usr/lib/libretro/gambatte_libretro.so", "pkm.gb"

def main():
    es = py_retro.core.EmulatedSystem(libpath)
    es.load_game_normal(path=rompath)

    screen = py_retro.pygame_video.pygame_display_set_mode(es, False)

    py_retro.pygame_video.set_video_refresh_surface(es, screen)
    py_retro.portaudio_audio.set_audio_sample_internal(es)
    py_retro.pygame_input.set_input_poll_joystick(es)

    # run each frame until closed.
    running = True
    fps = es.get_av_info()['fps'] or 60
    clock = pygame.time.Clock()

    while running:
        es.run()
        #pygame.display.flip()
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


if __name__ == "__main__":
    try:
        main()
    except:
        print("EXCEPTION")
        os.system("killall python")
        os.system("create_ap --stop ap0")
