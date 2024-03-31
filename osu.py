import pygame
from classes import *
import os
import zipfile

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
general, editor, metadata, difficulty, events, timing_points, hit_objects_data = parse_osu_file('beatmap.osz')

# Initialize Pygame
pygame.init()

# Set the size of the osu! playfield
osu_width, osu_height = 512, 384

# Set the size of the window (this can be any size)
window_width, window_height = 1024, 768

# Create a surface for the osu! playfield
osu_surface = pygame.Surface((osu_width, osu_height))

# Create the window
window = pygame.display.set_mode((window_width, window_height))

# Load the audio file
pygame.mixer.music.load(os.path.join('beatmaps', general['AudioFilename']))

# initial cursor position
cursor_position = (400, 300)  

#initiate cursor
cursor_instance = Cursor(cursor_position)


# Start playing the music
pygame.mixer.music.play()

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
    hit_objects_list.append(HitObject(position, time, type, hitSound, addition))
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

def handle_mouse_click(event, cursor_instance, hit_objects_list):
    if event.button == 1:  # Check if left mouse button clicked
        mouse_pos = pygame.mouse.get_pos()
        # Use spritecollide to detect collisions between mouse position and hit objects
        clicked_hit_objects = [hit_obj for hit_obj in hit_objects_list if cursor_instance.rect.colliderect(hit_obj.rect)]
        for hit_object in clicked_hit_objects:
            hit_object.hit()

def check_hit_circle(hit_object, event):
    # Check if the mouse click is within the hit circle
    return distance(event.pos, hit_object.position) <= 10

def main_game_logic(hit_objects_list, event):
    for hit_object in hit_objects_list:
        if hit_object.visible:
            if hit_object.type == 'circle':
                print("hit a circle")
            elif hit_object.type == 'slider':
                print("hit a slider")
            elif hit_object.type == 'spinner':
                print("why are you hitting a spinner?")


def main():
    clock = pygame.time.Clock()
    running = False  # Start with menu loop
    
    hit_circle_texture, slider_texture, spinner_texture = load_textures()

    while True:
        if not running:  # Display menu if not running
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

        else:  # Game loop
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    handle_mouse_click(event, cursor_instance, hit_objects_list)
                    main_game_logic(hit_objects_list, event)

            current_time = pygame.time.get_ticks()

            #update cursor position
            new_cursor_position = pygame.mouse.get_pos()
            cursor_instance.update_position(new_cursor_position)

            # Draw the background
            window.fill((0, 0, 0))

            # do hit objects
            for hit_object in hit_objects_list:
                hit_object.update(current_time)
                hit_object.draw(window)
            
            # display current time in ms
            current_time_str = "Current Time: {} ms".format(current_time)
            draw_text(current_time_str, font, TEXT_COL, 50, 50)


            # Update the display
            pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    main()

pygame.quit()

