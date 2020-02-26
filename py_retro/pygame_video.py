"""
Pygame output for libretro Video.
"""
import pygame
import ctypes
import cv2, os, threading
import numpy as np

def set_video_refresh_cb(core, callback, r=False):
    """
    Sets the callback that will handle updated video frames.

    Unlike core.EmulatedSystem.set_video_refresh_cb, the callback passed to this
    function should accept only one parameter:

        "surf" is an instance of pygame.Surface containing the frame data.
    """
    global surf

    fmt = core.env_props.get('pixel_format')
    # default: 0rgb1555 (assumed if the env_cb isn't called to set one)
    bpp = 15
    bitmasks = (0b0111110000000000, 0b0000001111100000, 0b0000000000011111, 0)  # (0x7c00, 0x03e0, 0x001f, 0)
    if fmt == 'xrgb8888':
        bpp = 32  # 24?
        bitmasks = (0xff0000, 0x00ff00, 0x0000ff, 0)
    elif fmt == 'rgb565':
        bpp = 16
        bitmasks = (0b1111100000000000, 0b0000011111100000, 0b0000000000011111, 0)  # (0xf80000, 0x007e00, 0x00001f, 0)

    def wrapper(data, width, height, pitch):
        if data is None:
            return

        # i.e. results in a surface width of "pitch//((15+7)//8)" = "pitch//2" for 15-bit
        bytes_per_pixel = (bpp + 7) // 8
        convsurf = pygame.Surface((pitch // bytes_per_pixel, height), depth=bpp, masks=bitmasks)
        #img = np.empty((pitch*height,))#, dtype=np.uint8)
        #ctypes.memmove(img.ctypes.data, data, pitch*height)
        #print(data, bytes_per_pixel, width, height, pitch)
        surf = convsurf.subsurface((0, 0, width, height))
        ctypes.memmove(convsurf._pixels_address, data, pitch*height)
        
        #color_image = pygame.surfarray.array3d(surf)
        
        #color_image = cv2.transpose(color_image)
        #color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        #pygame.image.save(surf, "screenshot.jpg")
        #img = cv2.imread("screenshot.jpg")
        #cv2.imwrite("static/tmp.jpg", color_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
        #threading.Thread(target=cv2.imwrite, args=["static/tmp.jpg", color_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]], daemon=True).start()
        #threading.Thread(target=os.system, args=["mv static/tmp.jpg static/img.jpg"], daemon=True).start()
        
        #threading.Thread(target=write_buffer, args=[surf], daemon=True).start()
        write_buffer(surf)
        
        #os.system("mv static/tmp.jpg static/img.jpg")
        
        callback(surf)

    core.set_video_refresh_cb(wrapper)

def write_buffer(surf):
    color_image = pygame.surfarray.array3d(surf)
    
    color_image = cv2.transpose(color_image)
    color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
    
    threading.Thread(target=cv2.imwrite, args=["static/tmp.jpg", color_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100]], daemon=True).start()
    threading.Thread(target=os.system, args=["mv static/tmp.jpg static/img.jpg"], daemon=True).start()


def set_video_refresh_surface(core, targetsurf, scale=False):
    
    if not scale:
        def wrapper(surf):
            targetsurf.blit(surf, (0, 0))
    else:
        def wrapper(surf):
            pygame.transform.scale(surf, targetsurf.get_size(), targetsurf)
    
    set_video_refresh_cb(core, wrapper)


def pygame_display_set_mode(core, use_max=True):
    key = 'max_size' if use_max else 'base_size'
    return pygame.Surface((1,1))#pygame.display.set_mode(core.get_av_info()[key])

