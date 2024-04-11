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
    hit_objects_list.append(HitObject(position, time, type, hitSound, ApproachRate, CircleSize, addition))
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

def handle_mouse_click(event, cursor_instance, hit_objects_list, current_time):
    if event.button == 1:  # Check if left mouse button clicked
        mouse_pos = pygame.mouse.get_pos()
        # Iterate through hit objects and check for circular hit detection
        for hit_object in hit_objects_list:
            # Calculate the distance between cursor position and hit object center
            distance_to_hit_object = math.sqrt((hit_object.position[0] - mouse_pos[0])**2 + (hit_object.position[1] - mouse_pos[1])**2)
            # Check if the distance is less than or equal to the hit object radius
            if distance_to_hit_object <= hit_object.circle_size:
                hit_object.hit(hit_time=current_time)  # Call hit method if hit detected


def check_hit_circle(hit_object, event):
    # Check if the mouse click is within the hit circle
    return distance(event.pos, hit_object.position) <= cir

def main_game_logic(hit_objects_list, event):

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
    pass

def main():
    clock = pygame.time.Clock()
    running = False  # Start with menu loop
    music_playing = False
    current_time = 0  # Initialize current_time
    start_time = 0  # Variable to store the time when the game starts running
    
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
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Check if left mouse button clicked
                        # Check if mouse click is within the bounding rectangle of any song text
                        for rect_top_left, song in song_rects.items():
                            if pygame.Rect(rect_top_left, (100, 30)).collidepoint(event.pos):  # Use 100x30 as width and height of text
                                print("Text clicked:", song)
                                running = True  # Start the game loop for the selected song
                                start_time = pygame.time.get_ticks()  # Record the start time

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

                elif event.type == pygame.MOUSEBUTTONDOWN:
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

