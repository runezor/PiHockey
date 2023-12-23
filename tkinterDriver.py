import pygame
import sys

# Window dimensions
WINDOW_WIDTH = 160
WINDOW_HEIGHT = 320

# Pixel array dimensions
PIXEL_WIDTH = 32
PIXEL_HEIGHT = 64

# Scaling factor to display pixels
SCALE = int(WINDOW_WIDTH/PIXEL_WIDTH)

pygame.mouse.set_visible(False)

class ScreenDriver:
    def __init__(self, renderer):
        self.renderer = renderer
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags=pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("PiHockey")

        print("Renderer started")

    def draw_pixel(self, x, y, color):
        """ Draw a single pixel """
        pygame.draw.rect(self.screen, color, (x * SCALE, y * SCALE, SCALE, SCALE))

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        for y in range(PIXEL_HEIGHT):
            for x in range(PIXEL_WIDTH):
                self.draw_pixel(x, y, self.renderer.get_colour(x,y))
        pygame.display.flip()
