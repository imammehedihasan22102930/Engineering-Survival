import pygame
import os
import json
import math
import random

pygame.init()

# ============================================================
# SOUND SYSTEM
# ============================================================

try:
    pygame.mixer.init()
    SOUND_ENABLED = True
except pygame.error:
    SOUND_ENABLED = False


# ============================================================
# WINDOW
# ============================================================

WIDTH = 1100
HEIGHT = 650

# SCALED keeps the original 1100x650 coordinate system while
# allowing the game to fill the monitor.
try:
    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT),
        pygame.FULLSCREEN | pygame.SCALED
    )
except pygame.error:
    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT)
    )

pygame.display.set_caption(
    "Engineering Survival"
)

FPS = 60
clock = pygame.time.Clock()

fullscreen = True


# ============================================================
# COLORS
# ============================================================

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

RED = (220, 50, 50)
GREEN = (50, 220, 80)
BLUE = (60, 150, 255)
YELLOW = (240, 210, 50)
ORANGE = (255, 150, 40)
CYAN = (50, 220, 220)

DARK = (25, 30, 35)
GRAY = (100, 100, 100)

DARK_BLUE = (7, 13, 24)
PANEL_DARK = (12, 21, 34)
PANEL_LIGHT = (20, 35, 52)


# ============================================================
# FONTS
# ============================================================

FONT = pygame.font.SysFont(
    "arial",
    22
)

SMALL_FONT = pygame.font.SysFont(
    "arial",
    17
)

BIG_FONT = pygame.font.SysFont(
    "arial",
    34,
    bold=True
)

TITLE_FONT = pygame.font.SysFont(
    "arial",
    48,
    bold=True
)

HUGE_FONT = pygame.font.SysFont(
    "arial",
    62,
    bold=True
)


# ============================================================
# GAME STATES
# ============================================================

MENU = "MENU"
EXPLORE = "EXPLORE"
PUZZLE = "PUZZLE"
MESSAGE = "MESSAGE"
INVENTORY = "INVENTORY"
PAUSE = "PAUSE"
OBJECTIVES = "OBJECTIVES"
GAME_OVER = "GAME_OVER"
MISSION_COMPLETE = "MISSION_COMPLETE"
CHARACTER_SELECT = "CHARACTER_SELECT"

game_state = MENU

selected_character_index = 0
selected_character = "MEHEDI"

menu_selection = 0

mission_completed = False


# ============================================================
# GLOBAL ANIMATION
# ============================================================

animation_time = 0.0
player_animation_time = 0.0
# 1 = facing right, -1 = facing left.
player_facing = 1
player_stride = 0.0
campus_animation_time = 0.0


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

IMAGE_DIR = os.path.join(
    BASE_DIR,
    "assets",
    "images"
)

SOUND_DIR = os.path.join(
    BASE_DIR,
    "assets",
    "sounds"
)

SAVE_FILE = os.path.join(
    BASE_DIR,
    "savegame.json"
)


# ============================================================
# IMAGE LOADER
# ============================================================

def load_image(
    filename,
    size,
    remove_white=False
):

    path = os.path.join(
        IMAGE_DIR,
        filename
    )

    try:

        image = pygame.image.load(
            path
        ).convert_alpha()

        image = pygame.transform.smoothscale(
            image,
            size
        )

        if remove_white:

            image = image.copy()

            pixel_array = pygame.PixelArray(
                image
            )

            white_color = image.map_rgb(
                (255, 255, 255)
            )

            transparent_color = image.map_rgb(
                (0, 0, 0, 0)
            )

            pixel_array.replace(
                white_color,
                transparent_color
            )

            del pixel_array

        return image

    except Exception as e:

        print(
            "Image loading error:",
            filename,
            e
        )

        placeholder = pygame.Surface(
            size,
            pygame.SRCALPHA
        )

        placeholder.fill(
            (80, 80, 80, 255)
        )

        pygame.draw.rect(
            placeholder,
            RED,
            placeholder.get_rect(),
            3
        )

        return placeholder


# ============================================================
# SOUND LOADER
# ============================================================

def load_sound(
    filename,
    volume=1.0
):

    if not SOUND_ENABLED:
        return None

    path = os.path.join(
        SOUND_DIR,
        filename
    )

    try:

        sound = pygame.mixer.Sound(
            path
        )

        sound.set_volume(
            volume
        )

        return sound

    except Exception as e:

        print(
            "Sound loading error:",
            filename,
            e
        )

        return None


def play_sound(sound):

    if SOUND_ENABLED and sound is not None:

        try:
            sound.play()
        except pygame.error:
            pass


def stop_all_sounds():

    if SOUND_ENABLED:

        try:
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        except pygame.error:
            pass


def play_mission_complete_only():

    if not SOUND_ENABLED:
        return

    try:

        pygame.mixer.music.stop()
        pygame.mixer.stop()

        if mission_complete_sound is not None:
            mission_complete_sound.play()

    except pygame.error:
        pass


# ============================================================
# LOAD SOUNDS
# ============================================================

menu_sound = load_sound(
    "menu_select.wav",
    0.5
)

interact_sound = load_sound(
    "interact.wav",
    0.6
)

puzzle_open_sound = load_sound(
    "puzzle_open.wav",
    0.6
)

correct_sound = load_sound(
    "correct.wav",
    0.7
)

wrong_sound = load_sound(
    "wrong.wav",
    0.7
)

door_sound = load_sound(
    "door.wav",
    0.6
)

warning_sound = load_sound(
    "warning.wav",
    0.4
)

shutdown_sound = load_sound(
    "shutdown.wav",
    0.7
)

mission_complete_sound = load_sound(
    "mission_complete.wav",
    0.8
)


# ============================================================
# BACKGROUND MUSIC
# ============================================================

BACKGROUND_MUSIC_VOLUME = 0.45
background_music_loaded = False


def find_sound_file(filename):

    candidates = [
        os.path.join(SOUND_DIR, filename),
        os.path.join(BASE_DIR, filename),
        os.path.join(BASE_DIR, "assets", filename),
        os.path.join(BASE_DIR, "sounds", filename)
    ]

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    return None


def start_background_music():

    global background_music_loaded

    if not SOUND_ENABLED:
        return

    try:

        music_path = find_sound_file("background_music.mp3")

        if music_path is None:
            print("Background music not found: background_music.mp3")
            return

        if not background_music_loaded:
            pygame.mixer.music.load(music_path)
            background_music_loaded = True

        pygame.mixer.music.set_volume(
            BACKGROUND_MUSIC_VOLUME
        )
        pygame.mixer.music.play(
            loops=-1,
            start=0.0
        )

    except Exception as e:
        print("Background music error:", e)


def stop_background_music():

    if not SOUND_ENABLED:
        return

    try:
        pygame.mixer.music.stop()
    except pygame.error:
        pass


# ============================================================
# LOAD IMAGES
# ============================================================

laboratory_img = load_image(
    "laboratory.png",
    (WIDTH, HEIGHT),
    False
)

power_room_img = load_image(
    "power_room.png",
    (WIDTH, HEIGHT),
    False
)

# Dedicated control-room artwork.
control_room_img = load_image(
    "control_room.png",
    (WIDTH, HEIGHT),
    False
)

campus_img = load_image(
    "campus.png",
    (WIDTH, HEIGHT),
    False
)


# ============================================================
# CHARACTER IMAGES
# ============================================================

mehedi_portrait = load_image(
    "mehedi.png",
    (220, 280),
    True
)

toyasin_portrait = load_image(
    "toyasin.png",
    (220, 280),
    True
)

mehedi_player_img = load_image(
    "mehedi.png",
    (65, 82),
    True
)

toyasin_player_img = load_image(
    "toyasin.png",
    (65, 82),
    True
)


def load_walk_frames(filename, fallback_img, frame_count=4):
    """Load an optional horizontal walk-cycle sprite sheet."""
    path = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(path):
        return []
    try:
        sheet = pygame.image.load(path).convert_alpha()
        frame_w = sheet.get_width() // frame_count
        frame_h = sheet.get_height()
        if frame_w <= 0 or frame_h <= 0:
            return []
        frames = []
        for i in range(frame_count):
            frame = sheet.subsurface(
                pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            ).copy()
            frames.append(pygame.transform.smoothscale(frame, fallback_img.get_size()))
        return frames
    except pygame.error:
        return []


# Optional 4-frame walk cycles. The game works without these files.
mehedi_walk_frames = load_walk_frames("mehedi_walk.png", mehedi_player_img)
toyasin_walk_frames = load_walk_frames("toyasin_walk.png", toyasin_player_img)

player_img = mehedi_player_img


# ============================================================
# OTHER IMAGES
# ============================================================

robot_img = load_image(
    "robot.png",
    (100, 125),
    True
)

panel_img = load_image(
    "electrical_panel.png",
    (100, 125),
    True
)

battery_img = load_image(
    "battery.png",
    (85, 105),
    True
)

generator_img = load_image(
    "generator.png",
    (130, 105),
    False
)

breaker_img = load_image(
    "circuit_breaker.png",
    (130, 90),
    False
)

motor_img = load_image(
    "motor.png",
    (140, 100),
    False
)

drone_img = load_image(
    "security_drone.png",
    (55, 55),
    False
)

door_img = load_image(
    "door.png",
    (55, 160),
    False
)


# ============================================================
# PLAYER
# ============================================================

player = pygame.Rect(
    100,
    300,
    65,
    82
)

PLAYER_SPEED = 5


# ============================================================
# PLAYER STATUS
# ============================================================

MAX_HEALTH = 150
MAX_ENERGY = 100

health = MAX_HEALTH
energy = MAX_ENERGY


# ============================================================
# MISSION
# ============================================================

MISSION_TIME = 600

mission_time = MISSION_TIME

score = 0

current_area = "MAIN LAB"

keycard = False

mission_completed = False

mission_complete_sound_played = False


# ============================================================
# SYSTEM STATUS
# ============================================================

battery_inspected = False
battery_active = False

panel_repaired = False

generator_repaired = False
breaker_solved = False

motor_solved = False
robot_inspected = False

# Control-room mission states.
scada_diagnostics_done = False
grid_status_verified = False
master_shutdown_done = False


# ============================================================
# INVENTORY
# ============================================================

inventory = []


def add_item(item):

    if item not in inventory:
        inventory.append(item)


# ============================================================
# OBJECTIVES
# ============================================================

def create_objectives():

    return [

        ["Inspect the battery", False],
        ["Activate battery system", False],
        ["Repair electrical panel", False],
        ["Repair backup generator", False],
        ["Solve circuit breaker problem", False],
        ["Repair motor drive", False],
        ["Inspect laboratory robot", False],
        ["Obtain laboratory keycard", False],
        ["Run SCADA diagnostic scan", False],
        ["Verify grid operating status", False],
        ["Execute master laboratory shutdown", False],
        ["Escape the laboratory", False]

    ]


objectives = create_objectives()


def refresh_objectives():

    global objectives

    states = [
        battery_inspected,
        battery_active,
        panel_repaired,
        generator_repaired,
        breaker_solved,
        motor_solved,
        robot_inspected,
        keycard,
        scada_diagnostics_done,
        grid_status_verified,
        master_shutdown_done,
        mission_completed
    ]

    if len(objectives) != len(states):
        objectives = create_objectives()

    for index, state in enumerate(states):
        objectives[index][1] = bool(state)


# ============================================================
# OBJECT RECTANGLES
# ============================================================

battery_rect = pygame.Rect(
    525,
    400,
    85,
    105
)

panel_rect = pygame.Rect(
    800,
    225,
    100,
    125
)

robot_rect = pygame.Rect(
    230,
    175,
    100,
    125
)

generator_rect = pygame.Rect(
    680,
    385,
    130,
    105
)

breaker_rect = pygame.Rect(
    650,
    180,
    130,
    90
)

motor_rect = pygame.Rect(
    360,
    385,
    140,
    100
)


# ============================================================
# DOORS
# ============================================================

power_door = pygame.Rect(
    0,
    245,
    55,
    160
)

control_door = pygame.Rect(
    1045,
    245,
    55,
    160
)

exit_door = pygame.Rect(
    940,
    510,
    100,
    140
)

power_back_door = pygame.Rect(
    0,
    245,
    55,
    160
)

control_back_door = pygame.Rect(
    1045,
    245,
    55,
    160
)

# Interaction zones carefully aligned with the generated control-room artwork.
# SCADA task: the long operator console and monitor bank across the lower-left.
scada_console_rect = pygame.Rect(
    245,
    465,
    430,
    105
)

# Grid task: the large GRID STATUS / SCADA display cluster on the upper-right.
grid_monitor_rect = pygame.Rect(
    690,
    205,
    325,
    120
)

# Shutdown task: the small wall control panel immediately beside the main-lab door.
shutdown_panel_rect = pygame.Rect(
    785,
    305,
    58,
    78
)


# ============================================================
# HAZARDS
# ============================================================

hazards = [

    pygame.Rect(
        600,
        140,
        170,
        55
    ),

    pygame.Rect(
        580,
        300,
        190,
        60
    ),

    pygame.Rect(
        330,
        500,
        220,
        45
    )

]


# ============================================================
# SECURITY DRONE
# ============================================================

drone_rect = pygame.Rect(
    850,
    120,
    55,
    55
)

drone_direction = 1
drone_speed = 2
drone_chasing = False
drone_damage_cooldown = 0

DRONE_PATROL_LEFT = 700
DRONE_PATROL_RIGHT = 1000


# ============================================================
# TEMPERATURE
# ============================================================

machine_temperature = 25

temperature_sound_cooldown = 0

hazard_damage_cooldown = 0


# ============================================================
# PUZZLE VARIABLES
# ============================================================

current_puzzle = None

puzzle_answer = ""

puzzle_question = ""


# ============================================================
# MESSAGE SYSTEM
# ============================================================

message_text = ""

message_timer = 0

previous_state = EXPLORE


def show_message(
    text,
    duration=180,
    return_state=None
):

    global message_text
    global message_timer
    global previous_state
    global game_state

    message_text = text

    message_timer = duration

    previous_state = (
        return_state
        if return_state is not None
        else game_state
    )

    game_state = MESSAGE


# ============================================================
# CHARACTER DATA
# ============================================================

characters = [

    {
        "name": "MEHEDI",
        "role": "ELECTRICAL ENGINEER",
        "specialty":
            "Power Systems | Circuit Analysis | Troubleshooting",
        "description":
            "Technical specialist focused on electrical systems, power networks and laboratory equipment.",
        "power": 95,
        "repair": 90,
        "analysis": 98,
        "field": 82
    },

    {
        "name": "TOYASIN",
        "role": "ENGINEERING SPECIALIST",
        "specialty":
            "Machine Systems | Equipment Repair | Field Support",
        "description":
            "Versatile engineering specialist focused on equipment inspection, machine systems and practical repair.",
        "power": 86,
        "repair": 97,
        "analysis": 84,
        "field": 95
    }

]


def apply_selected_character():

    global selected_character
    global player_img

    selected_character = characters[
        selected_character_index
    ]["name"]

    if selected_character == "TOYASIN":

        player_img = toyasin_player_img

    else:

        player_img = mehedi_player_img


# ============================================================
# CAMPUS PEOPLE
# ============================================================

campus_people = []

campus_shirt_colors = [
    (45, 95, 170),
    (180, 70, 60),
    (50, 135, 85),
    (125, 75, 160),
    (190, 125, 45),
    (70, 115, 145),
    (150, 65, 100)
]

campus_skin_colors = [
    (190, 135, 95),
    (205, 155, 110),
    (170, 115, 80),
    (220, 170, 125)
]


def create_campus_people():

    global campus_people

    campus_people = []

    for _ in range(15):

        person = {

            "x": random.randint(
                40,
                WIDTH - 40
            ),

            "y": random.randint(
                180,
                530
            ),

            "speed": random.choice([
                0.35,
                0.45,
                0.55,
                0.7,
                0.8
            ]),

            "direction": random.choice([
                -1,
                1
            ]),

            "scale": random.uniform(
                0.72,
                1.05
            ),

            "shirt": random.choice(
                campus_shirt_colors
            ),

            "skin": random.choice(
                campus_skin_colors
            ),

            "phase": random.uniform(
                0,
                math.pi * 2
            ),

            "pause": random.uniform(
                0,
                5
            ),

            "walking": True

        }

        campus_people.append(
            person
        )


create_campus_people()


# ============================================================
# CAMPUS BIRDS
# ============================================================

campus_birds = []

for _ in range(5):

    campus_birds.append({

        "x": random.randint(
            0,
            WIDTH
        ),

        "y": random.randint(
            80,
            260
        ),

        "speed": random.uniform(
            0.35,
            0.8
        ),

        "phase": random.uniform(
            0,
            math.pi * 2
        )

    })


# ============================================================
# CAMPUS PARTICLES
# ============================================================

campus_particles = []

for _ in range(35):

    campus_particles.append({

        "x": random.randint(
            0,
            WIDTH
        ),

        "y": random.randint(
            100,
            HEIGHT
        ),

        "speed": random.uniform(
            0.15,
            0.45
        ),

        "phase": random.uniform(
            0,
            math.pi * 2
        )

    })


# ============================================================
# RESET CAMPUS PEOPLE
# ============================================================

def reset_campus_people():

    # The university campus contains no random people.
    global campus_people
    campus_people = []


# ============================================================
# RESET GAME
# ============================================================

def reset_game():

    global health
    global energy
    global mission_time
    global score
    global current_area
    global keycard
    global mission_completed
    global mission_complete_sound_played

    global battery_inspected
    global battery_active

    global panel_repaired

    global generator_repaired
    global breaker_solved

    global motor_solved
    global robot_inspected

    global scada_diagnostics_done
    global grid_status_verified
    global master_shutdown_done

    global inventory
    global objectives

    global machine_temperature

    global drone_rect
    global player_facing
    global player_stride

    global drone_direction
    global drone_chasing
    global drone_damage_cooldown

    global temperature_sound_cooldown
    global hazard_damage_cooldown

    player.x = 100
    player.y = 300
    player_facing = 1
    player_stride = 0.0

    health = MAX_HEALTH
    energy = MAX_ENERGY

    mission_time = MISSION_TIME

    score = 0

    current_area = "MAIN LAB"

    keycard = False

    mission_completed = False

    mission_complete_sound_played = False

    battery_inspected = False
    battery_active = False

    panel_repaired = False

    generator_repaired = False
    breaker_solved = False

    motor_solved = False
    robot_inspected = False

    scada_diagnostics_done = False
    grid_status_verified = False
    master_shutdown_done = False

    inventory = []

    objectives = create_objectives()
    refresh_objectives()

    machine_temperature = 25

    drone_rect.x = 850
    drone_rect.y = 120

    drone_direction = 1
    drone_chasing = False

    drone_damage_cooldown = 0

    temperature_sound_cooldown = 0

    hazard_damage_cooldown = 0

    reset_campus_people()

    apply_selected_character()


# ============================================================
# SAVE GAME
# ============================================================

def save_game():

    data = {

        "health": health,
        "energy": energy,

        "mission_time": mission_time,
        "score": score,

        "current_area": current_area,

        "selected_character":
            selected_character,

        "player_facing":
            player_facing,

        "mission_completed":
            mission_completed,

        "keycard":
            keycard,

        "battery_inspected":
            battery_inspected,

        "battery_active":
            battery_active,

        "panel_repaired":
            panel_repaired,

        "generator_repaired":
            generator_repaired,

        "breaker_solved":
            breaker_solved,

        "motor_solved":
            motor_solved,

        "robot_inspected":
            robot_inspected,

        "scada_diagnostics_done":
            scada_diagnostics_done,

        "grid_status_verified":
            grid_status_verified,

        "master_shutdown_done":
            master_shutdown_done,

        "inventory":
            inventory,

        "objectives":
            objectives,

        "machine_temperature":
            machine_temperature,

        "player_x":
            player.x,

        "player_y":
            player.y

    }

    try:

        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

        show_message(
            "GAME SAVED SUCCESSFULLY",
            150
        )

    except Exception as e:

        print(
            "Save error:",
            e
        )

        show_message(
            "SAVE FAILED",
            150
        )


# ============================================================
# LOAD GAME
# ============================================================

def load_game():

    global health
    global energy
    global mission_time
    global score

    global current_area
    global keycard
    global selected_character
    global player_img

    global mission_completed
    global mission_complete_sound_played

    global battery_inspected
    global battery_active

    global panel_repaired

    global generator_repaired
    global breaker_solved

    global motor_solved
    global robot_inspected

    global scada_diagnostics_done
    global grid_status_verified
    global master_shutdown_done

    global inventory
    global objectives

    global machine_temperature
    global game_state

    global selected_character_index
    global player_facing

    if not os.path.exists(SAVE_FILE):

        show_message(
            "NO SAVE FILE FOUND",
            150,
            MENU
        )

        return

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        health = data.get(
            "health",
            MAX_HEALTH
        )

        energy = data.get(
            "energy",
            MAX_ENERGY
        )

        mission_time = data.get(
            "mission_time",
            MISSION_TIME
        )

        score = data.get(
            "score",
            0
        )

        current_area = data.get(
            "current_area",
            "MAIN LAB"
        )

        selected_character = data.get(
            "selected_character",
            "MEHEDI"
        )

        selected_character_index = 0

        player_facing = data.get("player_facing", 1)
        if player_facing not in (-1, 1):
            player_facing = 1

        if selected_character == "TOYASIN":
            selected_character_index = 1

        apply_selected_character()

        mission_completed = data.get(
            "mission_completed",
            current_area == "CAMPUS"
        )

        mission_complete_sound_played = (
            current_area == "CAMPUS"
        )

        keycard = data.get(
            "keycard",
            False
        )

        battery_inspected = data.get(
            "battery_inspected",
            False
        )

        battery_active = data.get(
            "battery_active",
            False
        )

        panel_repaired = data.get(
            "panel_repaired",
            False
        )

        generator_repaired = data.get(
            "generator_repaired",
            False
        )

        breaker_solved = data.get(
            "breaker_solved",
            False
        )

        motor_solved = data.get(
            "motor_solved",
            False
        )

        robot_inspected = data.get(
            "robot_inspected",
            False
        )

        scada_diagnostics_done = data.get(
            "scada_diagnostics_done",
            False
        )

        grid_status_verified = data.get(
            "grid_status_verified",
            False
        )

        master_shutdown_done = data.get(
            "master_shutdown_done",
            False
        )

        inventory = data.get(
            "inventory",
            []
        )

        # Rebuild the visible mission status from the actual flags.
        # This fixes stale/backdated objective lists in old save files.
        objectives = create_objectives()
        refresh_objectives()

        machine_temperature = data.get(
            "machine_temperature",
            25
        )

        player.x = data.get(
            "player_x",
            100
        )

        player.y = data.get(
            "player_y",
            300
        )

        reset_campus_people()

        game_state = EXPLORE

        # Restore the correct audio state for the saved area.
        if current_area == "CAMPUS":
            play_mission_complete_only()
            mission_complete_sound_played = True
        else:
            start_background_music()

        show_message(
            "GAME LOADED",
            150,
            EXPLORE
        )

    except Exception as e:

        print(
            "Load error:",
            e
        )

        show_message(
            "LOAD FAILED",
            150,
            MENU
        )


# ============================================================
# UPDATE OBJECTIVE
# ============================================================

def complete_objective(index):

    if 0 <= index < len(objectives):

        objectives[index][1] = True


# ============================================================
# PUZZLE START
# ============================================================

def start_puzzle(puzzle_name):

    global current_puzzle
    global puzzle_answer
    global puzzle_question
    global game_state

    current_puzzle = puzzle_name

    puzzle_answer = ""

    if puzzle_name == "battery":

        puzzle_question = (
            "Battery: 12V × 20Ah = ? Wh"
        )

    elif puzzle_name == "panel":

        puzzle_question = (
            "Panel: 1000W ÷ 5A = ? V"
        )

    elif puzzle_name == "generator":

        puzzle_question = (
            "Generator: 1500W ÷ 300V = ? A"
        )

    elif puzzle_name == "breaker":

        puzzle_question = (
            "Breaker: 2200W ÷ 220V = ? A"
        )

    elif puzzle_name == "motor":

        puzzle_question = (
            "Motor: 50V ÷ 10Ω = ? A"
        )

    elif puzzle_name == "scada":

        puzzle_question = (
            "SCADA: 230V × 10A × 0.80 PF = ? W"
        )

    elif puzzle_name == "grid_status":

        puzzle_question = (
            "Grid check: 400V ÷ 20A = ? Ω"
        )

    play_sound(
        puzzle_open_sound
    )

    game_state = PUZZLE


# ============================================================
# SOLVE PUZZLE
# ============================================================

def solve_puzzle():

    global health
    global energy

    global battery_inspected
    global battery_active

    global panel_repaired

    global generator_repaired
    global breaker_solved

    global motor_solved

    global scada_diagnostics_done
    global grid_status_verified

    global score
    global current_puzzle
    global game_state

    try:

        answer = float(
            puzzle_answer.strip()
        )

    except ValueError:

        play_sound(
            wrong_sound
        )

        health -= 5
        energy -= 5

        health = max(
            0,
            health
        )

        energy = max(
            0,
            energy
        )

        show_message(
            "INVALID ANSWER! -5 HP",
            120,
            PUZZLE
        )

        return

    correct = False

    if current_puzzle == "battery":

        correct = math.isclose(
            answer,
            240,
            rel_tol=0.01
        )

    elif current_puzzle == "panel":

        correct = math.isclose(
            answer,
            200,
            rel_tol=0.01
        )

    elif current_puzzle == "generator":

        correct = math.isclose(
            answer,
            5,
            rel_tol=0.01
        )

    elif current_puzzle == "breaker":

        correct = math.isclose(
            answer,
            10,
            rel_tol=0.01
        )

    elif current_puzzle == "motor":

        correct = math.isclose(
            answer,
            5,
            rel_tol=0.01
        )

    elif current_puzzle == "scada":

        correct = math.isclose(
            answer,
            1840,
            rel_tol=0.01
        )

    elif current_puzzle == "grid_status":

        correct = math.isclose(
            answer,
            20,
            rel_tol=0.01
        )

    if correct:

        play_sound(
            correct_sound
        )

        score += 100

        if current_puzzle == "battery":

            battery_inspected = True

            complete_objective(0)

            game_state = EXPLORE

            show_message(
                "BATTERY INSPECTED! Now activate the battery system.",
                180,
                EXPLORE
            )

        elif current_puzzle == "panel":

            panel_repaired = True

            complete_objective(2)

            game_state = EXPLORE

            show_message(
                "ELECTRICAL PANEL REPAIRED!",
                180,
                EXPLORE
            )

        elif current_puzzle == "generator":

            generator_repaired = True

            complete_objective(3)

            game_state = EXPLORE

            show_message(
                "BACKUP GENERATOR REPAIRED!",
                180,
                EXPLORE
            )

        elif current_puzzle == "breaker":

            breaker_solved = True

            complete_objective(4)

            game_state = EXPLORE

            show_message(
                "CIRCUIT BREAKER PROBLEM SOLVED!",
                180,
                EXPLORE
            )

        elif current_puzzle == "motor":

            motor_solved = True

            complete_objective(5)

            game_state = EXPLORE

            show_message(
                "MOTOR DRIVE REPAIRED!",
                180,
                EXPLORE
            )

        elif current_puzzle == "scada":

            scada_diagnostics_done = True

            complete_objective(8)

            game_state = EXPLORE

            show_message(
                "SCADA DIAGNOSTIC COMPLETE! Controller communication is healthy.",
                220,
                EXPLORE
            )

        elif current_puzzle == "grid_status":

            grid_status_verified = True

            complete_objective(9)

            game_state = EXPLORE

            show_message(
                "GRID STATUS VERIFIED! The laboratory network is ready for controlled shutdown.",
                220,
                EXPLORE
            )

    else:

        play_sound(
            wrong_sound
        )

        health -= 5
        energy -= 5

        health = max(
            0,
            health
        )

        energy = max(
            0,
            energy
        )

        show_message(
            "WRONG ANSWER! -5 HP / -5 ENERGY",
            150,
            PUZZLE
        )


# ============================================================
# ROBOT INTERACTION
# ============================================================

def inspect_robot():

    global robot_inspected
    global keycard

    if not motor_solved:

        show_message(
            "Robot is inactive. Repair the motor drive first.",
            180
        )

        return

    if not robot_inspected:

        robot_inspected = True

        complete_objective(6)

        add_item(
            "ROBOT DIAGNOSTIC DATA"
        )

        show_message(
            "ROBOT INSPECTED! Search it again for the laboratory keycard.",
            200
        )

    else:

        if not keycard:

            keycard = True

            complete_objective(7)

            add_item(
                "LABORATORY KEYCARD"
            )

            show_message(
                "LABORATORY KEYCARD OBTAINED!",
                200
            )


# ============================================================
# BATTERY ACTIVATION
# ============================================================

def activate_battery():

    global battery_active

    if not battery_inspected:

        show_message(
            "Inspect the battery first.",
            150
        )

        return

    if battery_active:

        show_message(
            "BATTERY SYSTEM IS ALREADY ACTIVE.",
            150
        )

        return

    battery_active = True

    complete_objective(1)

    play_sound(
        interact_sound
    )

    show_message(
        "BATTERY SYSTEM ACTIVATED!",
        180
    )


# ============================================================
# AREA TRANSITIONS
# ============================================================

def enter_power_room():

    global current_area

    if not panel_repaired:

        show_message(
            "POWER ROOM LOCKED! Repair the electrical panel first.",
            180
        )

        return

    play_sound(
        door_sound
    )

    current_area = "POWER ROOM"

    player.x = 90
    player.y = 300

    show_message(
        "ENTERED POWER ROOM",
        120
    )


def enter_control_room():

    global current_area
    global temperature_sound_cooldown

    refresh_objectives()

    if not keycard:

        show_message(
            "CONTROL ROOM LOCKED! You need the laboratory keycard.",
            180
        )

        return

    if not all(
        objective[1]
        for objective in objectives[:8]
    ):

        show_message(
            "CONTROL ROOM ACCESS LIMITED! Finish the laboratory repair sequence first.",
            200
        )

        return

    # The control room is a protected monitoring area.
    # Silence any active laboratory warning/alarm sound before
    # playing the door sound. Background music continues normally.
    if SOUND_ENABLED:
        try:
            pygame.mixer.stop()
        except pygame.error:
            pass

    temperature_sound_cooldown = 0

    play_sound(
        door_sound
    )

    current_area = "CONTROL ROOM"

    # Spawn just inside the real door on the right side of the artwork.
    player.x = 880
    player.y = 360

    show_message(
        "ENTERED CONTROL ROOM",
        120
    )


def return_to_main_lab():

    global current_area

    # Remember where the player came from so the transition feels
    # physically consistent with the door positions in each room.
    came_from_control_room = (
        current_area == "CONTROL ROOM"
    )

    play_sound(
        door_sound
    )

    current_area = "MAIN LAB"

    if came_from_control_room:
        # The control-room door is on the far-right side of the lab.
        # Place the player just inside that same right-side entrance.
        player.x = 930
        player.y = 300
    else:
        # The power room connects to the left side of the lab.
        player.x = 90
        player.y = 300

    show_message(
        "RETURNED TO MAIN LAB",
        120
    )


# ============================================================
# ENTER CAMPUS
# ============================================================

def enter_campus():

    global current_area
    global mission_completed
    global mission_complete_sound_played
    global score
    global game_state

    if current_area == "CAMPUS":
        return

    complete_objective(11)

    remaining_time = max(
        0,
        int(mission_time)
    )

    score += remaining_time * 2
    score += int(max(0, health))

    mission_completed = True

    current_area = "CAMPUS"

    player.x = 120
    player.y = 500

    reset_campus_people()

    # Stop laboratory music and switch to mission-complete music.
    if not mission_complete_sound_played:

        play_mission_complete_only()

        mission_complete_sound_played = True

    game_state = EXPLORE

    show_message(
        "MISSION COMPLETE! YOU ESCAPED THE LABORATORY AND ENTERED YOUR UNIVERSITY CAMPUS.",
        300,
        EXPLORE
    )


# ============================================================
# ESCAPE
# ============================================================

def try_escape():

    refresh_objectives()

    if not keycard:

        show_message(
            "EXIT LOCKED! You need the laboratory keycard.",
            180
        )

        return

    if not all(
        objective[1]
        for objective in objectives[:11]
    ):

        show_message(
            "MISSION INCOMPLETE! Complete the control-room shutdown sequence first.",
            200
        )

        return

    enter_campus()


# ============================================================
# DISTANCE / INTERACTION
# ============================================================

def near_player(
    rect,
    distance=45
):

    return rect.colliderect(
        player.inflate(
            distance * 2,
            distance * 2
        )
    )


# ============================================================
# INTERACT
# ============================================================

def interact():

    global score
    global master_shutdown_done

    if game_state != EXPLORE:
        return

    if current_area == "CAMPUS":

        show_message(
            "Enjoy the university campus. Mission completed!",
            120
        )

        return

    # ========================================================
    # MAIN LAB
    # ========================================================

    if current_area == "MAIN LAB":

        if near_player(
            battery_rect
        ):

            play_sound(
                interact_sound
            )

            if not battery_inspected:

                start_puzzle(
                    "battery"
                )

            else:

                activate_battery()

            return

        if near_player(
            panel_rect
        ):

            if not battery_active:

                show_message(
                    "Panel has no power. Activate battery first.",
                    180
                )

            elif not panel_repaired:

                start_puzzle(
                    "panel"
                )

            else:

                show_message(
                    "Electrical panel is already repaired.",
                    150
                )

            return

        if near_player(
            motor_rect
        ):

            if not breaker_solved:

                show_message(
                    "Motor system requires the circuit breaker to be solved first.",
                    180
                )

            elif not motor_solved:

                start_puzzle(
                    "motor"
                )

            else:

                show_message(
                    "Motor drive is already repaired.",
                    150
                )

            return

        if near_player(
            robot_rect
        ):

            inspect_robot()

            return

        if near_player(
            power_door
        ):

            enter_power_room()

            return

        if near_player(
            control_door
        ):

            enter_control_room()

            return

        if near_player(
            exit_door
        ):

            try_escape()

            return

        show_message(
            "Nothing useful to interact with here.",
            100
        )

    # ========================================================
    # POWER ROOM
    # ========================================================

    elif current_area == "POWER ROOM":

        if near_player(
            generator_rect
        ):

            if not panel_repaired:

                show_message(
                    "Repair the main electrical panel first.",
                    180
                )

            elif not generator_repaired:

                start_puzzle(
                    "generator"
                )

            else:

                show_message(
                    "Backup generator is already repaired.",
                    150
                )

            return

        if near_player(
            breaker_rect
        ):

            if not generator_repaired:

                show_message(
                    "Repair the backup generator first.",
                    180
                )

            elif not breaker_solved:

                start_puzzle(
                    "breaker"
                )

            else:

                show_message(
                    "Circuit breaker is already solved.",
                    150
                )

            return

        if near_player(
            power_back_door
        ):

            return_to_main_lab()

            return

        show_message(
            "Nothing useful to interact with.",
            100
        )

    # ========================================================
    # CONTROL ROOM
    # ========================================================

    elif current_area == "CONTROL ROOM":

        if near_player(scada_console_rect):

            if not scada_diagnostics_done:

                if not all(
                    objective[1]
                    for objective in objectives[:8]
                ):
                    show_message(
                        "SCADA ACCESS LOCKED! Complete the laboratory repair and keycard tasks first.",
                        200
                    )
                else:
                    start_puzzle("scada")

            else:
                show_message(
                    "SCADA DIAGNOSTIC ALREADY COMPLETE.",
                    150
                )

            return

        if near_player(grid_monitor_rect):

            if not scada_diagnostics_done:
                show_message(
                    "GRID MONITOR OFFLINE! Run the SCADA diagnostic scan first.",
                    180
                )

            elif not grid_status_verified:
                start_puzzle("grid_status")

            else:
                show_message(
                    "GRID STATUS ALREADY VERIFIED.",
                    150
                )

            return

        if near_player(shutdown_panel_rect):

            if not scada_diagnostics_done:
                show_message(
                    "SHUTDOWN BLOCKED! Complete the SCADA diagnostic scan first.",
                    180
                )

            elif not grid_status_verified:
                show_message(
                    "SHUTDOWN BLOCKED! Verify the grid operating status first.",
                    180
                )

            elif not master_shutdown_done:

                master_shutdown_done = True

                complete_objective(10)

                score += 250

                play_sound(
                    shutdown_sound
                )

                show_message(
                    "MASTER SHUTDOWN EXECUTED! Laboratory systems are safely offline. Return to the main lab and escape.",
                    260
                )

            else:
                show_message(
                    "MASTER SHUTDOWN IS ALREADY COMPLETE.",
                    150
                )

            return

        if near_player(control_back_door):

            return_to_main_lab()

            return

        show_message(
            "Nothing useful to interact with.",
            100
        )


# ============================================================
# MOVEMENT SOLIDS
# ============================================================

def get_solid_objects():

    if current_area == "MAIN LAB":

        return [
            battery_rect,
            panel_rect,
            robot_rect,
            motor_rect
        ]

    elif current_area == "POWER ROOM":

        return [
            generator_rect,
            breaker_rect
        ]

    elif current_area == "CONTROL ROOM":

        return [
            scada_console_rect,
            grid_monitor_rect,
            shutdown_panel_rect
        ]

    return []


# ============================================================
# MOVEMENT
# ============================================================

def move_player():

    global energy
    global player_animation_time
    global player_facing
    global player_stride

    keys = pygame.key.get_pressed()

    dx = 0
    dy = 0

    if (
        keys[pygame.K_w]
        or keys[pygame.K_UP]
    ):

        dy -= PLAYER_SPEED

    if (
        keys[pygame.K_s]
        or keys[pygame.K_DOWN]
    ):

        dy += PLAYER_SPEED

    if (
        keys[pygame.K_a]
        or keys[pygame.K_LEFT]
    ):

        dx -= PLAYER_SPEED

    if (
        keys[pygame.K_d]
        or keys[pygame.K_RIGHT]
    ):

        dx += PLAYER_SPEED

    moving = (
        dx != 0
        or dy != 0
    )

    # Face the direction of horizontal travel.
    if dx > 0:
        player_facing = 1
    elif dx < 0:
        player_facing = -1

    if moving:

        energy -= 0.08

        energy = max(
            0,
            energy
        )

        player_animation_time += 0.22
        player_stride += 0.22

    else:

        player_stride += 0.08
        player_stride %= (math.pi * 2)

        energy += 0.04

        energy = min(
            MAX_ENERGY,
            energy
        )

        player_animation_time += 0.06

    solids = get_solid_objects()

    player.x += dx

    for obj in solids:

        if player.colliderect(obj):

            if dx > 0:
                player.right = obj.left

            elif dx < 0:
                player.left = obj.right

    player.y += dy

    for obj in solids:

        if player.colliderect(obj):

            if dy > 0:
                player.bottom = obj.top

            elif dy < 0:
                player.top = obj.bottom

    player.left = max(
        0,
        player.left
    )

    player.right = min(
        WIDTH,
        player.right
    )

    player.top = max(
        72,
        player.top
    )

    player.bottom = min(
        HEIGHT,
        player.bottom
    )


# ============================================================
# ANIMATED PLAYER
# ============================================================

def draw_animated_player():

    moving_keys = pygame.key.get_pressed()

    moving = (
        moving_keys[pygame.K_w]
        or moving_keys[pygame.K_a]
        or moving_keys[pygame.K_s]
        or moving_keys[pygame.K_d]
        or moving_keys[pygame.K_UP]
        or moving_keys[pygame.K_DOWN]
        or moving_keys[pygame.K_LEFT]
        or moving_keys[pygame.K_RIGHT]
    )

    if selected_character == "TOYASIN":
        walk_frames = toyasin_walk_frames
    else:
        walk_frames = mehedi_walk_frames

    if moving:
        walk_phase = player_stride
        frame_index = int((walk_phase / (math.pi * 2)) * 4) % 4
        bob = int(math.sin(walk_phase * 2.0) * 2.5)
        lean = math.sin(walk_phase * 2.0) * 2.0
    else:
        walk_phase = animation_time * 1.2
        frame_index = 0
        bob = int(math.sin(animation_time * 2.0) * 1.0)
        lean = math.sin(animation_time * 1.4) * 0.6

    shadow_width = int(player.width * (0.78 + 0.06 * math.sin(walk_phase * 2.0)))
    shadow = pygame.Rect(
        player.centerx - shadow_width // 2,
        player.bottom - 8,
        shadow_width,
        10
    )

    shadow_surface = pygame.Surface(shadow.size, pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect())
    screen.blit(shadow_surface, shadow.topleft)

    if walk_frames:
        frame = walk_frames[frame_index]
        if player_facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        draw_rect = frame.get_rect(center=(player.centerx, player.centery + bob))
        screen.blit(frame, draw_rect)
    else:
        # Fallback animation for the current single character artwork.
        # It now faces left/right correctly and has a subtle stride, bob and lean.
        frame = player_img
        if player_facing < 0:
            frame = pygame.transform.flip(frame, True, False)

        if moving:
            scale_y = 1.0 + 0.018 * math.sin(walk_phase * 2.0)
            scale_x = 1.0 - 0.012 * math.sin(walk_phase * 2.0)
            frame_w = max(1, int(frame.get_width() * scale_x))
            frame_h = max(1, int(frame.get_height() * scale_y))
            frame = pygame.transform.smoothscale(frame, (frame_w, frame_h))
            frame = pygame.transform.rotozoom(frame, -lean * player_facing, 1.0)

        draw_rect = frame.get_rect(center=(player.centerx, player.centery + bob))
        screen.blit(frame, draw_rect)

    # Small alternating foot-contact effect.
    if moving and current_area != "CAMPUS":
        step_side = -1 if math.sin(walk_phase * 2.0) < 0 else 1
        foot_x = player.centerx + step_side * 10
        foot_y = player.bottom - 2
        step_alpha = int(75 + 55 * abs(math.sin(walk_phase * 2.0)))
        step_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(step_surface, (180, 220, 230, step_alpha), (4, 4), 2)
        screen.blit(step_surface, (foot_x - 4, foot_y - 4))

    if current_area == "CAMPUS":

        pulse = int(
            5
            + 4
            * (
                math.sin(animation_time * 3) + 1
            )
            / 2
        )

        marker = pygame.Rect(
            player.x - pulse,
            player.y - pulse,
            player.width + pulse * 2,
            player.height + pulse * 2
        )

        pygame.draw.ellipse(
            screen,
            GREEN,
            marker,
            2
        )


# ============================================================
# DRONE AI
# ============================================================

def update_drone():

    global drone_direction
    global drone_chasing
    global drone_damage_cooldown
    global health

    if current_area != "MAIN LAB":
        return

    distance = math.hypot(
        player.centerx - drone_rect.centerx,
        player.centery - drone_rect.centery
    )

    if distance < 280:
        drone_chasing = True

    elif distance > 360:
        drone_chasing = False

    if drone_chasing:

        if player.centerx > drone_rect.centerx:
            drone_rect.x += drone_speed

        else:
            drone_rect.x -= drone_speed

        if player.centery > drone_rect.centery:
            drone_rect.y += drone_speed

        else:
            drone_rect.y -= drone_speed

    else:

        drone_rect.x += (
            drone_speed
            * drone_direction
        )

        if drone_rect.left <= DRONE_PATROL_LEFT:
            drone_direction = 1

        elif drone_rect.right >= DRONE_PATROL_RIGHT:
            drone_direction = -1

    drone_rect.x = max(
        DRONE_PATROL_LEFT,
        min(
            drone_rect.x,
            DRONE_PATROL_RIGHT
            - drone_rect.width
        )
    )

    drone_rect.y = max(
        90,
        min(
            drone_rect.y,
            250
        )
    )

    if drone_damage_cooldown > 0:
        drone_damage_cooldown -= 1

    if (
        player.colliderect(drone_rect)
        and drone_damage_cooldown <= 0
    ):

        health -= 3

        drone_damage_cooldown = FPS

        play_sound(
            warning_sound
        )


# ============================================================
# ANIMATED DRONE
# ============================================================

def draw_animated_drone():

    bob = int(
        math.sin(
            animation_time * 3
        ) * 5
    )

    drone_x = drone_rect.x
    drone_y = drone_rect.y + bob

    # Shadow
    shadow = pygame.Rect(
        drone_x + 8,
        drone_y + 48,
        40,
        10
    )

    shadow_surface = pygame.Surface(
        shadow.size,
        pygame.SRCALPHA
    )

    pygame.draw.ellipse(
        shadow_surface,
        (0, 0, 0, 70),
        shadow_surface.get_rect()
    )

    screen.blit(
        shadow_surface,
        shadow.topleft
    )

    # Scanning circle
    scan_radius = int(
        28
        + 8
        * (
            math.sin(
                animation_time * 2
            ) + 1
        )
        / 2
    )

    scan_surface = pygame.Surface(
        (100, 100),
        pygame.SRCALPHA
    )

    pygame.draw.circle(
        scan_surface,
        (255, 50, 50, 30),
        (50, 50),
        scan_radius,
        2
    )

    screen.blit(
        scan_surface,
        (
            drone_x - 22,
            drone_y - 22
        )
    )

    screen.blit(
        drone_img,
        (
            drone_x,
            drone_y
        )
    )

    # Warning light
    light_value = int(
        120
        + 100
        * (
            math.sin(
                animation_time * 7
            ) + 1
        )
        / 2
    )

    pygame.draw.circle(
        screen,
        (
            255,
            light_value,
            40
        ),
        (
            drone_x + 27,
            drone_y + 10
        ),
        5
    )


# ============================================================
# HAZARD SYSTEM
# ============================================================

def update_hazards():

    global health
    global hazard_damage_cooldown

    if current_area != "MAIN LAB":
        return

    if hazard_damage_cooldown > 0:
        hazard_damage_cooldown -= 1

    for hazard in hazards:

        if (
            player.colliderect(hazard)
            and hazard_damage_cooldown <= 0
        ):

            health -= 5

            hazard_damage_cooldown = FPS

            play_sound(
                warning_sound
            )

            break


# ============================================================
# TEMPERATURE SYSTEM
# ============================================================

def update_temperature():

    global machine_temperature
    global health
    global temperature_sound_cooldown

    # The control room is environmentally safe. It has no heat hazard,
    # so entering it must never drain health or trigger the laboratory alarm.
    if current_area == "CONTROL ROOM":
        temperature_sound_cooldown = 0
        return

    if battery_active:

        machine_temperature += 0.01

    else:

        machine_temperature -= 0.015

    machine_temperature = max(
        25,
        min(
            100,
            machine_temperature
        )
    )

    if machine_temperature > 85:

        health -= 0.025

        if temperature_sound_cooldown <= 0:

            play_sound(
                warning_sound
            )

            temperature_sound_cooldown = FPS * 4

    if temperature_sound_cooldown > 0:
        temperature_sound_cooldown -= 1


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(
    text,
    x,
    y,
    font=FONT,
    color=WHITE
):

    surface = font.render(
        text,
        True,
        color
    )

    screen.blit(
        surface,
        (x, y)
    )


# ============================================================
# CENTER TEXT
# ============================================================

def draw_center_text(
    text,
    y,
    font=FONT,
    color=WHITE
):

    surface = font.render(
        text,
        True,
        color
    )

    screen.blit(
        surface,
        (
            WIDTH // 2
            - surface.get_width() // 2,
            y
        )
    )


# ============================================================
# DRAW BAR
# ============================================================

def draw_bar(
    x,
    y,
    width,
    height,
    value,
    maximum,
    color,
    label
):

    pygame.draw.rect(
        screen,
        BLACK,
        (
            x,
            y,
            width,
            height
        )
    )

    percentage = max(
        0,
        min(
            1,
            value / maximum
        )
    )

    pygame.draw.rect(
        screen,
        color,
        (
            x,
            y,
            int(
                width
                * percentage
            ),
            height
        )
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (
            x,
            y,
            width,
            height
        ),
        2
    )

    draw_text(
        label,
        x,
        y - 23,
        SMALL_FONT,
        WHITE
    )


# ============================================================
# HUD
# ============================================================

def draw_hud():

    pygame.draw.rect(
        screen,
        (10, 15, 20),
        (
            0,
            0,
            WIDTH,
            72
        )
    )

    pygame.draw.line(
        screen,
        CYAN,
        (0, 72),
        (WIDTH, 72),
        2
    )

    draw_bar(
        20,
        35,
        180,
        18,
        health,
        MAX_HEALTH,
        RED,
        "HEALTH"
    )

    draw_bar(
        230,
        35,
        180,
        18,
        energy,
        MAX_ENERGY,
        BLUE,
        "ENERGY"
    )

    temp_color = GREEN

    if machine_temperature > 70:
        temp_color = ORANGE

    if machine_temperature > 85:
        temp_color = RED

    draw_bar(
        440,
        35,
        180,
        18,
        machine_temperature,
        100,
        temp_color,
        "TEMPERATURE"
    )

    minutes = int(
        mission_time // 60
    )

    seconds = int(
        mission_time % 60
    )

    draw_text(
        f"TIME {minutes:02d}:{seconds:02d}",
        650,
        31,
        FONT,
        YELLOW
    )

    draw_text(
        f"SCORE {score}",
        850,
        31,
        FONT,
        CYAN
    )


# ============================================================
# DRAW LABEL
# ============================================================

def draw_label(
    text,
    rect,
    color=WHITE
):

    label = SMALL_FONT.render(
        text,
        True,
        color
    )

    background = pygame.Rect(
        rect.centerx
        - label.get_width() // 2
        - 6,
        rect.top - 28,
        label.get_width() + 12,
        label.get_height() + 6
    )

    pygame.draw.rect(
        screen,
        (10, 15, 20),
        background,
        border_radius=5
    )

    screen.blit(
        label,
        (
            background.x + 6,
            background.y + 3
        )
    )


# ============================================================
# OBJECT HIGHLIGHT
# ============================================================

def draw_object_highlight(rect):

    pulse = int(
        3
        + 3
        * (
            math.sin(
                animation_time * 4
            ) + 1
        )
        / 2
    )

    highlight = rect.inflate(
        10 + pulse,
        10 + pulse
    )

    pygame.draw.rect(
        screen,
        CYAN,
        highlight,
        3,
        border_radius=5
    )


# ============================================================
# HAZARD ZONE
# ============================================================

def draw_hazard_zone(rect):

    phase = animation_time * 3.0

    glow_strength = int(
        45
        + 35
        * (
            math.sin(
                phase
            ) + 1
        )
        / 2
    )

    glow_surface = pygame.Surface(
        (
            rect.width + 40,
            rect.height + 40
        ),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        glow_surface,
        (
            255,
            40,
            20,
            glow_strength
        ),
        glow_surface.get_rect(),
        border_radius=14
    )

    screen.blit(
        glow_surface,
        (
            rect.x - 20,
            rect.y - 20
        )
    )

    pygame.draw.rect(
        screen,
        (45, 30, 25),
        rect,
        border_radius=8
    )

    # Moving hazard stripes
    stripe_width = 14

    offset = int(
        animation_time * 50
    ) % (
        stripe_width * 2
    )

    for x in range(
        rect.left
        - rect.height
        - stripe_width * 2,
        rect.right
        + rect.height,
        stripe_width * 2
    ):

        x2 = x + offset

        points = [

            (
                x2,
                rect.bottom
            ),

            (
                x2 + stripe_width,
                rect.bottom
            ),

            (
                x2
                + rect.height
                + stripe_width,
                rect.top
            ),

            (
                x2
                + rect.height,
                rect.top
            )

        ]

        pygame.draw.polygon(
            screen,
            (245, 180, 30),
            points
        )

    pygame.draw.rect(
        screen,
        (255, 70, 40),
        rect,
        3,
        border_radius=8
    )

    cx = rect.centerx
    cy = rect.centery

    # Different animation based on hazard position
    hazard_index = hazards.index(rect)

    if hazard_index == 0:

        # Electrical sparks
        for i in range(5):

            angle = (
                animation_time * 4
                + i * 1.25
            )

            radius = 18 + (
                i % 3
            ) * 7

            sx = int(
                cx
                + math.cos(angle)
                * radius
            )

            sy = int(
                cy
                + math.sin(angle)
                * radius
            )

            ex = sx + random.randint(
                -8,
                8
            )

            ey = sy + random.randint(
                -8,
                8
            )

            pygame.draw.line(
                screen,
                YELLOW,
                (sx, sy),
                (ex, ey),
                2
            )

        pygame.draw.circle(
            screen,
            CYAN,
            (cx, cy),
            14,
            2
        )

        draw_text(
            "ELECTRICAL",
            rect.centerx - 45,
            rect.top + 5,
            SMALL_FONT,
            WHITE
        )

    elif hazard_index == 1:

        # Heat waves
        for i in range(3):

            wave = (
                animation_time * 2
                + i * 1.5
            )

            wave_x = int(
                cx
                + math.sin(wave)
                * 45
            )

            wave_y = int(
                cy
                - 10
                - (
                    (wave * 18)
                    % 35
                )
            )

            pygame.draw.arc(
                screen,
                ORANGE,
                (
                    wave_x - 15,
                    wave_y - 15,
                    30,
                    30
                ),
                0,
                math.pi,
                2
            )

        pygame.draw.circle(
            screen,
            ORANGE,
            (cx, cy),
            15,
            2
        )

        draw_text(
            "OVERHEAT",
            rect.centerx - 42,
            rect.top + 5,
            SMALL_FONT,
            WHITE
        )

    else:

        # High voltage pulse
        pulse = int(
            10
            + 8
            * (
                math.sin(
                    animation_time * 5
                ) + 1
            )
            / 2
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (cx, cy),
            pulse,
            2
        )

        pygame.draw.polygon(
            screen,
            YELLOW,
            [
                (cx, cy - 15),
                (cx - 10, cy + 5),
                (cx + 2, cy + 5),
                (cx - 3, cy + 18),
                (cx + 14, cy - 5),
                (cx + 3, cy - 5)
            ]
        )

        draw_text(
            "HIGH VOLTAGE",
            rect.centerx - 55,
            rect.top + 5,
            SMALL_FONT,
            WHITE
        )


# ============================================================
# EXIT DOOR
# ============================================================

def draw_exit_door():

    frame = exit_door.inflate(
        14,
        14
    )

    pygame.draw.rect(
        screen,
        (30, 30, 35),
        frame,
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        (45, 65, 80),
        exit_door,
        border_radius=4
    )

    pygame.draw.rect(
        screen,
        (70, 90, 105),
        (
            exit_door.x + 10,
            exit_door.y + 15,
            80,
            45
        ),
        2
    )

    pygame.draw.rect(
        screen,
        (70, 90, 105),
        (
            exit_door.x + 10,
            exit_door.y + 75,
            80,
            45
        ),
        2
    )

    light = int(
        130
        + 100
        * (
            math.sin(
                animation_time * 4
            ) + 1
        )
        / 2
    )

    pygame.draw.circle(
        screen,
        (255, light // 3, 40),
        (
            exit_door.centerx,
            exit_door.top - 12
        ),
        7
    )

    pygame.draw.circle(
        screen,
        (220, 190, 80),
        (
            exit_door.right - 18,
            exit_door.centery
        ),
        5
    )

    sign = pygame.Rect(
        exit_door.x - 5,
        exit_door.y - 48,
        exit_door.width + 10,
        30
    )

    pygame.draw.rect(
        screen,
        (20, 100, 45),
        sign,
        border_radius=5
    )

    pygame.draw.rect(
        screen,
        WHITE,
        sign,
        2,
        border_radius=5
    )

    text = SMALL_FONT.render(
        "EXIT DOOR",
        True,
        WHITE
    )

    screen.blit(
        text,
        (
            sign.centerx
            - text.get_width() // 2,
            sign.centery
            - text.get_height() // 2
        )
    )


# ============================================================
# MAIN LAB
# ============================================================

def draw_main_lab():

    screen.blit(
        laboratory_img,
        (0, 0)
    )

    for hazard in hazards:

        draw_hazard_zone(
            hazard
        )

    screen.blit(
        battery_img,
        battery_rect.topleft
    )

    draw_label(
        "BATTERY",
        battery_rect,
        CYAN
    )

    screen.blit(
        panel_img,
        panel_rect.topleft
    )

    draw_label(
        "ELECTRICAL PANEL",
        panel_rect,
        CYAN
    )

    screen.blit(
        robot_img,
        robot_rect.topleft
    )

    draw_label(
        "LAB ROBOT",
        robot_rect,
        CYAN
    )

    screen.blit(
        motor_img,
        motor_rect.topleft
    )

    draw_label(
        "MOTOR",
        motor_rect,
        CYAN
    )

    screen.blit(
        door_img,
        power_door.topleft
    )

    draw_label(
        "POWER ROOM",
        power_door,
        ORANGE
    )

    screen.blit(
        door_img,
        control_door.topleft
    )

    draw_label(
        "CONTROL ROOM",
        control_door,
        CYAN
    )

    draw_exit_door()

    draw_animated_drone()


# ============================================================
# POWER ROOM
# ============================================================

def draw_power_room():

    screen.blit(
        power_room_img,
        (0, 0)
    )

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (20, 30, 40, 45)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        "POWER ROOM",
        30,
        90,
        BIG_FONT,
        YELLOW
    )

    draw_text(
        "BACKUP POWER & CIRCUIT SYSTEM",
        30,
        130,
        SMALL_FONT,
        WHITE
    )

    screen.blit(
        generator_img,
        generator_rect.topleft
    )

    draw_label(
        "BACKUP GENERATOR",
        generator_rect,
        ORANGE
    )

    screen.blit(
        breaker_img,
        breaker_rect.topleft
    )

    draw_label(
        "CIRCUIT BREAKER",
        breaker_rect,
        YELLOW
    )

    # Animated power flow
    flow_offset = int(
        animation_time * 80
    ) % 30

    for y in range(
        breaker_rect.bottom + 20,
        generator_rect.top - 20,
        30
    ):

        pygame.draw.circle(
            screen,
            CYAN,
            (
                generator_rect.centerx,
                y + flow_offset
            ),
            4
        )

    pygame.draw.line(
        screen,
        CYAN,
        (
            generator_rect.centerx,
            generator_rect.top - 20
        ),
        (
            generator_rect.centerx,
            breaker_rect.bottom + 20
        ),
        3
    )

    pygame.draw.circle(
        screen,
        GREEN if generator_repaired else RED,
        (
            generator_rect.centerx,
            generator_rect.top - 20
        ),
        8
    )

    pygame.draw.circle(
        screen,
        GREEN if breaker_solved else RED,
        (
            breaker_rect.centerx,
            breaker_rect.bottom + 20
        ),
        8
    )

    draw_text(
        "GENERATOR → BREAKER → MOTOR",
        350,
        580,
        SMALL_FONT,
        CYAN
    )

    screen.blit(
        door_img,
        power_back_door.topleft
    )

    draw_label(
        "MAIN LAB",
        power_back_door,
        WHITE
    )


# ============================================================
# CONTROL ROOM
# ============================================================

def draw_control_room():

    # Dedicated generated control-room artwork.
    screen.blit(
        control_room_img,
        (0, 0)
    )

    # Subtle cinematic tint.
    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (5, 15, 30, 35)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_text(
        "CONTROL ROOM",
        30,
        88,
        BIG_FONT,
        CYAN
    )

    draw_text(
        "SCADA • GRID MONITORING • MASTER SHUTDOWN",
        30,
        128,
        SMALL_FONT,
        WHITE
    )

    scada_color = GREEN if scada_diagnostics_done else YELLOW
    scada_text = (
        "SCADA ONLINE"
        if scada_diagnostics_done
        else "RUN SCADA DIAGNOSTIC"
    )

    pygame.draw.circle(
        screen,
        scada_color,
        scada_console_rect.center,
        9
    )

    draw_label(
        scada_text,
        scada_console_rect,
        scada_color
    )

    grid_color = GREEN if grid_status_verified else YELLOW
    grid_text = (
        "GRID STATUS VERIFIED"
        if grid_status_verified
        else "VERIFY GRID STATUS"
    )

    pygame.draw.circle(
        screen,
        grid_color,
        grid_monitor_rect.center,
        9
    )

    draw_label(
        grid_text,
        grid_monitor_rect,
        grid_color
    )

    shutdown_color = GREEN if master_shutdown_done else RED
    shutdown_text = (
        "MASTER SHUTDOWN COMPLETE"
        if master_shutdown_done
        else "MASTER SHUTDOWN PANEL"
    )

    pygame.draw.circle(
        screen,
        shutdown_color,
        shutdown_panel_rect.center,
        9
    )

    draw_label(
        shutdown_text,
        shutdown_panel_rect,
        shutdown_color
    )

    # Animated SCADA data bars.
    for i in range(9):

        x = 350 + i * 28

        height = int(
            18
            + (
                math.sin(
                    animation_time * 3
                    + i * 0.7
                )
                + 1
            )
            * 16
        )

        pygame.draw.line(
            screen,
            (50, 210, 220),
            (x, 500),
            (x, 500 - height),
            3
        )

    # Soft animated status outlines.
    pulse = int(
        4
        + 3
        * (
            math.sin(
                animation_time * 4
            ) + 1
        )
        / 2
    )

    for rect, color in [
        (scada_console_rect, scada_color),
        (grid_monitor_rect, grid_color),
        (shutdown_panel_rect, shutdown_color)
    ]:

        glow_rect = rect.inflate(
            pulse * 2,
            pulse * 2
        )

        pygame.draw.rect(
            screen,
            color,
            glow_rect,
            2,
            border_radius=10
        )

    screen.blit(
        door_img,
        control_back_door.topleft
    )

    draw_label(
        "MAIN LAB",
        control_back_door,
        WHITE
    )


# ============================================================
# CAMPUS PEOPLE UPDATE
# ============================================================

def update_campus_people(dt):

    for person in campus_people:

        if person["pause"] > 0:

            person["pause"] -= dt

            if person["pause"] <= 0:
                person["walking"] = True

            continue

        person["x"] += (
            person["speed"]
            * person["direction"]
        )

        if (
            random.random()
            < 0.0007
        ):

            person["walking"] = False

            person["pause"] = random.uniform(
                1.0,
                3.0
            )

        if person["x"] < -30:

            person["x"] = WIDTH + 30

        elif person["x"] > WIDTH + 30:

            person["x"] = -30


# ============================================================
# CAMPUS PEOPLE DRAW
# ============================================================

def draw_campus_person(person):

    x = int(
        person["x"]
    )

    y = int(
        person["y"]
        + math.sin(
            animation_time * 3
            + person["phase"]
        ) * 1.5
    )

    scale = person["scale"]

    head_radius = max(
        5,
        int(7 * scale)
    )

    body_width = max(
        8,
        int(14 * scale)
    )

    body_height = max(
        12,
        int(23 * scale)
    )

    leg_length = max(
        7,
        int(13 * scale)
    )

    # Ground shadow
    pygame.draw.ellipse(
        screen,
        (20, 40, 25),
        (
            x - int(10 * scale),
            y + int(27 * scale),
            int(20 * scale),
            int(6 * scale)
        )
    )

    # Head
    pygame.draw.circle(
        screen,
        person["skin"],
        (
            x,
            y
        ),
        head_radius
    )

    # Hair
    pygame.draw.arc(
        screen,
        (35, 25, 20),
        (
            x - head_radius,
            y - head_radius,
            head_radius * 2,
            head_radius * 2
        ),
        math.pi,
        math.pi * 2,
        max(2, int(2 * scale))
    )

    # Body
    body_rect = pygame.Rect(
        x - body_width // 2,
        y + head_radius,
        body_width,
        body_height
    )

    pygame.draw.rect(
        screen,
        person["shirt"],
        body_rect,
        border_radius=4
    )

    # Legs
    leg_y = body_rect.bottom

    walk_offset = 0

    if person["walking"]:

        walk_offset = int(
            math.sin(
                animation_time * 8
                + person["phase"]
            )
            * 4
            * scale
        )

    pygame.draw.line(
        screen,
        (35, 45, 55),
        (
            x - int(3 * scale),
            leg_y
        ),
        (
            x - int(4 * scale) + walk_offset,
            leg_y + leg_length
        ),
        max(2, int(3 * scale))
    )

    pygame.draw.line(
        screen,
        (35, 45, 55),
        (
            x + int(3 * scale),
            leg_y
        ),
        (
            x + int(4 * scale) - walk_offset,
            leg_y + leg_length
        ),
        max(2, int(3 * scale))
    )


# ============================================================
# CAMPUS BIRDS
# ============================================================

def update_campus_birds():

    for bird in campus_birds:

        bird["x"] += bird["speed"]

        bird["y"] += math.sin(
            animation_time
            + bird["phase"]
        ) * 0.15

        if bird["x"] > WIDTH + 30:

            bird["x"] = -30

            bird["y"] = random.randint(
                80,
                260
            )


def draw_campus_birds():

    for bird in campus_birds:

        x = int(
            bird["x"]
        )

        y = int(
            bird["y"]
        )

        wing = int(
            4
            * math.sin(
                animation_time * 8
                + bird["phase"]
            )
        )

        pygame.draw.arc(
            screen,
            (35, 50, 45),
            (
                x - 10,
                y - wing,
                10,
                8
            ),
            0,
            math.pi,
            1
        )

        pygame.draw.arc(
            screen,
            (35, 50, 45),
            (
                x,
                y + wing,
                10,
                8
            ),
            0,
            math.pi,
            1
        )


# ============================================================
# CAMPUS PARTICLES
# ============================================================

def update_campus_particles():

    for particle in campus_particles:

        particle["y"] -= particle["speed"]

        particle["x"] += (
            math.sin(
                animation_time
                + particle["phase"]
            )
            * 0.12
        )

        if particle["y"] < 100:

            particle["y"] = HEIGHT

            particle["x"] = random.randint(
                0,
                WIDTH
            )


def draw_campus_particles():

    for particle in campus_particles:

        brightness = int(
            80
            + 40
            * (
                math.sin(
                    animation_time * 2
                    + particle["phase"]
                )
                + 1
            )
            / 2
        )

        pygame.draw.circle(
            screen,
            (
                100,
                brightness,
                120
            ),
            (
                int(particle["x"]),
                int(particle["y"])
            ),
            1
        )


# ============================================================
# CAMPUS DECORATIVE ANIMATION
# ============================================================

def draw_campus_atmosphere():

    # Soft sun glow
    glow_surface = pygame.Surface(
        (180, 180),
        pygame.SRCALPHA
    )

    for radius in range(
        80,
        10,
        -10
    ):

        alpha = int(
            2
            + (
                80 - radius
            ) * 0.15
        )

        pygame.draw.circle(
            glow_surface,
            (
                255,
                230,
                130,
                max(2, alpha)
            ),
            (90, 90),
            radius
        )

    screen.blit(
        glow_surface,
        (
            WIDTH - 180,
            70
        )
    )


# ============================================================
# UNIVERSITY CAMPUS
# ============================================================

def draw_campus():

    screen.blit(
        campus_img,
        (0, 0)
    )

    draw_campus_atmosphere()

    update_campus_particles()
    draw_campus_particles()

    draw_campus_birds()

    # No random people are drawn in the campus scene.
    # The player character is rendered by draw_world().

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 20, 10, 25)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    # ========================================================
    # CAMPUS HEADER
    # ========================================================

    title_box = pygame.Rect(
        20,
        18,
        430,
        72
    )

    pygame.draw.rect(
        screen,
        (10, 25, 22),
        title_box,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        GREEN,
        title_box,
        2,
        border_radius=12
    )

    draw_text(
        "JKKNIU UNIVERSITY CAMPUS",
        38,
        28,
        FONT,
        WHITE
    )

    draw_text(
        "MISSION COMPLETE • FREE ROAM",
        38,
        57,
        SMALL_FONT,
        GREEN
    )

    # ========================================================
    # CHARACTER INFORMATION
    # ========================================================

    character_box = pygame.Rect(
        WIDTH - 300,
        18,
        280,
        72
    )

    pygame.draw.rect(
        screen,
        (10, 25, 22),
        character_box,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        CYAN,
        character_box,
        2,
        border_radius=12
    )

    draw_text(
        selected_character,
        character_box.x + 15,
        character_box.y + 12,
        FONT,
        CYAN
    )

    draw_text(
        "ENGINEER • SURVIVOR",
        character_box.x + 15,
        character_box.y + 42,
        SMALL_FONT,
        WHITE
    )

    # ========================================================
    # SUCCESS BADGE
    # ========================================================

    badge = pygame.Rect(
        WIDTH // 2 - 180,
        105,
        360,
        50
    )

    pygame.draw.rect(
        screen,
        (10, 40, 25),
        badge,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        GREEN,
        badge,
        2,
        border_radius=10
    )

    badge_text = SMALL_FONT.render(
        "LABORATORY ESCAPE SUCCESSFUL",
        True,
        GREEN
    )

    screen.blit(
        badge_text,
        (
            badge.centerx
            - badge_text.get_width() // 2,
            badge.y + 15
        )
    )

    # ========================================================
    # CAMPUS STATUS
    # ========================================================

    status_box = pygame.Rect(
        20,
        105,
        270,
        55
    )

    pygame.draw.rect(
        screen,
        (10, 25, 22),
        status_box,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        GREEN,
        status_box,
        2,
        border_radius=10
    )

    draw_text(
        "CAMPUS STATUS: SAFE",
        status_box.x + 15,
        status_box.y + 8,
        SMALL_FONT,
        GREEN
    )

    draw_text(
        "MISSION THREATS: NONE",
        status_box.x + 15,
        status_box.y + 30,
        SMALL_FONT,
        WHITE
    )

    # ========================================================
    # CONTROLS
    # ========================================================

    controls = pygame.Rect(
        20,
        HEIGHT - 78,
        500,
        55
    )

    pygame.draw.rect(
        screen,
        (10, 20, 18),
        controls,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        CYAN,
        controls,
        2,
        border_radius=10
    )

    draw_text(
        "WASD / ARROWS = Explore",
        32,
        HEIGHT - 65,
        SMALL_FONT,
        WHITE
    )

    draw_text(
        "P = Pause    ESC = Menu",
        32,
        HEIGHT - 42,
        SMALL_FONT,
        WHITE
    )


# ============================================================
# CURRENT OBJECTIVE
# ============================================================

def get_current_objective():

    refresh_objectives()

    for index, objective in enumerate(objectives):

        if not objective[1]:

            return index, objective[0]

    return len(objectives) - 1, "Mission complete"


def draw_current_objective():

    if current_area == "CAMPUS":
        return

    index, objective_text = get_current_objective()

    panel = pygame.Rect(
        18,
        82,
        500,
        62
    )

    pygame.draw.rect(
        screen,
        (5, 15, 25),
        panel,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        CYAN,
        panel,
        2,
        border_radius=10
    )

    draw_text(
        "CURRENT OBJECTIVE",
        panel.x + 14,
        panel.y + 8,
        SMALL_FONT,
        CYAN
    )

    draw_text(
        f"{index + 1:02d}  {objective_text}",
        panel.x + 14,
        panel.y + 31,
        SMALL_FONT,
        WHITE
    )


# ============================================================
# MISSION MAP
# ============================================================

def draw_mission_map(x, y, width=980, height=405):

    map_rect = pygame.Rect(
        x,
        y,
        width,
        height
    )

    pygame.draw.rect(
        screen,
        (7, 16, 27),
        map_rect,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        (35, 85, 105),
        map_rect,
        2,
        border_radius=18
    )

    draw_text(
        "MISSION MAP",
        map_rect.x + 24,
        map_rect.y + 18,
        BIG_FONT,
        CYAN
    )

    draw_text(
        "ENGINEERING SURVIVAL ROUTE",
        map_rect.x + 27,
        map_rect.y + 58,
        SMALL_FONT,
        GRAY
    )

    # A single continuous serpentine route. Node 12 now sits directly
    # on the same second-row path, so it can never look disconnected.
    nodes = [
        ("1", "BATTERY", 90, 145, 0),
        ("2", "ACTIVATE", 245, 145, 1),
        ("3", "PANEL", 400, 145, 2),
        ("4", "POWER", 555, 145, 3),
        ("5", "BREAKER", 710, 145, 4),
        ("6", "MOTOR", 865, 145, 5),
        ("7", "ROBOT", 865, 290, 6),
        ("8", "KEYCARD", 710, 290, 7),
        ("9", "SCADA", 555, 290, 8),
        ("10", "GRID", 400, 290, 9),
        ("11", "SHUTDOWN", 245, 290, 10),
        ("12", "CAMPUS", 90, 290, 11)
    ]

    route_points = [
        (map_rect.x + 90, map_rect.y + 145),
        (map_rect.x + 245, map_rect.y + 145),
        (map_rect.x + 400, map_rect.y + 145),
        (map_rect.x + 555, map_rect.y + 145),
        (map_rect.x + 710, map_rect.y + 145),
        (map_rect.x + 865, map_rect.y + 145),
        (map_rect.x + 865, map_rect.y + 290),
        (map_rect.x + 710, map_rect.y + 290),
        (map_rect.x + 555, map_rect.y + 290),
        (map_rect.x + 400, map_rect.y + 290),
        (map_rect.x + 245, map_rect.y + 290),
        (map_rect.x + 90, map_rect.y + 290)
    ]

    for i in range(len(route_points) - 1):

        pygame.draw.line(
            screen,
            (45, 85, 105),
            route_points[i],
            route_points[i + 1],
            3
        )

    current_index, _ = get_current_objective()

    for number, label, nx, ny, index in nodes:

        state = objectives[index][1]

        if state:
            color = GREEN
        elif index == current_index:
            color = YELLOW
        else:
            color = (90, 105, 120)

        center = (
            map_rect.x + nx,
            map_rect.y + ny
        )

        pygame.draw.circle(
            screen,
            (8, 20, 32),
            center,
            28
        )

        pygame.draw.circle(
            screen,
            color,
            center,
            28,
            3
        )

        number_surface = SMALL_FONT.render(
            number,
            True,
            color
        )

        screen.blit(
            number_surface,
            (
                center[0]
                - number_surface.get_width() // 2,
                center[1]
                - number_surface.get_height() // 2
            )
        )

        label_surface = SMALL_FONT.render(
            label,
            True,
            WHITE
        )

        screen.blit(
            label_surface,
            (
                center[0]
                - label_surface.get_width() // 2,
                center[1] + 34
            )
        )

    draw_text(
        "GREEN = COMPLETE     YELLOW = NEXT TASK     GREY = LOCKED",
        map_rect.x + 24,
        map_rect.bottom - 30,
        SMALL_FONT,
        WHITE
    )


# ============================================================
# WORLD
# ============================================================

def draw_world():

    if current_area == "MAIN LAB":

        draw_main_lab()

    elif current_area == "POWER ROOM":

        draw_power_room()

    elif current_area == "CONTROL ROOM":

        draw_control_room()

    elif current_area == "CAMPUS":

        draw_campus()

    target = None
    target_name = ""

    if current_area == "MAIN LAB":

        checks = [

            ("BATTERY", battery_rect),
            ("ELECTRICAL PANEL", panel_rect),
            ("MOTOR", motor_rect),
            ("LAB ROBOT", robot_rect),
            ("POWER ROOM", power_door),
            ("CONTROL ROOM", control_door),
            ("EXIT DOOR", exit_door)

        ]

    elif current_area == "POWER ROOM":

        checks = [

            ("BACKUP GENERATOR", generator_rect),
            ("CIRCUIT BREAKER", breaker_rect),
            ("MAIN LAB", power_back_door)

        ]

    elif current_area == "CONTROL ROOM":

        checks = [

            (
                "SCADA DIAGNOSTIC",
                scada_console_rect
            ),

            (
                "GRID STATUS MONITOR",
                grid_monitor_rect
            ),

            (
                "MASTER SHUTDOWN",
                shutdown_panel_rect
            ),

            (
                "MAIN LAB",
                control_back_door
            )

        ]

    else:

        checks = []

    for name, rect in checks:

        if near_player(
            rect,
            35
        ):

            target = rect
            target_name = name

            break

    if target is not None:

        draw_object_highlight(
            target
        )

        hint_width = 300

        hint = pygame.Rect(
            WIDTH // 2
            - hint_width // 2,
            HEIGHT - 55,
            hint_width,
            40
        )

        pygame.draw.rect(
            screen,
            (10, 15, 20),
            hint,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            CYAN,
            hint,
            2,
            border_radius=8
        )

        text = SMALL_FONT.render(
            f"[E] INTERACT — {target_name}",
            True,
            WHITE
        )

        screen.blit(
            text,
            (
                hint.centerx
                - text.get_width() // 2,
                hint.centery
                - text.get_height() // 2
            )
        )

    draw_animated_player()

    if current_area != "CAMPUS":

        draw_hud()
        draw_current_objective()


# ============================================================
# OBJECTIVES SCREEN
# ============================================================

def draw_objectives():

    screen.fill(
        (5, 12, 20)
    )

    refresh_objectives()

    draw_mission_map(
        60,
        45,
        980,
        410
    )

    index, objective_text = get_current_objective()

    active = pygame.Rect(
        80,
        485,
        940,
        70
    )

    pygame.draw.rect(
        screen,
        (10, 28, 38),
        active,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        YELLOW,
        active,
        2,
        border_radius=12
    )

    draw_text(
        "NEXT TASK",
        active.x + 18,
        active.y + 10,
        SMALL_FONT,
        YELLOW
    )

    draw_text(
        f"{index + 1:02d}. {objective_text}",
        active.x + 18,
        active.y + 34,
        FONT,
        WHITE
    )

    draw_text(
        "O / ESC = Return to mission",
        60,
        590,
        SMALL_FONT,
        GRAY
    )


# ============================================================
# INVENTORY SCREEN
# ============================================================

def draw_inventory():

    screen.fill(
        (15, 20, 25)
    )

    draw_text(
        "INVENTORY",
        60,
        50,
        TITLE_FONT,
        CYAN
    )

    if not inventory:

        draw_text(
            "Inventory is empty.",
            80,
            140,
            FONT,
            GRAY
        )

    else:

        y = 140

        for item in inventory:

            pygame.draw.rect(
                screen,
                (30, 40, 50),
                (
                    70,
                    y - 5,
                    450,
                    40
                ),
                border_radius=6
            )

            pygame.draw.rect(
                screen,
                CYAN,
                (
                    70,
                    y - 5,
                    450,
                    40
                ),
                2,
                border_radius=6
            )

            draw_text(
                "• " + item,
                85,
                y,
                FONT,
                WHITE
            )

            y += 55

    draw_text(
        "Press I or ESC to return",
        60,
        590,
        SMALL_FONT,
        GRAY
    )


# ============================================================
# PUZZLE SCREEN
# ============================================================

def draw_puzzle():

    draw_world()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 175)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    box = pygame.Rect(
        250,
        170,
        600,
        310
    )

    pygame.draw.rect(
        screen,
        (20, 25, 30),
        box,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        CYAN,
        box,
        3,
        border_radius=12
    )

    draw_text(
        "ENGINEERING PUZZLE",
        330,
        200,
        BIG_FONT,
        CYAN
    )

    draw_text(
        puzzle_question,
        300,
        265,
        FONT,
        WHITE
    )

    input_box = pygame.Rect(
        400,
        330,
        300,
        55
    )

    pygame.draw.rect(
        screen,
        BLACK,
        input_box,
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        YELLOW,
        input_box,
        2,
        border_radius=6
    )

    draw_text(
        puzzle_answer,
        input_box.x + 15,
        input_box.y + 13,
        FONT,
        WHITE
    )

    draw_text(
        "ENTER = Submit    ESC = Cancel",
        365,
        415,
        SMALL_FONT,
        GRAY
    )


# ============================================================
# MESSAGE SCREEN
# ============================================================

def draw_message():

    draw_world()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 150)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    box = pygame.Rect(
        180,
        220,
        740,
        190
    )

    pygame.draw.rect(
        screen,
        (20, 25, 30),
        box,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        CYAN,
        box,
        3,
        border_radius=12
    )

    words = message_text.split()

    lines = []

    current = ""

    for word in words:

        test = (
            current
            + " "
            + word
        ).strip()

        if FONT.size(test)[0] <= 680:

            current = test

        else:

            if current:
                lines.append(
                    current
                )

            current = word

    if current:
        lines.append(
            current
        )

    y = box.y + 35

    for line in lines:

        surface = FONT.render(
            line,
            True,
            WHITE
        )

        screen.blit(
            surface,
            (
                box.centerx
                - surface.get_width() // 2,
                y
            )
        )

        y += 32

    draw_text(
        "Press ENTER / SPACE / ESC",
        box.centerx - 125,
        box.bottom - 38,
        SMALL_FONT,
        GRAY
    )


# ============================================================
# PAUSE SCREEN
# ============================================================

def draw_pause():

    draw_world()

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 175)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    draw_center_text(
        "GAME PAUSED",
        170,
        TITLE_FONT,
        YELLOW
    )

    draw_center_text(
        "P = Resume",
        270,
        FONT,
        WHITE
    )

    draw_center_text(
        "S = Save Game",
        320,
        FONT,
        WHITE
    )

    draw_center_text(
        "O = Objectives",
        370,
        FONT,
        WHITE
    )

    draw_center_text(
        "I = Inventory",
        420,
        FONT,
        WHITE
    )

    draw_center_text(
        "ESC = Menu",
        470,
        FONT,
        WHITE
    )


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over():

    screen.fill(
        (10, 10, 15)
    )

    draw_center_text(
        "MISSION FAILED",
        190,
        TITLE_FONT,
        RED
    )

    if mission_time <= 0:

        reason = "TIME RAN OUT"

    else:

        reason = "PLAYER SYSTEM FAILURE"

    draw_center_text(
        reason,
        270,
        BIG_FONT,
        WHITE
    )

    draw_center_text(
        f"Final Score: {score}",
        340,
        FONT,
        YELLOW
    )

    draw_center_text(
        "Press R to Restart",
        430,
        FONT,
        CYAN
    )

    draw_center_text(
        "Press ESC for Menu",
        475,
        FONT,
        WHITE
    )


# ============================================================
# MISSION COMPLETE SCREEN
# ============================================================

def draw_mission_complete():

    screen.fill(
        (8, 20, 15)
    )

    draw_center_text(
        "MISSION COMPLETE!",
        130,
        TITLE_FONT,
        GREEN
    )

    draw_center_text(
        "LABORATORY SUCCESSFULLY SHUT DOWN",
        220,
        FONT,
        WHITE
    )

    draw_center_text(
        f"FINAL SCORE: {score}",
        300,
        BIG_FONT,
        YELLOW
    )

    draw_center_text(
        f"HEALTH REMAINING: {int(health)}",
        360,
        FONT,
        RED
    )

    draw_center_text(
        f"TIME REMAINING: {int(mission_time)} seconds",
        405,
        FONT,
        CYAN
    )

    draw_center_text(
        "Press R to Play Again",
        490,
        FONT,
        GREEN
    )

    draw_center_text(
        "Press ESC for Menu",
        535,
        FONT,
        WHITE
    )


# ============================================================
# MENU BACKGROUND PARTICLES
# ============================================================

menu_particles = []

for _ in range(65):

    menu_particles.append({

        "x": random.randint(
            0,
            WIDTH
        ),

        "y": random.randint(
            0,
            HEIGHT
        ),

        "speed": random.uniform(
            0.2,
            1.0
        ),

        "size": random.randint(
            1,
            3
        ),

        "phase": random.uniform(
            0,
            math.pi * 2
        )

    })


menu_time = 0


def update_menu_particles(dt):

    global menu_time

    menu_time += dt

    for particle in menu_particles:

        particle["y"] -= (
            particle["speed"]
            * 60
            * dt
        )

        particle["x"] += (
            math.sin(
                menu_time
                + particle["phase"]
            )
            * 0.15
        )

        if particle["y"] < -10:

            particle["y"] = HEIGHT + 10

            particle["x"] = random.randint(
                0,
                WIDTH
            )


def draw_menu_background():

    screen.fill(
        DARK_BLUE
    )

    pygame.draw.circle(
        screen,
        (10, 28, 45),
        (180, 330),
        270
    )

    pygame.draw.circle(
        screen,
        (9, 22, 38),
        (920, 350),
        300
    )

    # Technical grid
    for x in range(
        0,
        WIDTH,
        55
    ):

        pygame.draw.line(
            screen,
            (15, 35, 50),
            (x, 0),
            (x, HEIGHT),
            1
        )

    for y in range(
        0,
        HEIGHT,
        55
    ):

        pygame.draw.line(
            screen,
            (15, 35, 50),
            (0, y),
            (WIDTH, y),
            1
        )

    circuit_points = [

        [
            (0, 125),
            (180, 125),
            (220, 85),
            (370, 85)
        ],

        [
            (730, 80),
            (850, 80),
            (900, 125),
            (1100, 125)
        ],

        [
            (0, 535),
            (180, 535),
            (220, 575),
            (400, 575)
        ],

        [
            (720, 575),
            (870, 575),
            (920, 530),
            (1100, 530)
        ]

    ]

    for points in circuit_points:

        pygame.draw.lines(
            screen,
            (20, 75, 90),
            False,
            points,
            2
        )

        for point in points:

            pygame.draw.circle(
                screen,
                CYAN,
                point,
                3
            )

    # Moving energy pulse
    pulse_position = (
        int(
            animation_time * 100
        )
        % WIDTH
    )

    pygame.draw.circle(
        screen,
        CYAN,
        (
            pulse_position,
            125
        ),
        4
    )

    for particle in menu_particles:

        brightness = int(
            80
            + 70
            * (
                math.sin(
                    menu_time
                    + particle["phase"]
                )
                + 1
            )
            / 2
        )

        brightness = max(
            30,
            min(
                180,
                brightness
            )
        )

        pygame.draw.circle(
            screen,
            (
                30,
                brightness,
                brightness
            ),
            (
                int(
                    particle["x"]
                ),
                int(
                    particle["y"]
                )
            ),
            particle["size"]
        )


# ============================================================
# GLOW TEXT
# ============================================================

def draw_glow_text(
    text,
    center_x,
    y,
    font,
    main_color
):

    for offset, alpha in [
        (8, 30),
        (5, 50),
        (3, 80)
    ]:

        glow_font = font.render(
            text,
            True,
            main_color
        )

        glow_surface = pygame.Surface(
            glow_font.get_size(),
            pygame.SRCALPHA
        )

        glow_surface.blit(
            glow_font,
            (0, 0)
        )

        glow_surface.set_alpha(
            alpha
        )

        screen.blit(
            glow_surface,
            (
                center_x
                - glow_surface.get_width() // 2
                + offset // 2,
                y
                + offset // 2
            )
        )

    surface = font.render(
        text,
        True,
        main_color
    )

    screen.blit(
        surface,
        (
            center_x
            - surface.get_width() // 2,
            y
        )
    )


# ============================================================
# MENU BUTTON
# ============================================================

def draw_menu_button(
    rect,
    text,
    selected
):

    if selected:

        pulse = int(
            2
            * (
                math.sin(
                    animation_time * 4
                ) + 1
            )
            / 2
        )

        fill = (
            20,
            65 + pulse * 3,
            78 + pulse * 3
        )

        border = CYAN

        border_width = 3

    else:

        fill = (
            13,
            27,
            40
        )

        border = (
            55,
            85,
            100
        )

        border_width = 2

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        border,
        rect,
        border_width,
        border_radius=12
    )

    if selected:

        pygame.draw.line(
            screen,
            CYAN,
            (
                rect.left + 15,
                rect.centery
            ),
            (
                rect.left + 35,
                rect.centery
            ),
            4
        )

        pygame.draw.line(
            screen,
            CYAN,
            (
                rect.right - 35,
                rect.centery
            ),
            (
                rect.right - 15,
                rect.centery
            ),
            4
        )

    surface = FONT.render(
        text,
        True,
        WHITE
    )

    screen.blit(
        surface,
        (
            rect.centerx
            - surface.get_width() // 2,
            rect.centery
            - surface.get_height() // 2
        )
    )


# ============================================================
# CREATOR INFORMATION
# ============================================================

def draw_creator_info():

    panel = pygame.Rect(
        50,
        455,
        1000,
        150
    )

    pygame.draw.rect(
        screen,
        (5, 13, 22),
        panel,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        (35, 90, 105),
        panel,
        2,
        border_radius=18
    )

    draw_text(
        "ENGINEERING SURVIVAL",
        panel.x + 30,
        panel.y + 18,
        BIG_FONT,
        CYAN
    )

    draw_text(
        "An Engineering Adventure Game",
        panel.x + 32,
        panel.y + 58,
        SMALL_FONT,
        WHITE
    )

    draw_text(
        "Created & Developed by",
        panel.x + 560,
        panel.y + 20,
        SMALL_FONT,
        GRAY
    )

    draw_text(
        "Imam Mehedi Hasan",
        panel.x + 560,
        panel.y + 43,
        FONT,
        WHITE
    )

    draw_text(
        "Department of Electrical & Electronic Engineering",
        panel.x + 560,
        panel.y + 70,
        SMALL_FONT,
        CYAN
    )

    draw_text(
        "Jatiya Kabi Kazi Nazrul Islam University",
        panel.x + 560,
        panel.y + 94,
        SMALL_FONT,
        WHITE
    )

    draw_text(
        "© 2026",
        panel.x + 30,
        panel.y + 108,
        SMALL_FONT,
        GRAY
    )


# ============================================================
# MAIN MENU
# ============================================================

def draw_menu(dt):

    update_menu_particles(
        dt
    )

    draw_menu_background()

    main_panel = pygame.Rect(
        235,
        25,
        630,
        605
    )

    pygame.draw.rect(
        screen,
        (7, 15, 25),
        main_panel,
        border_radius=25
    )

    pygame.draw.rect(
        screen,
        (35, 85, 105),
        main_panel,
        2,
        border_radius=25
    )

    # Clean, character-free title screen. Character selection is handled
    # on the next screen so the front page represents the whole game.
    draw_center_text(
        "ADVANCED ENGINEERING MISSION SIMULATION",
        42,
        SMALL_FONT,
        CYAN
    )

    # Animated technical emblem
    emblem_center = (WIDTH // 2, 100)
    emblem_radius = 39 + int(3 * math.sin(animation_time * 3))

    pygame.draw.circle(
        screen,
        (8, 25, 38),
        emblem_center,
        emblem_radius
    )

    pygame.draw.circle(
        screen,
        CYAN,
        emblem_center,
        emblem_radius,
        3
    )

    pygame.draw.circle(
        screen, (25, 75, 95),
        emblem_center,
        28,
        2
    )

    # Engineering-style lightning/energy symbol
    bolt = [
        (emblem_center[0] - 8, emblem_center[1] - 25),
        (emblem_center[0] + 7, emblem_center[1] - 4),
        (emblem_center[0] - 2, emblem_center[1] - 4),
        (emblem_center[0] + 10, emblem_center[1] + 25),
        (emblem_center[0] - 12, emblem_center[1] + 1),
        (emblem_center[0] - 2, emblem_center[1] + 1)
    ]

    pygame.draw.polygon(
        screen,
        YELLOW,
        bolt
    )

    draw_glow_text(
        "ENGINEERING",
        WIDTH // 2,
        145,
        TITLE_FONT,
        WHITE
    )

    draw_glow_text(
        "SURVIVAL",
        WIDTH // 2,
        208,
        TITLE_FONT,
        YELLOW
    )

    draw_center_text(
        "REPAIR • ANALYZE • RESTORE • ESCAPE",
        268,
        SMALL_FONT,
        GREEN
    )

    pygame.draw.line(
        screen,
        CYAN,
        (330, 292),
        (770, 292),
        2
    )

    # Mission preview cards
    preview_items = [
        ("01", "LAB REPAIR"),
        ("02", "SCADA CONTROL"),
        ("03", "SAFE ESCAPE")
    ]

    card_width = 150
    gap = 22
    total_width = len(preview_items) * card_width + (len(preview_items) - 1) * gap
    card_x = WIDTH // 2 - total_width // 2

    for i, (number, label) in enumerate(preview_items):

        card = pygame.Rect(
            card_x + i * (card_width + gap),
            304,
            card_width,
            45
        )

        pygame.draw.rect(
            screen,
            (10, 27, 40),
            card,
            border_radius=9
        )

        pygame.draw.rect(
            screen,
            (35, 85, 105),
            card,
            1,
            border_radius=9
        )

        draw_text(
            number,
            card.x + 10,
            card.y + 12,
            SMALL_FONT,
            CYAN
        )

        label_surface = SMALL_FONT.render(
            label,
            True,
            WHITE
        )

        screen.blit(
            label_surface,
            (
                card.right - label_surface.get_width() - 10,
                card.y + 12
            )
        )

    button_width = 360
    button_height = 48

    start_x = (
        WIDTH // 2
        - button_width // 2
    )

    buttons = [

        pygame.Rect(
            start_x,
            360,
            button_width,
            42
        ),

        pygame.Rect(
            start_x,
            410,
            button_width,
            42
        ),

        pygame.Rect(
            start_x,
            460,
            button_width,
            42
        )

    ]

    labels = [
        "NEW MISSION",
        "LOAD MISSION",
        "QUIT"
    ]

    for i in range(3):

        draw_menu_button(
            buttons[i],
            labels[i],
            menu_selection == i
        )

    # Creator area
    creator = pygame.Rect(
        255,
        515,
        590,
        82
    )

    pygame.draw.rect(
        screen,
        (9, 19, 29),
        creator,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        (30, 70, 85),
        creator,
        1,
        border_radius=12
    )

    draw_center_text(
        "CREATED & DEVELOPED BY",
        523,
        SMALL_FONT,
        GRAY
    )

    draw_center_text(
        "IMAM MEHEDI HASAN",
        543,
        FONT,
        WHITE
    )

    draw_center_text(
        "EEE • JKKNIU • © 2026",
        570,
        SMALL_FONT,
        CYAN
    )

    draw_center_text(
        "↑ ↓ / W S SELECT     ENTER CONFIRM     F11 FULLSCREEN",
        615,
        SMALL_FONT,
        GRAY
    )


# ============================================================
# CHARACTER STAT BAR
# ============================================================

def draw_character_stat(
    label,
    value,
    x,
    y,
    width=170
):

    draw_text(
        label,
        x,
        y - 22,
        SMALL_FONT,
        WHITE
    )

    pygame.draw.rect(
        screen,
        (8, 15, 23),
        (
            x,
            y,
            width,
            14
        ),
        border_radius=7
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (
            x,
            y,
            int(
                width
                * value
                / 100
            ),
            14
        ),
        border_radius=7
    )

    draw_text(
        str(value),
        x + width + 8,
        y - 4,
        SMALL_FONT,
        CYAN
    )


# ============================================================
# CHARACTER SELECTION
# ============================================================

def draw_character_select():

    screen.blit(
        laboratory_img,
        (0, 0)
    )

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (4, 8, 14, 205)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    # Animated background particles
    for i in range(20):

        px = int(
            (i * 67
             + animation_time * 15)
            % WIDTH
        )

        py = int(
            100
            + (
                math.sin(
                    animation_time
                    + i
                )
                + 1
            )
            * 230
        )

        pygame.draw.circle(
            screen,
            (20, 70, 85),
            (px, py),
            2
        )

    draw_glow_text(
        "SELECT YOUR ENGINEER",
        WIDTH // 2,
        18,
        TITLE_FONT,
        CYAN
    )

    draw_center_text(
        "Choose your specialist before entering the laboratory",
        72,
        SMALL_FONT,
        WHITE
    )

    cards = [

        pygame.Rect(
            40,
            105,
            500,
            420
        ),

        pygame.Rect(
            560,
            105,
            500,
            420
        )

    ]

    portraits = [
        mehedi_portrait,
        toyasin_portrait
    ]

    for i, card in enumerate(
        cards
    ):

        selected = (
            i
            == selected_character_index
        )

        if selected:

            pulse = int(
                3
                * (
                    math.sin(
                        animation_time * 4
                    ) + 1
                )
                / 2
            )

            fill = (
                15,
                38 + pulse,
                54 + pulse
            )

            border = CYAN

        else:

            fill = (
                12,
                20,
                30
            )

            border = (
                70,
                80,
                90
            )

        pygame.draw.rect(
            screen,
            fill,
            card,
            border_radius=20
        )

        pygame.draw.rect(
            screen,
            border,
            card,
            4 if selected else 2,
            border_radius=20
        )

        if selected:

            pygame.draw.circle(
                screen,
                CYAN,
                (
                    card.left + 18,
                    card.top + 18
                ),
                5
            )

            pygame.draw.circle(
                screen,
                CYAN,
                (
                    card.right - 18,
                    card.top + 18
                ),
                5
            )

        portrait = portraits[i]

        portrait_x = (
            card.centerx
            - portrait.get_width() // 2
        )

        portrait_y = (
            card.y + 5
            + int(
                math.sin(
                    animation_time * 2
                    + i
                )
                * 2
            )
        )

        screen.blit(
            portrait,
            (
                portrait_x,
                portrait_y
            )
        )

        name = characters[i]["name"]

        name_color = (
            CYAN
            if i == 0
            else ORANGE
        )

        name_surface = BIG_FONT.render(
            name,
            True,
            name_color
        )

        screen.blit(
            name_surface,
            (
                card.centerx
                - name_surface.get_width() // 2,
                card.y + 275
            )
        )

        role = characters[i]["role"]

        role_surface = SMALL_FONT.render(
            role,
            True,
            WHITE
        )

        screen.blit(
            role_surface,
            (
                card.centerx
                - role_surface.get_width() // 2,
                card.y + 318
            )
        )

        specialty_parts = [
            part.strip()
            for part in characters[i][
                "specialty"
            ].split("|")
        ]

        first_specialty = " • ".join(
            specialty_parts[:2]
        )

        second_specialty = ""

        if len(specialty_parts) > 2:

            second_specialty = (
                " • "
                + specialty_parts[2]
            )

        specialty_surface = SMALL_FONT.render(
            first_specialty,
            True,
            YELLOW
        )

        screen.blit(
            specialty_surface,
            (
                card.centerx
                - specialty_surface.get_width() // 2,
                card.y + 350
            )
        )

        if second_specialty:

            specialty_surface_2 = SMALL_FONT.render(
                second_specialty,
                True,
                YELLOW
            )

            screen.blit(
                specialty_surface_2,
                (
                    card.centerx
                    - specialty_surface_2.get_width() // 2,
                    card.y + 374
                )
            )

        if selected:

            tag = pygame.Rect(
                card.centerx - 85,
                card.bottom - 38,
                170,
                28
            )

            pygame.draw.rect(
                screen,
                CYAN,
                tag,
                border_radius=7
            )

            selected_text = SMALL_FONT.render(
                "SELECTED ENGINEER",
                True,
                BLACK
            )

            screen.blit(
                selected_text,
                (
                    tag.centerx
                    - selected_text.get_width() // 2,
                    tag.y + 5
                )
            )

    info = characters[
        selected_character_index
    ]

    detail_box = pygame.Rect(
        120,
        540,
        860,
        90
    )

    pygame.draw.rect(
        screen,
        (8, 17, 27),
        detail_box,
        border_radius=14
    )

    pygame.draw.rect(
        screen,
        CYAN,
        detail_box,
        2,
        border_radius=14
    )

    description = info[
        "description"
    ]

    description_surface = SMALL_FONT.render(
        description,
        True,
        WHITE
    )

    screen.blit(
        description_surface,
        (
            detail_box.centerx
            - description_surface.get_width() // 2,
            detail_box.y + 8
        )
    )

    stats = [

        (
            "POWER",
            info["power"]
        ),

        (
            "REPAIR",
            info["repair"]
        ),

        (
            "ANALYSIS",
            info["analysis"]
        ),

        (
            "FIELD",
            info["field"]
        )

    ]

    stat_x = (
        detail_box.x + 55
    )

    for label, value in stats:

        draw_character_stat(
            label,
            value,
            stat_x,
            detail_box.y + 58,
            145
        )

        stat_x += 190

    controls = (
        "A / D or ← / → CHANGE ENGINEER     "
        "ENTER START MISSION     "
        "ESC BACK"
    )

    controls_surface = SMALL_FONT.render(
        controls,
        True,
        GREEN
    )

    screen.blit(
        controls_surface,
        (
            WIDTH // 2
            - controls_surface.get_width() // 2,
            632
        )
    )


# ============================================================
# FULLSCREEN TOGGLE
# ============================================================

def toggle_fullscreen():

    global screen
    global fullscreen

    fullscreen = not fullscreen

    try:

        if fullscreen:

            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.FULLSCREEN
                | pygame.SCALED
            )

        else:

            screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.SCALED
            )

    except pygame.error:

        fullscreen = not fullscreen


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    dt = clock.tick(
        FPS
    ) / 1000.0

    animation_time += dt
    campus_animation_time += dt

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        # ====================================================
        # FULLSCREEN
        # ====================================================

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_F11:

                toggle_fullscreen()

                continue

        # ====================================================
        # MOUSE
        # ====================================================

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                # ------------------------------------------------
                # MENU MOUSE
                # ------------------------------------------------

                if game_state == MENU:

                    button_width = 360

                    start_x = (
                        WIDTH // 2
                        - button_width // 2
                    )

                    menu_buttons = [

                        pygame.Rect(
                            start_x,
                            330,
                            button_width,
                            48
                        ),

                        pygame.Rect(
                            start_x,
                            388,
                            button_width,
                            48
                        ),

                        pygame.Rect(
                            start_x,
                            446,
                            button_width,
                            48
                        )

                    ]

                    for i, button in enumerate(
                        menu_buttons
                    ):

                        if button.collidepoint(
                            event.pos
                        ):

                            menu_selection = i

                            play_sound(
                                menu_sound
                            )

                            if i == 0:

                                selected_character_index = 0

                                game_state = (
                                    CHARACTER_SELECT
                                )

                            elif i == 1:

                                load_game()

                            elif i == 2:

                                running = False

                # ------------------------------------------------
                # CHARACTER CARD MOUSE
                # ------------------------------------------------

                elif game_state == CHARACTER_SELECT:

                    character_cards = [

                        pygame.Rect(
                            40,
                            105,
                            500,
                            420
                        ),

                        pygame.Rect(
                            560,
                            105,
                            500,
                            420
                        )

                    ]

                    for i, card in enumerate(
                        character_cards
                    ):

                        if card.collidepoint(
                            event.pos
                        ):

                            selected_character_index = i

                            play_sound(
                                menu_sound
                            )

        # ====================================================
        # KEYBOARD
        # ====================================================

        if event.type == pygame.KEYDOWN:

            # =================================================
            # MENU
            # =================================================

            if game_state == MENU:

                if event.key in (
                    pygame.K_DOWN,
                    pygame.K_s
                ):

                    menu_selection = (
                        menu_selection + 1
                    ) % 3

                    play_sound(
                        menu_sound
                    )

                elif event.key in (
                    pygame.K_UP,
                    pygame.K_w
                ):

                    menu_selection = (
                        menu_selection - 1
                    ) % 3

                    play_sound(
                        menu_sound
                    )

                elif event.key == pygame.K_RETURN:

                    play_sound(
                        menu_sound
                    )

                    if menu_selection == 0:

                        selected_character_index = 0

                        game_state = (
                            CHARACTER_SELECT
                        )

                    elif menu_selection == 1:

                        load_game()

                    elif menu_selection == 2:

                        running = False

                elif event.key == pygame.K_ESCAPE:

                    running = False

            # =================================================
            # CHARACTER SELECT
            # =================================================

            elif game_state == CHARACTER_SELECT:

                if event.key in (
                    pygame.K_RIGHT,
                    pygame.K_d
                ):

                    selected_character_index = (
                        selected_character_index + 1
                    ) % len(characters)

                    play_sound(
                        menu_sound
                    )

                elif event.key in (
                    pygame.K_LEFT,
                    pygame.K_a
                ):

                    selected_character_index = (
                        selected_character_index - 1
                    ) % len(characters)

                    play_sound(
                        menu_sound
                    )

                elif event.key == pygame.K_RETURN:

                    apply_selected_character()

                    reset_game()

                    game_state = EXPLORE

                    # Start the laboratory music from the beginning.
                    start_background_music()

                    play_sound(
                        menu_sound
                    )

                elif event.key == pygame.K_ESCAPE:

                    stop_background_music()
                    game_state = MENU

            # =================================================
            # EXPLORE
            # =================================================

            elif game_state == EXPLORE:

                if event.key == pygame.K_e:

                    interact()

                elif event.key == pygame.K_i:

                    game_state = INVENTORY

                elif event.key == pygame.K_o:

                    game_state = OBJECTIVES

                elif event.key == pygame.K_p:

                    game_state = PAUSE

                elif event.key == pygame.K_s:

                    save_game()

                elif event.key == pygame.K_ESCAPE:

                    stop_background_music()
                    game_state = MENU

            # =================================================
            # PUZZLE
            # =================================================

            elif game_state == PUZZLE:

                if event.key == pygame.K_ESCAPE:

                    game_state = EXPLORE

                elif event.key == pygame.K_RETURN:

                    solve_puzzle()

                elif event.key == pygame.K_BACKSPACE:

                    puzzle_answer = (
                        puzzle_answer[:-1]
                    )

                else:

                    if (
                        event.unicode.isdigit()
                        or event.unicode in ".-"
                    ):

                        puzzle_answer += (
                            event.unicode
                        )

            # =================================================
            # MESSAGE
            # =================================================

            elif game_state == MESSAGE:

                if event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                    pygame.K_ESCAPE
                ):

                    game_state = previous_state

                    message_timer = 0

            # =================================================
            # INVENTORY
            # =================================================

            elif game_state == INVENTORY:

                if event.key in (
                    pygame.K_i,
                    pygame.K_ESCAPE
                ):

                    game_state = EXPLORE

            # =================================================
            # OBJECTIVES
            # =================================================

            elif game_state == OBJECTIVES:

                if event.key in (
                    pygame.K_o,
                    pygame.K_ESCAPE
                ):

                    game_state = EXPLORE

            # =================================================
            # PAUSE
            # =================================================

            elif game_state == PAUSE:

                if event.key == pygame.K_p:

                    game_state = EXPLORE

                elif event.key == pygame.K_s:

                    save_game()

                elif event.key == pygame.K_o:

                    game_state = OBJECTIVES

                elif event.key == pygame.K_i:

                    game_state = INVENTORY

                elif event.key == pygame.K_ESCAPE:

                    game_state = MENU

            # =================================================
            # GAME OVER
            # =================================================

            elif game_state == GAME_OVER:

                if event.key == pygame.K_r:

                    stop_background_music()
                    game_state = CHARACTER_SELECT

                elif event.key == pygame.K_ESCAPE:

                    stop_background_music()
                    game_state = MENU

            # =================================================
            # MISSION COMPLETE
            # =================================================

            elif game_state == MISSION_COMPLETE:

                if event.key == pygame.K_r:

                    stop_all_sounds()
                    game_state = CHARACTER_SELECT

                elif event.key == pygame.K_ESCAPE:

                    stop_all_sounds()
                    game_state = MENU

    # ========================================================
    # GAME UPDATE
    # ========================================================

    if game_state == EXPLORE:

        move_player()

        # ====================================================
        # CAMPUS FREE ROAM
        # ====================================================

        if current_area == "CAMPUS":

            # Peaceful campus.
            # No timer, drone, hazard, temperature damage
            # or warning sounds.
            # Peaceful campus: only flying birds are animated.
            update_campus_birds()

        else:

            update_drone()

            update_hazards()

            update_temperature()

            mission_time -= dt

            if mission_time <= 0:

                mission_time = 0

                stop_all_sounds()

                game_state = GAME_OVER

            if health <= 0:

                health = 0

                stop_all_sounds()

                game_state = GAME_OVER

    # ========================================================
    # MESSAGE TIMER
    # ========================================================

    if game_state == MESSAGE:

        message_timer -= 1

        if message_timer <= 0:

            game_state = previous_state

    # ========================================================
    # DRAW
    # ========================================================

    if game_state == MENU:

        draw_menu(
            dt
        )

    elif game_state == CHARACTER_SELECT:

        draw_character_select()

    elif game_state == EXPLORE:

        draw_world()

    elif game_state == PUZZLE:

        draw_puzzle()

    elif game_state == MESSAGE:

        draw_message()

    elif game_state == INVENTORY:

        draw_inventory()

    elif game_state == OBJECTIVES:

        draw_objectives()

    elif game_state == PAUSE:

        draw_pause()

    elif game_state == GAME_OVER:

        draw_game_over()

    elif game_state == MISSION_COMPLETE:

        draw_mission_complete()

    pygame.display.flip()


# ============================================================
# QUIT
# ============================================================

stop_all_sounds()

pygame.quit()