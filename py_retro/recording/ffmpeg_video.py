"""
WAV-file output for libretro Audio.
"""

import subprocess
from threading import Thread

import pygame

from ..api.retro_constants import PIXEL_FORMAT_0RGB1555, PIXEL_FORMAT_XRGB8888, PIXEL_FORMAT_RGB565, rcl
from ..interactive.pygame_video import PygameVideoMixin, pixel_format_depths, pixel_format_masks

pixel_format_ffmpeg_names = {
    PIXEL_FORMAT_0RGB1555: 'rgb555le',
    PIXEL_FORMAT_RGB565: 'rgb565le',
    PIXEL_FORMAT_XRGB8888: 'bgr0',
}


class FfmpegVideoMixin(PygameVideoMixin):
    def __init__(self, libpath, **kw):
        super().__init__(libpath, **kw)
        pygame.display.init()
        self.__framebuffer = None
        self.__bits_per_pixel = None
        self.__bit_masks = None
        self.__fps = None
        self.__pipe = None
        self.__pix_fmt = None

    def video_record(self, output_file, extra_params=()):
        w, h = self.__framebuffer.get_size()
        fps = self.__fps
        cmd = (f'ffmpeg -y -f rawvideo -c:v rawvideo -s {w}x{h} -pix_fmt {self.__pix_fmt}'
               f' -r {fps} -i - -an -pix_fmt yuv420p').split()
        cmd.extend(extra_params)
        cmd.append(output_file)
        self.__pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.STDOUT)
        return self.__pipe

    def video_stream(self, extra_params=()):
        w, h = self.__framebuffer.get_size()
        fps = self.__fps
        fps = 30  # force 30
        cmd = (f'ffmpeg -f rawvideo -c:v rawvideo -s {w}x{h} -pix_fmt {self.__pix_fmt}'
               f' -r {fps} -i - -an -pix_fmt yuv420p').split()
        cmd.extend(extra_params)
        cmd.extend('-')
        print("streaming with command " + str(cmd))

        #ftl_cmd = (f'/home/vivlim/git/ftl-sdk/build/ftl_app').split()
        ftl_cmd = (f'/home/vivlim/git/ftl-sdk/build/ftl_app -s <STREAM KEY> -S -i ingest-sea.mixer.com').split()

        self.__pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                       stderr=subprocess.DEVNULL)

        self.__pipe_mixer = subprocess.Popen(ftl_cmd, stdin=self.__pipe.stdout, stdout=subprocess.PIPE)

        #self._watch_subprocess_stdout(self.__pipe.stdout, "ffmpeg")
        self._watch_subprocess_stdout(self.__pipe_mixer.stdout, "mixer")
        return self.__pipe

    def get_video_resolution(self) -> tuple:
        return self.__framebuffer.get_size()

    def _watch_subprocess_stdout(self, pipe, label):
        stdout_viewer = Thread(target=self._subprocess_stdout_thread, args=(pipe, label,), daemon=True)
        stdout_viewer.start()

    @staticmethod
    def _subprocess_stdout_thread(pipe, label):
        for line in iter(pipe.readline, b''):
            print("[{}]: {}".format(label, str(line).rstrip()))

    def _set_pixel_format(self, fmt: int):
        try:
            self.__bits_per_pixel = pixel_format_depths[fmt]
            self.__bit_masks = pixel_format_masks[fmt]
            self.__pix_fmt = pixel_format_ffmpeg_names[fmt]
        except KeyError:
            print(f'Unsupported pixel format {rcl("PIXEL", fmt)}')
            return False
        return super()._set_pixel_format(fmt)

    def _set_geometry(self, base_size: tuple, max_size: tuple, aspect_ratio: float) -> bool:
        if not self.__pipe:
            self.__framebuffer = pygame.Surface(
                base_size,
                depth=self.__bits_per_pixel,
                masks=self.__bit_masks
            )
            return super()._set_geometry(base_size, max_size, aspect_ratio)
        else:
            print(f'NOT resizing to {base_size} in the middle of encoding!')
            return False

    def _set_timing(self, fps: float, sample_rate: float) -> bool:
        if not self.__pipe:
            self.__fps = fps
            return super()._set_timing(fps, sample_rate)
        else:
            print(f'NOT changing to {fps} FPS in the middle of encoding!')
            return False

    def run(self):
        super().run()
        if self.surface and self.__framebuffer and self.__pipe:
            if self.__pipe.stdin.closed:
                self.__pipe = None
                print("Pipe is closed :(")
                return
            pygame.transform.scale(self.surface, self.__framebuffer.get_size(), self.__framebuffer)
            self.__pipe.stdin.write(self.__framebuffer.get_view('2').raw)
