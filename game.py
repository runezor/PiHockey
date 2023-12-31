import math
import pygame
import random
from backgrounds import StarBackground, FireBackground, FabricBackground, StartBackground, EndBackground, Star2Background
from enum import Enum

BAT_MAX_V = 640

BALL_MAX_V_EASY = 90
BALL_MAX_V_MEDIUM = 90
BALL_MAX_V_HARD = 105

FRICTION_EASY = 30
FRICTION_MEDIUM = 35
FRICTION_HARD = 35

BAT_R_EASY = 4.0
BALL_R_EASY = 4.0

BAT_R_MEDIUM = 3.5
BALL_R_MEDIUM = 3.5

BAT_R_HARD = 3.5
BALL_R_HARD = 3.5


TIMEOUT_T = 0.2

ROOM_W = 32
ROOM_H = 64

END_SCORE = 10

pygame.init()
pygame.mixer.init()
crash_sound = pygame.mixer.Sound("sounds/clang.wav")
start_sound = pygame.mixer.Sound("sounds/prepare_to_fight.wav")
explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")

taunt_sounds = [pygame.mixer.Sound("sounds/accuracy.wav"),
                pygame.mixer.Sound("sounds/humiliation.wav"),
                pygame.mixer.Sound("sounds/impressive.wav"),
                pygame.mixer.Sound("sounds/perfect.wav"),
                pygame.mixer.Sound("sounds/sudden_death.wav")]

blue_lead_sounds = [pygame.mixer.Sound("sounds/blue_leads.wav")]

red_lead_sounds = [pygame.mixer.Sound("sounds/red_leads.wav")]

tied_sounds = [pygame.mixer.Sound("sounds/teams_are_tied.wav"),
                pygame.mixer.Sound("sounds/you_are_tied_for_the_lead.wav")]

def sign(x):
    return -1 if x<0 else 1

def switch_music(new_track):
    pygame.mixer.music.stop()
    pygame.mixer.music.load(new_track)
    pygame.mixer.music.play(-1)

class GameState(Enum):
    PLAYING = 1
    SCORE_PAUSE = 2
    GAME_OVER = 3
    GAME_START = 4

class GameExcitement(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Game:
    def __init__(self):
        self.state = GameState.GAME_START
        self.background = StartBackground(ROOM_W, ROOM_H)

        self.ball_r = BALL_R_MEDIUM
        self.bat_r = BAT_R_MEDIUM

        self.bat1_x = 0
        self.bat1_y = 0
        self.bat1_timeout = 0

        self.bat2_x = 0
        self.bat2_y = 59
        self.bat2_timeout = 0

        self.ball_x = 0
        self.ball_y = 0
        self.ball_v_x = 0
        self.ball_v_y = 0

        self.friction = 0

        self.player1_score = 0
        self.player2_score = 0

        self.excitement = None
        self.set_excitement(GameExcitement.LOW)

        self.background_pause_c = (0,0,0)

        self.particles = []


    def compute_new_ball_position(self, time_delta):
        return self.ball_x+self.ball_v_x*time_delta, self.ball_y+self.ball_v_y*time_delta

    def get_ball_footprint(self):
        return [(int(self.ball_x), int(self.ball_y)),(int(self.ball_x)+1, int(self.ball_y)),(int(self.ball_x), int(self.ball_y)+1),(int(self.ball_x)+1, int(self.ball_y)+1)]

    def get_bat1_footprint(self):
        return [(x+1, int(self.bat1_y)) for x in range(int(self.bat1_x), int(self.bat1_x+BAT_W-2))] + \
               [(x, int(self.bat1_y+1)) for x in range(int(self.bat1_x), int(self.bat1_x+BAT_W))] + \
               [(x, int(self.bat1_y+2)) for x in range(int(self.bat1_x), int(self.bat1_x+BAT_W))] + \
               [(x+1, int(self.bat1_y+3)) for x in range(int(self.bat1_x), int(self.bat1_x+BAT_W-2))]

    def get_bat2_footprint(self):
        return [(x, int(self.bat2_y)) for x in range(int(self.bat2_x), int(self.bat2_x+BAT_W))]

    def does_point_collide_bat(self,x,y):
        return (x-self.bat1_x)**2+(y-self.bat1_y)**2<self.bat_r**2 or (x-self.bat2_x)**2+(y-self.bat2_y)**2<self.bat_r**2

    def does_point_collide_ball(self,x,y):
        return (x-self.ball_x)**2+(y-self.ball_y)**2<self.bat_r**2

    def does_ball_collide_bat1(self):
        dist = (self.ball_x - self.bat1_x)**2+(self.ball_y - self.bat1_y)**2
        return dist<(self.ball_r+self.bat_r)**2

    def does_ball_collide_bat2(self):
        dist = (self.ball_x - self.bat2_x)**2+(self.ball_y - self.bat2_y)**2
        return dist<(self.ball_r+self.bat_r)**2

    def is_ball_outside_room(self):
        points = self.get_ball_footprint()
        for x,y in points:
            if x<0 or x>ROOM_W:
                return True
        return False

    def get_t_of_ball_collision(self, p_x, p_y, v_x, v_y, b_x, b_y, u_x, u_y, r):
        # Calculate collision t
        ts = []

        inner = ((-2 * b_x * u_x + 2 * b_x * v_x - 2 * b_y * u_y + 2 * b_y * v_y + 2 * p_x * u_x - 2 * p_x * v_x + 2 * p_y * u_y - 2 * p_y * v_y)**2 - 4 * (-u_x**2 + 2 * u_x * v_x - u_y**2 + 2 * u_y * v_y - v_x**2 - v_y**2) * (-b_x**2 + 2 * b_x * p_x - b_y**2 + 2 * b_y * p_y - p_x**2 - p_y**2 + r**2))
        if inner>0:
            t = (math.sqrt(inner) + 2 * b_x * u_x - 2 * b_x * v_x + 2 * b_y * u_y - 2 * b_y * v_y - 2 * p_x * u_x + 2 * p_x * v_x - 2 * p_y * u_y + 2 * p_y * v_y)/(2 * (-u_x**2 + 2 * u_x * v_x - u_y**2 + 2 * u_y * v_y - v_x**2 - v_y**2))
            if t>0:
                ts += [t]

        inner = (-2 * b_x * u_x + 2 * b_x * v_x - 2 * b_y * u_y + 2 * b_y * v_y + 2 * p_x * u_x - 2 * p_x * v_x + 2 * p_y * u_y - 2 * p_y * v_y)**2 - 4 * (-u_x**2 + 2 * u_x * v_x - u_y**2 + 2 * u_y * v_y - v_x**2 - v_y**2) * (-b_x**2 + 2 * b_x * p_x - b_y**2 + 2 * b_y * p_y - p_x**2 - p_y**2 + r**2)
        if inner>0:
            t = (-math.sqrt(inner) + 2 * b_x * u_x - 2 * b_x * v_x + 2 * b_y * u_y - 2 * b_y * v_y - 2 * p_x * u_x + 2 * p_x * v_x - 2 * p_y * u_y + 2 * p_y * v_y)/(2 * (-u_x**2 + 2 * u_x * v_x - u_y**2 + 2 * u_y * v_y - v_x**2 - v_y**2))
            if t>0:
                ts += [t]

        if ts:
            return min(ts)
        else:
            return None

    def transition_playing(self, kickoff = True):
        if kickoff:
            self.ball_x = 0
            self.ball_y = 32
            self.ball_v_x = 20 * random.choice([-1, 1])
            self.ball_v_y = -30 * random.choice([-1, 1])

        self.state = GameState.PLAYING

    def transition_score_pause(self, score_pause_t):
        self.bat1_timeout = 0
        self.bat2_timeout = 0

        # If transitioning from start phase, select difficulty
        if self.state == GameState.GAME_START:
            pygame.mixer.Sound.play(start_sound)
            # Play start sound
            if self.bat1_x<ROOM_W/3:
                self.ball_r = BALL_R_EASY
                self.bat_r = BAT_R_EASY
                self.ball_max_v = BALL_MAX_V_EASY
                self.friction = FRICTION_EASY
                self.background_pause_c = (0, 200, 0)
            elif self.bat1_x<ROOM_W/3*2:
                self.ball_r = BALL_R_MEDIUM
                self.bat_r = BAT_R_MEDIUM
                self.ball_max_v = BALL_MAX_V_MEDIUM
                self.friction = FRICTION_MEDIUM
                self.background_pause_c = (200, 120, 0)
            else:
                self.ball_r = BALL_R_HARD
                self.bat_r = BAT_R_HARD
                self.ball_max_v = BALL_MAX_V_HARD
                self.friction = FRICTION_HARD
                self.background_pause_c = (200, 0, 0)
        else:
            self.background_pause_c = (0, 0, 0)

        self.score_pause_t = score_pause_t

        self.state = GameState.SCORE_PAUSE

        max_score = max(self.player1_score, self.player2_score)
        if max_score<3:
            self.set_excitement(GameExcitement.LOW)
            self.background = StarBackground(ROOM_W, ROOM_H)
        elif max_score<7:
            self.set_excitement(GameExcitement.MEDIUM)
            self.background = FireBackground(ROOM_W, ROOM_H)
        else:
            self.set_excitement(GameExcitement.HIGH)
            self.background = Star2Background(ROOM_W, ROOM_H)

    def play_taunt_sound(self):
        if self.player1_score == self.player2_score + 1:
            pygame.mixer.Sound.play(random.choice(blue_lead_sounds))
        elif self.player2_score == self.player1_score + 1:
            pygame.mixer.Sound.play(random.choice(red_lead_sounds))
        elif self.player1_score == self.player2_score:
            pygame.mixer.Sound.play(random.choice(tied_sounds))
        else:
            pygame.mixer.Sound.play(random.choice(taunt_sounds))

    def step_playing(self, bat1_x, bat1_y, bat2_x, bat2_y, time_delta):
        self.background.update(time_delta)

        self.bat1_timeout = max(0,self.bat1_timeout-time_delta)
        self.bat2_timeout = max(0,self.bat2_timeout-time_delta)

        bat1_vel_x = (bat1_x - self.bat1_x) / time_delta
        bat1_vel_y = (bat1_y - self.bat1_y) / time_delta

        bat2_vel_x = (bat2_x - self.bat2_x) / time_delta
        bat2_vel_y = (bat2_y - self.bat2_y) / time_delta

        bat1_speed = math.sqrt(bat1_vel_x**2+bat1_vel_y**2)
        bat2_speed = math.sqrt(bat2_vel_x**2+bat2_vel_y**2)
        if bat1_speed>BAT_MAX_V:
            bat1_vel_x = bat1_vel_x * (BAT_MAX_V/bat1_speed)
            bat1_vel_y = bat1_vel_y * (BAT_MAX_V/bat1_speed)

        if bat2_speed>BAT_MAX_V:
            bat2_vel_x = bat2_vel_x * (BAT_MAX_V/bat2_speed)
            bat2_vel_y = bat2_vel_y * (BAT_MAX_V/bat2_speed)

        vl = math.sqrt(self.ball_v_x**2 + self.ball_v_y**2)
        ball_new_v = min(vl-self.friction*time_delta, self.ball_max_v)

        if ball_new_v>0:
            self.ball_v_x = self.ball_v_x * ball_new_v/vl
            self.ball_v_y = self.ball_v_y * ball_new_v/vl
        else:
            self.ball_v_x = 0
            self.ball_v_y = 0

        t_bat1 = self.get_t_of_ball_collision(self.ball_x, self.ball_y, self.ball_v_x, self.ball_v_y, self.bat1_x, self.bat1_y, bat1_vel_x, bat1_vel_y, self.bat_r + self.ball_r)
        t_bat2 = self.get_t_of_ball_collision(self.ball_x, self.ball_y, self.ball_v_x, self.ball_v_y, self.bat2_x, self.bat2_y, bat2_vel_x, bat2_vel_y, self.bat_r + self.ball_r)

        if t_bat1 and t_bat1<time_delta and self.bat1_timeout == 0:
            pygame.mixer.Sound.play(crash_sound)
            # First set ball collision to colliding point
            t = t_bat1

            self.ball_x += self.ball_v_x * t
            self.ball_y += self.ball_v_y * t

            bat1_col_x = self.bat1_x + bat1_vel_x*t
            bat1_col_y = self.bat1_y + bat1_vel_y*t

            n_x = self.ball_x - bat1_col_x
            n_y = self.ball_y - bat1_col_y

            n_l = math.sqrt(n_x**2+n_y**2)
            n_x /= n_l
            n_y /= n_l

            reframe_ball_v_x = self.ball_v_x - bat1_vel_x
            reframe_ball_v_y = self.ball_v_y - bat1_vel_y

            dot_product = 2 * (n_x * reframe_ball_v_x + n_y * reframe_ball_v_y)

            reframe_ball_v_x -= dot_product * n_x
            reframe_ball_v_y -= dot_product * n_y

            self.ball_v_x = reframe_ball_v_x + bat1_vel_x
            self.ball_v_y = reframe_ball_v_y + bat1_vel_y

            # Now move ball the remaining part
            self.ball_x += self.ball_v_x * (time_delta-t)
            self.ball_y += self.ball_v_y * (time_delta-t)
        elif t_bat2 and t_bat2<time_delta and self.bat2_timeout == 0:
            pygame.mixer.Sound.play(crash_sound)
            # First set ball collision to colliding point
            t = t_bat2

            self.ball_x += self.ball_v_x * t
            self.ball_y += self.ball_v_y * t

            bat2_col_x = self.bat2_x + bat2_vel_x*t
            bat2_col_y = self.bat2_y + bat2_vel_y*t

            n_x = self.ball_x - bat2_col_x
            n_y = self.ball_y - bat2_col_y

            n_l = math.sqrt(n_x**2+n_y**2)
            n_x /= n_l
            n_y /= n_l

            reframe_ball_v_x = self.ball_v_x - bat2_vel_x
            reframe_ball_v_y = self.ball_v_y - bat2_vel_y

            dot_product = 2 * (n_x * reframe_ball_v_x + n_y * reframe_ball_v_y)

            reframe_ball_v_x -= dot_product * n_x
            reframe_ball_v_y -= dot_product * n_y

            self.ball_v_x = reframe_ball_v_x + bat2_vel_x
            self.ball_v_y = reframe_ball_v_y + bat2_vel_y

            # Now move ball the remaining part
            self.ball_x += self.ball_v_x * (time_delta-t)
            self.ball_y += self.ball_v_y * (time_delta-t)
        else:
            self.ball_x, self.ball_y = self.compute_new_ball_position(time_delta)

        self.bat1_x += bat1_vel_x * time_delta
        self.bat1_y += bat1_vel_y * time_delta

        self.bat2_x += bat2_vel_x * time_delta
        self.bat2_y += bat2_vel_y * time_delta

        # Push from bats
        if self.does_ball_collide_bat1() and self.bat1_timeout == 0:
            v_x = self.ball_x -self.bat1_x
            v_y = self.ball_y -self.bat1_y
            if v_x == 0 and v_y == 0:
                v_y = 1
            else:
                l = math.sqrt(v_x**2+v_y**2)
                v_x = v_x / l
                v_y = v_y / l
            self.ball_x += v_x * (self.bat_r+self.ball_r+0.01)
            self.ball_y += v_y * (self.bat_r+self.ball_r+0.01)
            self.ball_v_x = v_x / time_delta
            self.ball_v_y = v_y / time_delta

        if self.does_ball_collide_bat2() and self.bat2_timeout == 0:
            print("PUSH LOGIC")
            v_x = self.ball_x -self.bat2_x
            v_y = self.ball_y -self.bat2_y
            if v_x == 0 and v_y == 0:
                v_y = 1
            else:
                l = math.sqrt(v_x**2+v_y**2)
                v_x = v_x / l
                v_y = v_y / l
            self.ball_x += v_x * (self.bat_r+self.ball_r+0.01)
            self.ball_y += v_y * (self.bat_r+self.ball_r+0.01)
            self.ball_v_x = v_x / time_delta
            self.ball_v_y = v_y / time_delta

        # Wall correct
        # Move ball and check for wall
        if self.ball_x<self.ball_r:
            self.ball_x = self.ball_r
            self.ball_v_x = -self.ball_v_x
        if self.ball_x>ROOM_W-self.ball_r:
            self.ball_x = ROOM_W-self.ball_r
            self.ball_v_x = -self.ball_v_x

        # If still colliding, set timeout
        if self.does_ball_collide_bat1():
            self.bat1_timeout = TIMEOUT_T
        if self.does_ball_collide_bat2():
            self.bat2_timeout = TIMEOUT_T

        if self.ball_y<-self.ball_r:
            self.player2_score += 1
            self.ball_x = 16
            self.ball_y = 16
            self.ball_v_x = 0
            self.ball_v_y = 0

            self.play_taunt_sound()

            if self.player2_score<END_SCORE:
                self.transition_score_pause(1)
            else:
                self.ball_x = 1000
                self.transition_game_over(False)

        if self.ball_y>ROOM_H+self.ball_r:
            self.player1_score += 1
            self.ball_x = 16
            self.ball_y = 64-16
            self.ball_v_x = 0
            self.ball_v_y = 0

            self.play_taunt_sound()

            if self.player1_score<END_SCORE:
                self.transition_score_pause(1)
            else:
                self.ball_x = 1000
                self.transition_game_over(True)

    def transition_game_over(self, player1_won):
        self.bat1_timeout = 0
        self.bat2_timeout = 0

        self.state = GameState.GAME_OVER
        self.set_excitement(GameExcitement.LOW)
        pygame.mixer.Sound.play(explosion_sound)
        if player1_won:
            self.background = EndBackground(ROOM_W, ROOM_H, self.bat2_x, self.bat2_y)
        else:
            self.background = EndBackground(ROOM_W, ROOM_H, self.bat1_x, self.bat1_y)

    def transition_game_start(self):
        self.bat1_timeout = 0
        self.bat2_timeout = 0

        self.player1_score = 0
        self.player2_score = 0
        self.state = GameState.GAME_START
        self.background = StartBackground(ROOM_W, ROOM_H)

    def step_update_bats(self, bat1_x, bat1_y, bat2_x, bat2_y, time_delta):
        bat1_vel_x = (bat1_x - self.bat1_x) / time_delta
        bat1_vel_y = (bat1_y - self.bat1_y) / time_delta

        bat2_vel_x = (bat2_x - self.bat2_x) / time_delta
        bat2_vel_y = (bat2_y - self.bat2_y) / time_delta

        self.bat1_x += bat1_vel_x * time_delta
        self.bat1_y += bat1_vel_y * time_delta

        self.bat2_x += bat2_vel_x * time_delta
        self.bat2_y += bat2_vel_y * time_delta


    def step_score_pause(self, bat1_x, bat1_y, bat2_x, bat2_y, time_delta):
        self.step_update_bats(bat1_x, bat1_y, bat2_x, bat2_y, time_delta)

        self.score_pause_t -= time_delta
        if self.score_pause_t<=0:
            self.transition_playing(kickoff=(self.player1_score==0 and self.player2_score==0))

    def step_game_start(self, bat1_x, bat1_y, bat2_x, bat2_y, time_delta):
        self.background.update(time_delta)
        self.step_update_bats(bat1_x, bat1_y, bat2_x, bat2_y, time_delta)
        self.ball_x = -100
        self.ball_y = -100

    def step_game_over(self, bat1_x, bat1_y, bat2_x, bat2_y, time_delta):
        self.background.update(time_delta)
        self.step_update_bats(bat1_x, bat1_y, bat2_x, bat2_y, time_delta)

    def set_excitement(self, excitement):
        if self.excitement != excitement:
            self.excitement = excitement
            if excitement == GameExcitement.LOW:
                switch_music("PiHockeyLowExcitement.mp3")
            elif excitement == GameExcitement.MEDIUM:
                switch_music("PiHockeyMediumExcitement.mp3")
            elif excitement == GameExcitement.HIGH:
                switch_music("PiHockeyHighExcitement.mp3")

    def restart(self):
        self.player1_score = 0
        self.player2_score = 0
        self.state = GameState.GAME_START # Probably want to do with a start transition (also not done in init)
        self.set_excitement(GameExcitement.LOW) # Probably wanna do in start transition instead

    def step(self,bat1_x, bat1_y, bat2_x, bat2_y, time_delta):
        if self.state == GameState.PLAYING:
            self.step_playing(bat1_x, bat1_y, bat2_x, bat2_y, time_delta)
        elif self.state == GameState.SCORE_PAUSE:
            self.step_score_pause(bat1_x, bat1_y, bat2_x, bat2_y, time_delta)
        elif self.state == GameState.GAME_START:
            self.step_game_start(bat1_x, bat1_y, bat2_x, bat2_y, time_delta)
        elif self.state == GameState.GAME_OVER:
            self.step_game_over(bat1_x, bat1_y, bat2_x, bat2_y, time_delta)



