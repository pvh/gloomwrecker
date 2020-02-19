#!/usr/bin/env python

from itertools import chain
from rpi_ws281x import Color, PixelStrip, ws

LED_COUNT = 298         # Number of LED pixels.
LED_PIN = 12           # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10           # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 16    # Set to 0 for darkest and 255 for brightest
LED_INVERT = False     # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0
LED_STRIP = ws.SK6812_STRIP_GRBW

strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
strip.begin()

import ghh
import asyncio
import math

TCP_IP = '192.168.1.15'
TCP_PORT = 58888

# (the fifth player sits at the end of the table)
SEATING_POSITIONS=[8, 50, 155, 200, 105]

CHARACTER_CLASS_ENUM = [
    "Escort",
    "Objective", 
    "Brute",
    "Cragheart",
    "Mindtheif",
    "Scoundrel",
    "Spellweaver",
    "Tinkerer",
    "Diviner",
    "TwoMinis",
    "Lightning",
    "AngryFace",
    "Triangles",
    "Moon",
    "ChuluFace",
    "TrippleArrow",
    "Saw",
    "MusicNote",
    "Circles",
    "Sun",
    "value20",
]

CLASS_COLORS = {
    "Scoundrel": (165, 209, 102, 0),
    "Brute": (78, 127, 193, 0),
    "Cragheart": (137, 149, 56, 0),
    "Mindthief": (100, 124, 157, 0),
    "Spellweaver": (181, 120, 179, 0),
    "Tinkerer": (197, 181, 141, 0),
    "TwoMinis": (173, 116, 92, 0),
    "Lightning": (209, 78, 78, 0),
    "AngryFace": (56, 195, 241, 0),
    "Triangles": (158, 158, 158, 0),
    "Moon": (158, 159, 205, 0),
    "ChuluFace": (116, 199, 187, 0),
    "TrippleArrow": (217, 137, 38, 0),
    "Saw": (223, 221, 202, 0),
    "MusicNote": (223, 126, 122, 0),
    "Circles": (235, 111, 163, 0),
    "Sun": (243, 195, 57, 0),
    "value20": (255, 1, 1, 0),
}

STATUS_COLORS = {
"Stun": (46, 64, 103),
"Immobilize": (153, 40, 45),
"Disarm": (98, 116, 122),
"Wound": (230, 80, 29),
"Muddle": (105, 78, 59),
"Poison": (116, 124, 94),
"Strengthen": (89, 150, 214),
"Invisible": (25, 23, 21),
"Regenerate": (200, 59, 150),
}

GAMMA = list(map(lambda x: round(((x/255.0)**2.5)*255), range(0, 256)))

# players get about 30px to represent them
# *********|*********|*********|
# --- HHHHHHHHHHHHHHHH SSSSS ---

PLAYER_WIDTH = 30
COLOR_BAR_WIDTH = 4
INITIATIVE_WIDTH = 3
START_OF_HEALTH = COLOR_BAR_WIDTH + 1
HEALTH_BAR_WIDTH = 14
END_OF_HEALTH = START_OF_HEALTH + HEALTH_BAR_WIDTH

def render_player(player):
    character_class = player.character_class
    class_name = CHARACTER_CLASS_ENUM[character_class]
    color = CLASS_COLORS.get(class_name, (255, 255, 255))

    hp = player.hp
    hp_max = player.hp_max


    initiative = player.initiative
    waiting_color = (0, 0, 128, 0)
    ready_color = (0, 255, 0, 255)
    initiative_color = waiting_color if (initiative == 0) else ready_color


    for i in range(0, COLOR_BAR_WIDTH):
        yield color

    for i in range(0, INITIATIVE_WIDTH):
        yield initiative_color

    # mind the gap
    yield (0, 0, 0)


    # health bar rendering
    healthy_color = (0, 255, 0, 0)
    ouchie_color = (255, 0, 0, 0)
    lights = math.ceil(float(hp) / float(hp_max) * HEALTH_BAR_WIDTH)
    for i in range(HEALTH_BAR_WIDTH):
        if i < lights:
            yield healthy_color
        else:
            yield ouchie_color 

    yield (0, 0, 0, 0)

    for i in range(0, INITIATIVE_WIDTH):
        yield initiative_color

    for i in range(0, COLOR_BAR_WIDTH):
        yield color

def set_pixel_color(current_led, color):
    gamma_corrected = map(lambda x: GAMMA[x], color)
    strip.setPixelColor(current_led, Color(*gamma_corrected))
    
def paint_starting_at(current_led):
    next_led = current_led

    def set_next_led(color):
        nonlocal next_led
        curr = next_led
        next_led += 1
        set_pixel_color(next_led, color)
    return set_next_led

ELEMENT_START_POINT = 250
def render_elements(game_state):
    set_next_led = paint_starting_at(ELEMENT_START_POINT)

    banner_w = [ 32, 64, 128, 255, 0 ]
    for item in list(banner_w):
        set_next_led((0, 0, 0, banner_w))

    for color in chain(
        render_element("dark", game_state.dark),
        render_element("light", game_state.light),
        render_element("earth", game_state.earth),
        render_element("air", game_state.air),
        render_element("ice", game_state.ice),
        render_element("fire", game_state.fire)
    ):
        set_next_led(color)

    for item in list(reversed(banner_w)):
        set_next_led((0, 0, 0, banner_w))


ELEMENT_COLORS = {
    "fire": (226, 66, 30),
    "ice": (85, 200, 239), 
    "air": (152, 176, 181), 
    "earth": (124, 168, 42), 
    "light": (236, 166, 15), 
    "dark": (31, 50, 131), 
}

def render_element(element, intensity):
    color = ELEMENT_COLORS[element]

    if (intensity == 0):
        yield (0, 0, 0)
        yield (0, 0, 0)
        yield (0, 0, 0)
    elif (intensity == 2): # waning
        yield (0, 0, 0)
        yield color
        yield (0, 0, 0)
    elif (intensity == 1): # full
        yield color
        yield color
        yield color
    yield (0, 0, 0, 0)

async def on_game_state(message_number, game_state):
    render_elements(game_state)
        
    for actor in game_state.actors:
        
        player = actor.getPlayer()
        
        if (player):
            global table_state

            character_class = player.character_class

            if not (character_class in table_state["seating_positions"]):
                # table_state["seating_positions"][character_class] = table_state["next_seat"]
                # table_state["next_seat"] = table_state["next_seat"] + 1
                if character_class == ghh.CharacterClass.Triangles:
                    table_state["seating_positions"][character_class] = 2
                elif character_class == ghh.CharacterClass.Sun:
                    table_state["seating_positions"][character_class] = 3
                elif character_class == ghh.CharacterClass.AngryFace:
                    table_state["seating_positions"][character_class] = 0
                else:
                    table_state["seating_positions"][character_class] = 1


            player_render = render_player(player)

            player_start_led = SEATING_POSITIONS[table_state["seating_positions"][character_class]]
            set_next_led = paint_starting_at(player_start_led)

            for color in player_render:
                set_next_led(color)

    strip.show()

table_state = {
    "next_seat": 0,
    "seating_positions": {},
}

async def main():
    client = ghh.Client(TCP_IP, TCP_PORT)
    client.on_game_state = on_game_state
    await client.connect()
    print("Connected")

asyncio.get_event_loop().create_task(main())
asyncio.get_event_loop().run_forever()
