from game import Game, ROOM_W, ROOM_H, BAT_W, BAT_H, GameState
from renderer import Renderer
from tkinterDriver import ScreenDriver
from mouseDriver import MouseDriver
import time
from threading import Thread


game = Game()
renderer = Renderer()
screenDriver = ScreenDriver(renderer)

time_delta = 1/60

y_span = 25
sensitivity_x = 0.00015
sensitivity_y = sensitivity_x * (ROOM_W/y_span)

def on_mouse_pressed():
    if game.state == GameState.GAME_START:
        game.transition_score_pause(3)
    if game.state == GameState.GAME_OVER:
        game.transition_game_start()

mouse1 = MouseDriver('/dev/input/mouse1',sensitivity_x,sensitivity_y,on_mouse_pressed, rev_x = True)
mouse2 = MouseDriver('/dev/input/mouse2',sensitivity_x,sensitivity_y,on_mouse_pressed, rev_y = True)

while True:
    start = time.time()
    cor1_x, cor1_y = mouse1.get()
    cor2_x, cor2_y = mouse2.get()
    game.step(cor1_x*(ROOM_W), cor1_y*y_span, cor2_x*(ROOM_W), ROOM_H-y_span+cor2_y*y_span, time_delta/2)

    cor1_x, cor1_y = mouse1.get()
    cor2_x, cor2_y = mouse2.get()
    game.step(cor1_x*(ROOM_W), cor1_y*y_span, cor2_x*(ROOM_W), ROOM_H-y_span+cor2_y*y_span, time_delta/2)

    game_t = time.time()

    renderer.render(game)
    renderer_t = time.time()


    screenDriver.render()
    screenDriver_t = time.time()
    end = time.time()

    extra_t = time_delta - (end-start)
    if extra_t >= 0:
        time.sleep(extra_t)
    else:
        print("Lag", "target FPS:", 1/time_delta, "Actual FPS:", 1/(end-start))
        print("game_t", 1/(game_t-start), "renderer_t", 1/(renderer_t-game_t), "screenDriver_t", 1/(screenDriver_t-renderer_t))
