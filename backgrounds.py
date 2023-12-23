import math
import random

class StarBackground:
    class Star:
        def __init__(self, x, y, dir, spd):
            self.x = x
            self.y = y
            self.spd = spd
            self.dir = dir / 180 * math.pi

        def update(self, time_delta):
            self.x += math.cos(self.dir) * self.spd * time_delta
            self.y += math.sin(self.dir) * self.spd * time_delta

        def get_coords(self):
            return int(self.x), int(self.y)

    def  __init__(self, width, height, dispersion = 4, spd = 20):
        self.w = width
        self.h = height
        self.t = 0
        self.next_t = 0
        self.dispersion = dispersion
        self.spd = spd

        self.pixels = [[(0,0,0) for x in range(self.w)] for y in range(self.h)]
        self.stars = []

    def update(self, time_delta):
        self.t += time_delta
        for star in self.stars:
            star.update(time_delta)
        self.stars = [star for star in self.stars if star.x>0 and star.x<self.w and star.y>0 and star.y<self.h]

        x_center = self.w // 2
        y_center = self.h // 2

        if self.next_t<self.t:
            for i in range(0, 360, 45):
                self.stars += [StarBackground.Star(x_center, y_center, i, self.spd)]

            self.next_t = self.t + 1 / self.dispersion

    def render(self):
        self.pixels = [[(0,0,0) for x in range(self.w)] for y in range(self.h)]
        for star in self.stars:
            x, y = star.get_coords()
            self.pixels[y][x] = (200, 200, 200)
        return self.pixels

class FireBackground:
    class Star:
        def __init__(self, x, y, dir, spd):
            self.x = x
            self.y = y
            self.spd = spd
            self.dir = dir / 180 * math.pi
            self.t = 0.0

        def update(self, time_delta):
            self.x += math.cos(self.dir) * self.spd * time_delta
            self.y += math.sin(self.dir) * self.spd * time_delta
            self.t += time_delta

        def get_coords(self):
            return int(self.x), int(self.y)


        def wave_colour(self, offset, damp):
            return int((math.sin(self.t/damp+offset)+1)/2.0*255)

        def get_colour(self):
            r_offset = 10
            g_offset = 20
            b_offset = 30

            r_damp = 0.1
            g_damp = 0.4
            b_damp = 0.8

            return (self.wave_colour(r_offset, r_damp), self.wave_colour(g_offset, g_damp), self.wave_colour(b_offset, b_damp))

    def  __init__(self, width, height, dispersion = 300, spd = 30, spin_time = 0.4):
        self.w = width
        self.h = height
        self.t = 0
        self.next_t = 0
        self.dispersion = dispersion
        self.spd = spd

        self.pixels = [[(0,0,0) for x in range(self.w)] for y in range(self.h)]
        self.stars = []
        self.spin_time = spin_time

    def update(self, time_delta):
        self.t += time_delta
        for star in self.stars:
            star.update(time_delta)
        self.stars = [star for star in self.stars if star.x>0 and star.x<self.w and star.y>0 and star.y<self.h]

        x_center = self.w // 2
        y_center = self.h // 2

        if self.next_t<self.t:
            self.stars += [FireBackground.Star(x_center, y_center, (self.t * 360 / self.spin_time) % 360, self.spd)]

            self.next_t = self.t + 1 / self.dispersion

    def render(self):
        self.pixels = [[(0,0,0) for x in range(self.w)] for y in range(self.h)]
        for star in self.stars:
            x, y = star.get_coords()
            self.pixels[y][x] = star.get_colour()
        return self.pixels



class FabricBackground:
    def  __init__(self, game, width, height, dispersion = 300, spd = 30, fade_in_t = 2, interleave_fac = 4):
        self.w = width
        self.h = height
        self.t = 0
        self.next_t = 0
        self.dispersion = dispersion
        self.spd = spd

        self.interleave_fac = interleave_fac


        self.pixels = [[(0,0,0) for x in range(self.w)] for y in range(self.h)]
        self.t_off = random.randint(0,1000)
        self.fade_in_t = fade_in_t
        self.game = game


    def wave_colour(self, offset, damp, t):
        fade_in = 1-max((self.fade_in_t-t)/self.fade_in_t,0)
        return int((math.sin((t+self.t_off+offset)/damp)+1)/2.0*160*fade_in)

    def get_point_colour(self, x, y, t):
        player1_x = self.game.bat1_x
        player1_y = self.game.bat1_y
        player2_x = self.game.bat2_x
        player2_y = self.game.bat2_y
        ball_x = self.game.ball_x
        ball_y = self.game.ball_y


        offset_damp = 1000
        offset_damp_player = 2000
        r_offset = (x-y)/offset_damp + ((player1_x-x)**2+(player1_y-y)**2) / offset_damp_player
        g_offset = (x+y)/offset_damp + ((player2_x-x)**2+(player2_y-y)**2) / offset_damp_player
        b_offset = (x**2-y**2)/offset_damp + ((ball_x-x)**2+(ball_y-y)**2) / offset_damp_player

        r_damp = 0.1*2
        g_damp = 0.08*2
        b_damp = 0.16*2

        return (self.wave_colour(r_offset, r_damp, t),self.wave_colour(g_offset, g_damp, t),self.wave_colour(b_offset, b_damp, t))


    def update(self, time_delta):
        self.t += time_delta

    def render(self):
        for j in range(0,self.w*self.h//self.interleave_fac):
            x = random.randint(0, self.w-1)
            y = random.randint(0, self.h-1)
            self.pixels[y][x] = self.get_point_colour(x,y,self.t)

        return self.pixels


class StartBackground:
    def  __init__(self, width, height, rot_spd = 1.5, line_sep = 15, line_spd = 40):
        self.w = width
        self.h = height
        self.t = 0
        self.rot_spd = rot_spd
        self.line_sep = line_sep
        self.line_spd = line_spd

    def update(self, time_delta):
        self.t += time_delta

    def draw_line(self, start_x, start_y, dir):
        x_slope = math.cos(dir)
        y_slope = math.sin(dir)


        t1 = (self.w-start_x) / x_slope if x_slope!=0.0 else -1
        t2 = (self.h-start_y) / y_slope if y_slope!=0.0 else -1
        t3 = (-start_x) / x_slope if x_slope!=0.0 else -1
        t4 = (-start_y) / y_slope if y_slope!=0.0 else -1

        ts = [i for i in [t1, t2, t3, t4] if i>0]
        if ts:
            r = math.sqrt(self.w**2+self.h**2)
            t = min(max(ts),r)

            for t in range(0, int(t)):
                x = int(start_x+x_slope*t)
                y = int(start_y+y_slope*t)
                if x>0 and x<self.w and y>0 and y<self.h:
                    self.pixels[y][x] = (255, 255, 255)

    def draw_lines(self, dir, step_size, offset = 0):
        x_slope = math.cos(dir) * step_size
        y_slope = math.sin(dir) * step_size

        r = math.sqrt(self.w**2+self.h**2)
        self.draw_line(int(self.w/2), int(self.h/2), dir + math.pi / 2)
        self.draw_line(int(self.w/2), int(self.h/2), dir - math.pi / 2)
        for t in range(0, int(r)):
            x = int(self.w/2+x_slope*t + x_slope * offset)
            y = int(self.h/2+y_slope*t + y_slope * offset)
            self.draw_line(x, y, dir + math.pi / 2)
            self.draw_line(x, y, dir - math.pi / 2)



    def render(self):
        self.pixels = [[(0,0,0) for x in range(self.w)] for y in range(self.h)]

        self.draw_lines(self.t*self.rot_spd, self.line_sep, (self.t*self.line_spd/self.line_sep)%1)
        self.draw_lines(self.t*self.rot_spd+math.pi, self.line_sep, (self.t*self.line_spd/self.line_sep)%1)

        return self.pixels


class EndBackground:
    class CircleExplosion:
        def __init__(self, x, y, r, c):
            self.x = x
            self.y = y
            self.r = r
            self.c = c

        def grow(self, s):
            self.r += s

    def  __init__(self, width, height, circle_spawn_x, circle_spawn_y, circle_spawn_freq = 0.3, circle_growth_spd = 30, circle_max_r = 24):
        self.w = width
        self.h = height
        self.t = 0
        self.new_t = 0
        self.circles = []

        self.circle_spawn_freq = circle_spawn_freq
        self.circle_growth_spd = circle_growth_spd
        self.circle_max_r = circle_max_r

        self.circle_spawn_x = circle_spawn_x
        self.circle_spawn_y = circle_spawn_y

    def update(self, time_delta):
        self.t += time_delta

        for c in self.circles:
            c.grow(self.circle_growth_spd * time_delta)

        if self.new_t<self.t:
            self.circles = [EndBackground.CircleExplosion(self.circle_spawn_x, self.circle_spawn_y, 0, (random.randint(0,255),random.randint(0,255),random.randint(0,255)))] + self.circles
            self.new_t = self.t + self.circle_spawn_freq

    def get_point_colour(self, x, y):
        for circ in self.circles:
            if (x-circ.x)**2+(y-circ.y)**2 < circ.r**2:
                return circ.c

        dist = (x-16)**2+(y)**2
        # Red gradient from top to bottom (depending on who won)
        return (0,0,0)

    def render(self):
        self.circles = [c for c in self.circles if c.r<self.circle_max_r]
        pixels = [[self.get_point_colour(x,y) for x in range(self.w)] for y in range(self.h)]
        return pixels
