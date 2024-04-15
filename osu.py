import pygame
from classes import *
import os
import zipfile
import math

pygame.init()

#define fonts
font = pygame.font.SysFont("arialblack", 20)

#define colours
TEXT_COL = (255, 255, 255)

def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  img_rect = img.get_rect(topleft=(x, y))
  window.blit(img, (x, y))
  return img_rect

def load_textures():
    # Load hit circle texture
    hit_circle_texture = pygame.image.load("assets/hitcircle.png").convert_alpha()
    # Load slider texture
    slider_texture = pygame.image.load("assets/slider.png").convert_alpha()
    # Load spinner texture
    spinner_texture = pygame.image.load("assets/spinner.png").convert_alpha()
    
    return hit_circle_texture, slider_texture, spinner_texture



def parse_osu_file(filename):
    # Check if the file is a .osz file
    if filename.endswith('.osz'):
        # Extract the .osz file
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall('beatmaps')

        # Find the first .osu file in the extracted files
        for root, dirs, files in os.walk('beatmaps'):
            for file in files:
                if file.endswith('.osu'):
                    filename = os.path.join(root, file)
                    break

    with open(filename, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file.readlines()]

    # Initialize dictionaries to hold the data from each section
    general = {}
    editor = {}
    metadata = {}
    difficulty = {}
    events = []
    timing_points = []
    hit_objects = []

    # A dictionary to map section names to dictionaries
    sections = {
        '[General]': general,
        '[Editor]': editor,
        '[Metadata]': metadata,
        '[Difficulty]': difficulty,
        '[Events]': events,
        '[TimingPoints]': timing_points,
        '[HitObjects]': hit_objects
    }

    # Variable to hold the current section name
    section_name = ''

    for line in lines:
        if line.startswith('['):  # This line is a section name
            section_name = line
        elif line:  # This line is not blank
            # This line is part of a section
            section = sections.get(section_name)
            if section is not None:
                if isinstance(section, list):
                    # For list sections, just append the line
                    section.append(line)
                else:
                    # For dict sections, split the line into key and value
                    key, value = line.split(':', 1)
                    section[key.strip()] = value.strip()

    # Return the parsed data
    return general, editor, metadata, difficulty, events, timing_points, hit_objects

# Parse the .osu file
general, editor, metadata, difficulty_data, events, timing_points, hit_objects_data = parse_osu_file('beatmap.osz')

# Initialize Pygame
pygame.init()

# Set the size of the osu! playfield
OSU_WIDTH, OSU_HEIGHT = 512, 384

# Set the vertical shift of the osu! playfield
VERTICAL_SHIFT = 8

# Set the size of the window (this can be any size)
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600

# Create a surface for the osu! playfield
osu_surface = pygame.Surface((OSU_WIDTH, OSU_HEIGHT))

# Create the window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

# initialize playfield
#playfield_instance = Playfield()

# Load the audio file
pygame.mixer.music.load(os.path.join('beatmaps', general['AudioFilename']))

# initial cursor position
cursor_position = (400, 300)  

#initiate cursor
cursor_instance = Cursor(cursor_position)

#create current hit objects list
current_hit_objects = []

# Extract variables from difficulty_data
HPDrainRate = int(difficulty_data['HPDrainRate'])
CircleSize = int(difficulty_data['CircleSize'])
OverallDifficulty = int(difficulty_data['OverallDifficulty'])
ApproachRate = int(difficulty_data['ApproachRate'])
SliderMultiplier = float(difficulty_data['SliderMultiplier'])
SliderTickRate = int(difficulty_data['SliderTickRate'])
print(difficulty_data)

# Create a list to hold the hit objects
hit_objects_list = []
for line in hit_objects_data:
    components = line.split(',')
    x = int(components[0])
    y = int(components[1])
    time = int(components[2])
    type = int(components[3])
    hitSound = int(components[4])
    addition = components[5:]  # The rest of the components are specific to the type of hit object
    position = (x, y)
    hit_objects_list.append(HitObject(position, time, type, hitSound, ApproachRate, CircleSize, window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT, addition))
    print(line)
    

def display_menu(window):
    window.fill((0, 0, 0))
    
    draw_text("Select a Song:", font, TEXT_COL, 50, 50)

    songs = [file for file in os.listdir('beatmaps') if file.endswith('.osu')]

    song_rects = {}  # Dictionary to store bounding rectangles of song texts

    menu_y = 100
    for index, song in enumerate(songs):
        text_rect = draw_text(song, font, TEXT_COL, 50, menu_y)
        song_rects[text_rect.topleft] = song  # Store the top-left corner of the bounding rectangle and corresponding song text
        menu_y += 40

    pygame.display.flip() 
    return song_rects

def display_keybindings_menu(window):
    window.fill((0, 0, 0))
    
    draw_text("Select a Keybinding:", font, TEXT_COL, 50, 50)

    keybindings = list(settings.keys())  # Get a list of all keybindings

    keybinding_rects = {}  # Dictionary to store bounding rectangles of keybinding texts

    menu_y = 100
    for index, keybinding in enumerate(settings):
        text_rect = draw_text(keybinding, font, TEXT_COL, 50, menu_y)
        keybinding_rects[text_rect.topleft] = keybinding  # Store the top-left corner of the bounding rectangle and corresponding keybinding text
        menu_y += 40

    pygame.display.flip() 
    return keybinding_rects


def handle_mouse_click(event, cursor_instance, hit_objects_list, current_time):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == settings['left_click'] or event.button == settings['right_click']:  # Check if left mouse button clicked
            mouse_pos = pygame.mouse.get_pos()
            # Iterate through hit objects and check for circular hit detection
            for hit_object in hit_objects_list:
                if hit_object.visible:
                    # Calculate the distance between the cursor and the center of the hit object
                    distance = check_hit_circle(hit_object)
                    # Check if the distance is less than or equal to the hit object radius
                    if distance <= hit_object.circle_size:
                        hit_object.hit(hit_time=current_time)
                    else:
                        print(distance)
    elif event.type == pygame.KEYDOWN:
        if event.key == settings['left_click'] or event.key == settings['right_click']:
            mouse_pos = pygame.mouse.get_pos()
            # Iterate through hit objects and check for circular hit detection
            for hit_object in hit_objects_list:
                if hit_object.visible:
                    # Calculate the distance between the cursor and the center of the hit object
                    distance = check_hit_circle(hit_object)
                    # Check if the distance is less than or equal to the hit object radius
                    if distance <= hit_object.circle_size:
                        hit_object.hit(hit_time=current_time)
                    else:
                        print(distance)
            


def check_hit_circle(hit_object):
    # Check if the mouse click is within the hit circle
    distance_from_center = distance(pygame.mouse.get_pos(), hit_object.adjusted_position)
    return distance_from_center

def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def main_game_logic(hit_objects_list, event):
    pass
    ## Iterate through hit objects
    #for hit_object in hit_objects_list:
    #    if hit_object.visible:
    #        current_hit_objects.append(hit_object)
    #        #if hit_object.type == 'circle':
    #        #    print("Hit a circle")
    #        #elif hit_object.type == 'slider':
    #        #    print("Hit a slider")
    #        #elif hit_object.type == 'spinner':
    #        #    print("Why are you hitting a spinner?")
    #    else:
    #        current_hit_objects.remove(hit_object)  # Remove the hit object from the current objects

def recalculate_adjusted_position():
    print("rezized the window")
    for hit_object in hit_objects_list:
        hit_object.recalculate_adjusted_position(window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT)

# Initialize settings with default keybindings
settings = {
    'left_click': pygame.MOUSEBUTTONDOWN,
    'right_click': pygame.MOUSEBUTTONDOWN,
}

def change_keybinding(key_binding):
    print(f"Press a key to set the new keybinding for {key_binding}")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                settings[key_binding] = event.key  # Update the keybinding in the settings
                print(f"Keybinding for {key_binding} has been changed to {event.key}")
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                settings[key_binding] = event.button
                print(f"Keybinding for {key_binding} has been changed to {event.button}")
                return


def main():
    clock = pygame.time.Clock()
    running = False  # Start with menu loop
    music_playing = False
    current_time = 0  # Initialize current_time
    start_time = 0  # Variable to store the time when the game starts running
    exit_settings = False
    
    hit_circle_texture, slider_texture, spinner_texture = load_textures()

    while True:
        if not running:  # Display menu if not running
            current_time = 0
            song_rects = display_menu(window)  # Get bounding rectangles and corresponding song texts
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return  # Exit program if window closed
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return  # Exit program if ESC pressed
                    elif event.key == pygame.K_RETURN:  # Start the game loop when Enter is pressed
                        running = True
                    elif event.key == pygame.K_o:
                        while True:
                            keybinding_rects = display_keybindings_menu(window)  # Display the keybindings menu
                            for settings_event in pygame.event.get():  # Fetch new events
                                if settings_event.type == pygame.KEYDOWN:
                                    if settings_event.key == pygame.K_ESCAPE:
                                        exit_settings = True  # Set the flag to True when you want to exit
                                        break
                                elif settings_event.type == pygame.MOUSEBUTTONDOWN:
                                    if settings_event.button == 1:  # Check if left mouse button clicked
                                        # Check if mouse click is within the bounding rectangle of any keybinding text
                                        for rect_top_left, keybinding in keybinding_rects.items():
                                            if pygame.Rect(rect_top_left, (100, 30)).collidepoint(settings_event.pos):  # Use 100x30 as width and height of text
                                                print("Keybinding selected:", keybinding)
                                                change_keybinding(keybinding)  # Change the selected keybinding
                            if exit_settings:  # Check the flag after the inner loop
                                break  # If the flag is True, break the outer loop

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Check if left mouse button clicked
                        # Check if mouse click is within the bounding rectangle of any song text
                        for rect_top_left, song in song_rects.items():
                            if pygame.Rect(rect_top_left, (100, 30)).collidepoint(event.pos):  # Use 100x30 as width and height of text
                                print("Text clicked:", song)
                                running = True  # Start the game loop for the selected song
                                start_time = pygame.time.get_ticks()  # Record the start time
                elif event.type == pygame.VIDEORESIZE:
                    recalculate_adjusted_position()

        else:  # Game loop

            if not music_playing:
                # Start playing the music
                pygame.mixer.music.play()
                music_playing = True
            
            if current_time and not running:
                current_time = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == settings['right_click'] or settings['left_click']:
                    handle_mouse_click(event, cursor_instance, hit_objects_list, current_time)
                    main_game_logic(hit_objects_list, event)

            current_time = pygame.time.get_ticks() - start_time 

            #update cursor position
            new_cursor_position = pygame.mouse.get_pos()
            cursor_instance.update_position(new_cursor_position)

            # Rendering
            window.fill((0, 0, 0))  # Clear the screen

            # do hit objects
            for hit_object in hit_objects_list:
                hit_object.update(current_time)
                hit_object.draw(window, OSU_HEIGHT, OSU_HEIGHT, VERTICAL_SHIFT)
            
            # display current time in ms
            current_time_str = "Current Time: {} ms".format(current_time)
            draw_text(current_time_str, font, TEXT_COL, 50, 50)

            # Update the display
            pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    main()

pygame.quit()

