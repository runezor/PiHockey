import pygame
import sys

# Window dimensions
WINDOW_WIDTH = 320
WINDOW_HEIGHT = 640

# Pixel array dimensions
PIXEL_WIDTH = 32
PIXEL_HEIGHT = 64

# Scaling factor to display pixels
SCALE = 10

class ScreenDriver:
    def __init__(self, renderer):
        self.renderer = renderer
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PiHockey")

        print("Renderer started")

    def draw_pixel(self, x, y, color):
        """ Draw a single pixel """
        pygame.draw.rect(self.screen, color, (x * SCALE, y * SCALE, SCALE, SCALE))

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        self.screen.fill((0,0,0))
        for y in range(PIXEL_HEIGHT):
            for x in range(PIXEL_WIDTH):
                self.draw_pixel(x, y, self.renderer.get_colour(x,y))
        pygame.display.flip()
