#!/usr/bin/env python

import ghh
import asyncio
import math

TCP_IP = '127.0.0.1'
TCP_PORT = 58888

# (the fifth player sits at the end of the table)
SEATING_POSITIONS=[8, 50, 170, 220, 110]

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
    "Scoundrel": (165, 209, 102),
    "Brute": (78, 127, 193),
    "Cragheart": (137, 149, 56),
    "Mindthief": (100, 124, 157),
    "Spellweaver": (181, 120, 179),
    "Tinkerer": (197, 181, 141),
    "TwoMinis": (173, 116, 92),
    "Lightning": (209, 78, 78),
    "AngryFace": (56, 195, 241),
    "Triangles": (158, 158, 158),
    "Moon": (158, 159, 205),
    "ChuluFace": (116, 199, 187),
    "TrippleArrow": (217, 137, 38),
    "Saw": (223, 221, 202),
    "MusicNote": (223, 126, 122),
    "Circles": (235, 111, 163),
    "Sun": (243, 195, 57),
    "value20": (255, 1, 1),
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

# players get about 30px to represent them
# *********|*********|*********|
# --- HHHHHHHHHHHHHHHH SSSSS ---

PLAYER_WIDTH = 30
COLOR_BAR_WIDTH = 4
START_OF_HEALTH = COLOR_BAR_WIDTH + 1
HEALTH_BAR_WIDTH = 17
END_OF_HEALTH = START_OF_HEALTH + HEALTH_BAR_WIDTH

def render_player(player):
    character_class = player.character_class
    class_name = CHARACTER_CLASS_ENUM[character_class]
    color = CLASS_COLORS.get(class_name, (255, 255, 255))

    hp = player.hp
    hp_max = player.hp_max


    for i in range(0, COLOR_BAR_WIDTH):
        yield color

    # mind the gap
    yield (0, 0, 0)

    # health bar rendering
    healthy_color = (255, 0, 0)
    ouchie_color = (1, 1, 1)
    lights = math.ceil(float(hp) / float(hp_max) * HEALTH_BAR_WIDTH)
    for i in range(HEALTH_BAR_WIDTH):
        if i < lights:
            yield healthy_color
        else:
            yield ouchie_color 

    yield (0, 0, 0)

    for i in range(0, COLOR_BAR_WIDTH):
        yield color

ELEMENT_START_POINT = 260
def render_elements(game_state):
    current_led = ELEMENT_START_POINT
    for color in render_element("fire", game_state.fire):
        print(current_led, color)
        current_led = current_led + 1

    for color in render_element("ice", game_state.ice):
        print(current_led, color)
        current_led = current_led + 1

    for color in render_element("air", game_state.air):
        print(current_led, color)
        current_led = current_led + 1

    for color in render_element("earth", game_state.earth):
        print(current_led, color)
        current_led = current_led + 1

    for color in render_element("light", game_state.light):
        print(current_led, color)
        current_led = current_led + 1

    for color in render_element("dark", game_state.dark):
        print(current_led, color)
        current_led = current_led + 1
    
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

async def on_game_state(message_number, game_state):
    render_elements(game_state)
        
    for actor in game_state.actors:
        
        player = actor.getPlayer()
        
        if (player):
            global table_state

            character_class = player.character_class
            
            if not (character_class in table_state["seating_positions"]):
                table_state["seating_positions"][character_class] = table_state["next_seat"]
                table_state["next_seat"] = table_state["next_seat"] + 1

            player_render = render_player(player)
            
            current_led = SEATING_POSITIONS[table_state["seating_positions"][character_class]]
            for color in player_render:
                print(current_led, color)
                current_led = current_led + 1

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
