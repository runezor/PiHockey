from game import GameState, ROOM_W, ROOM_H
import math
from numberBitmaps import Numbers

class Renderer:
    def __init__(self):
        self.pixels = [[(0,0,0) for x in range(ROOM_W)] for y in range(ROOM_H)]

    def set_pixel(self,x,y,color):
        self.pixels[y][x] = color

    def draw_number(self, x,y, number, reverse = False):
        for y_i, row in enumerate(number):
            for x_i, a in enumerate(row):
                if reverse:
                    self.draw_pixel_a(x+len(row)-1-x_i, y+len(number)-1-y_i, (255,255,255), a)
                else:
                    self.draw_pixel_a(x+x_i, y+y_i, (255,255,255), a)

    def draw_pixel_a(self,x,y,c,a):
        p = self.pixels[y][x]
        self.pixels[y][x] = (int(c[0]*a+p[0]*(1-a)),int(c[1]*a+p[1]*(1-a)), int(c[2]*a+p[2]*(1-a)))

    def get_colour(self, x,y):
        return self.pixels[y][x]

    def draw_sphere(self, x_c, y_c, r, color, dropoff_factor = 0.3):
        for x in range(math.floor(x_c-r), math.ceil(x_c+r)):
            for y in range(math.floor(y_c-r), math.ceil(y_c+r)):
                if 0<=x and x<ROOM_W and 0<=y and y<ROOM_H:
                    # distance from center of point to center of circle
                    p_xc = x+0.5
                    p_yc = y+0.5
                    f = max(0,(1-math.sqrt((x_c-p_xc)**2+(y_c-p_yc)**2)/r))**dropoff_factor
                    self.draw_pixel_a(x,y, color, f)


    def render(self, game):
        # Clear
        background = game.background.render()

        if game.state != GameState.SCORE_PAUSE:
            for y in range(ROOM_H):
                for x in range(ROOM_W):
                    self.set_pixel(x, y, background[y][x])
        else:
            for y in range(ROOM_H):
                for x in range(ROOM_W):
                    self.set_pixel(x, y, game.background_pause_c)

        if game.state != GameState.GAME_OVER or game.player1_score>game.player2_score:
            c = (0,0,255) if game.bat1_timeout == 0 else (255,255,0)
            self.draw_sphere(game.bat1_x,game.bat1_y,game.bat_r, c)

        if game.state != GameState.GAME_OVER or game.player2_score > game.player1_score:
            c = (255,0,0) if game.bat2_timeout == 0 else (255,255,0)
            self.draw_sphere(game.bat2_x,game.bat2_y,game.bat_r, c)

        self.draw_sphere(game.ball_x,game.ball_y,game.ball_r, (255,255,255))

        if game.state == GameState.SCORE_PAUSE:
            self.draw_number(2,2,Numbers.NumberBitmap[game.player2_score], True)
            self.draw_number(ROOM_W-11,2,Numbers.NumberBitmap[game.player1_score], True)

            self.draw_number(2,ROOM_H-2-16,Numbers.NumberBitmap[game.player2_score], False)
            self.draw_number(ROOM_W-11,ROOM_H-2-16,Numbers.NumberBitmap[game.player1_score], False)

