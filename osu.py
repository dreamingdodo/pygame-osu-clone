import pygame
from classes import *
import os
import zipfile
import math
import bisect
import requests
from bs4 import BeautifulSoup
import shutil

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

def get_beatmap_info():
    url = "https://beatconnect.io"
    response = requests.get(url)
    
    beatmap_info = {}  # Dictionary to store names and links
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find all elements containing the names and links
        elements = soup.find_all("div", class_="gallery-item")
        
        # Extract names and links from the elements and store in dictionary
        for element in elements:
            name = element.find("span", class_="title").text.strip()
            link = element.find("a", class_="download").get("href")
            beatmap_info[name] = link
        
        return beatmap_info
    else:
        print("Failed to retrieve the website.", response.status_code)

def generate_download_link(link):
    url = "https://beatconnect.io"
    full_link = url + link
    return full_link

def download_and_import_file(url):
    # Function to download a file from a URL and import it
    
    def rename_file(old_path, new_name, target_dir):
        # Rename a file
        try:
            new_path = os.path.join(target_dir, new_name)
            os.rename(old_path, new_path)
            print(f"File '{old_path}' renamed to '{new_path}'.")
            return new_path
        except FileNotFoundError:
            print(f"File '{old_path}' not found.")
            return None

    def delete_folder(folder_path):
        # Delete a folder
        try:
            shutil.rmtree(folder_path)
            print(f"Folder '{folder_path}' deleted successfully.")
        except FileNotFoundError:
            print(f"Folder '{folder_path}' not found.")

    # Get directory of the script
    target_dir = os.path.dirname(os.path.abspath(__file__))

    # Download the file
    response = requests.get(url)
    if response.status_code == 200:
        # Save the file
        file_path = os.path.join(target_dir, "beatmap.osz")
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"File downloaded successfully to '{file_path}'.")

        # Additional logic here to import the file into the game
        # For now, let's just print the file path
        print(f"File imported: {file_path}")

        # Delete folder
        folder_to_delete = os.path.join(target_dir, "beatmaps")
        delete_folder(folder_to_delete)
    else:
        print(f"Failed to download file from {url}. Status code: {response.status_code}")

    # Restart
    restart_program()


def get_bit(value, bit_index):
    mask = 1 << bit_index  # Create a mask for the bit index
    return (value & mask) >> bit_index  # Use bitwise AND to get the bit at the index, then shift it back to the right

def load_textures():
    # Load hit circle texture
    hit_circle_texture = pygame.image.load("assets/hitcircle.png").convert_alpha()
    # Load slider texture
    slider_texture = pygame.image.load("assets/slider.png").convert_alpha()
    # Load spinner texture
    spinner_texture = pygame.image.load("assets/spinner.png").convert_alpha()
    
    return hit_circle_texture, slider_texture, spinner_texture

def get_current_score():
    total = sum(hit_object.score for hit_object in hit_objects_list)
    return str(total)

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

# Get API key from beatconnect.IO
#api_key = get_api_key()

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

# calc center of screen
#CENTER = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

#initiate cursor
cursor_instance = Cursor(cursor_position)

#create current hit objects list
current_hit_objects = []

# Spinner list
spinner_list = []

# Create spinner list that holds the respective hit_objects
hit_spinner_list = []

# Slider list
slider_list = []

# Create slider list that holds the respective hit_objects
hit_slider_list = []

# Make the dir's work on both windows and linux
assets_dir = "assets"

# Load the sounds
hit_sound = pygame.mixer.Sound(os.path.join(assets_dir, 'drum-hitnormal.wav'))
bye_sound = pygame.mixer.Sound(os.path.join(assets_dir, 'seeya.ogg'))
combo_break_sound = pygame.mixer.Sound(os.path.join(assets_dir, 'combobreak.wav'))

bye_length_seconds = bye_sound.get_length()


# Extract variables from difficulty_data
HPDrainRate = float(difficulty_data['HPDrainRate'])
CircleSize = float(difficulty_data['CircleSize'])
OverallDifficulty = float(difficulty_data['OverallDifficulty'])
ApproachRate = float(difficulty_data['ApproachRate'])
SliderMultiplier = float(difficulty_data['SliderMultiplier'])
SliderTickRate = int(difficulty_data['SliderTickRate'])
print(difficulty_data)

# Extract a list of timing_points
timing_points_list = []
for line in timing_points:
    components = line.split(',')
    time = float(components[0])
    beatLength = components[1]
    meter = components[2]
    sampleSet = components[3]
    sampleIndex = components[4]
    volume = components[5]
    uninherited = components[6]
    effects = components[7]
    timing_points_list.append(TimingPoints(time, beatLength, meter, sampleSet, sampleIndex, volume, uninherited, effects))
    print("timing point line: ",line)

# Sort the list of the timing points according to self.time
timing_points_list.sort(key=lambda TimingPoints: TimingPoints.time)

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

def object_comparator(HitObject):
    return HitObject.time

# sort a list of hit objects according to their time
sorted_hit_object_list = sorted(hit_objects_list, key=object_comparator)

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

def display_names_menu(window, names, scroll_offset):
    window.fill((0, 0, 0))
    
    draw_text("Select a Name:", font, TEXT_COL, 50, 50)

    name_rects = {}  # Dictionary to store bounding rectangles of name texts

    visible_names = names[scroll_offset:scroll_offset + 10]  # Display up to 10 names at a time

    menu_y = 100
    for index, name in enumerate(visible_names):
        text_rect = draw_text(name, font, TEXT_COL, 50, menu_y)
        name_rects[text_rect.topleft] = name  # Store the top-left corner of the bounding rectangle and corresponding name text
        menu_y += 40

    pygame.display.flip() 
    return name_rects


def handle_mouse_click(event, cursor_instance, hit_objects_list, current_time, OverallDifficulty, hit_sound, sorted_hit_object_list, hit_something):
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
                        hit_object.hit(current_time, OverallDifficulty, sorted_hit_object_list, hit_something, hit_sound)
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
                        hit_object.hit(hit_time=current_time, OverallDifficulty = OverallDifficulty, sorted_hit_object_list= sorted_hit_object_list, hit_something= hit_something, hit_sound= hit_sound)
                    else:
                        print(distance)
            
def restart_program():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def check_hit_circle(hit_object):
    # Check if the mouse click is within the hit circle
    distance_from_center = distance(pygame.mouse.get_pos(), hit_object.adjusted_position)
    return distance_from_center

# Function to calculate angle
def calculate_angle(CENTER, current, initial):
    d1 = (initial[0]-center[0], initial[1]-center[1])
    d2 = (current[0]-center[0], current[1]-center[1])
    return math.atan2(d1[0]*d2[1] - d1[1]*d2[0], d1[0]*d2[0] + d1[1]*d2[1])

def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def main_game_logic(hit_objects_list, event, current_time, initial_pos, dt, current_timing_point, CENTER):
    for hit_object in hit_objects_list:
        if hit_object.visible:
            for bit_index in range(8):
                bit_value = get_bit(hit_object.type, bit_index)
                if bit_value == 1:
                    if bit_index == 0: #hit circle
                        pass
                        #already done i think
                    elif bit_index == 1: #slider
                        if not hit_object.has_slider:
                            # Get the curve points and curve type
                            curve_points_curve_type = hit_object.addition[0]
                            parts = curve_points_curve_type.split('|')
                            curve_type = parts[0]
                            curve_points = [tuple(map(int, part.split(':'))) for part in parts[1:]]
                            # Get all other attributes
                            slides = hit_object.addition[1] # Repeat count plus one
                            length = hit_object.addition[2]
                            edge_sounds = hit_object.addition[3] if len(hit_object.addition) > 3 else "None"
                            edge_sets = hit_object.addition[4].split('|') if len(hit_object.addition) > 4 else ["0:0:0:0:"]
                            print("curve type:", curve_type, "slides:", slides, "length:", length, "edge sounds:", edge_sounds, "edge sets:", edge_sets,"curve points:", curve_points)
                            slider = Slider(hit_object, curve_type, slides, length, edge_sounds, edge_sets, curve_points)
                            hit_object.has_slider = True
                            hit_slider_list.append(hit_object)
                            slider_list.append(slider)
                            print("added slider to list")
                    elif bit_index == 2: #new combo
                        pass
                    elif bit_index == 3: #spinner
                        if not hit_object.has_spinner:
                            endtime = hit_object.addition[0]
                            print("endtime: ", endtime)
                            if hit_object.addition[1:]:
                                hitsample = hit_object.addition[1]
                            spinner = Spinner(hit_object, pygame.mouse.get_pos(), pygame.mouse.get_pos(), endtime)
                            hit_object.has_spinner = True
                            hit_spinner_list.append(hit_object)
                            spinner_list.append(spinner)
                            print("added spinner to list")
                    elif bit_index == 4: #color hax
                        pass
                    elif bit_index == 5: #color hax
                        pass
                    elif bit_index == 6: #color hax
                        pass
                    elif bit_index == 7: #mania hold
                        pass

    for spinner in spinner_list:
        #print("Spinner Time: {spinner.time}, End Time: {spinner.endtime}, Current Time: {current_time}")
        if spinner.time <= current_time:
            if int(spinner.endtime) >= current_time:
                pygame.draw.circle(window, (255, 255, 255), CENTER, 50)
                if spinner.initial_pos == (0,0):
                    print("got new pos for initial")
                    spinner.initial_pos = pygame.mouse.get_pos()
                current_pos = pygame.mouse.get_pos()
                angular_velocity_return =  spinner.calculate_angular_velocity(CENTER, current_pos, dt)
                angular_velocity = angular_velocity_return[0]
                spinner.initial_pos = angular_velocity_return[1]
                draw_text(str(angular_velocity), font, TEXT_COL, 100, 100)
            else:
                spinner_list.remove(spinner)
                initial_pos = (0, 0)
                print("removed spinner")
    
    for slider in slider_list:
        if not hasattr(slider, 'endtime_absolute'):
            slider.calculate_slider_endtime(current_timing_point, SliderMultiplier, current_time)
        if slider.endtime_absolute <= current_time:
            print(slider.endtime_relative, current_time)
            slider_list.remove(slider)
            print("removed slider from list")
        else:
            Slider.draw_slider(slider, window)
            Slider.update(slider, dt)

                

def recalculate_adjusted_position():
    print("rezized the window")
    for hit_object in hit_objects_list:
        hit_object.recalculate_adjusted_position(window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT)

# Initialize settings with default keybindings
settings = {
    'left_click': 1,
    'right_click': 3,
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

def get_last_time():
    last_object = hit_objects_list[-1]
    last_time = last_object.time
    print(last_time)
    return last_time

def main():
    clock = pygame.time.Clock()
    running = False  # Start with menu loop
    music_playing = False
    current_time = 0  # Initialize current_time
    start_time = 0  # Variable to store the time when the game starts running
    initial_pos = (0, 0)
    CENTER = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    hit_something = False # Variable that defines if a object has already been hit that frame
    last_time = get_last_time()
    
    hit_circle_texture, slider_texture, spinner_texture = load_textures()

    while True:
        if not running:  # Display menu if not running
            current_time = 0
            song_rects = display_menu(window)  # Get bounding rectangles and corresponding song texts
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    bye_sound.play()
                    pygame.time.delay(int(bye_length_seconds * 1000))
                    pygame.quit()
                    return  # Exit program if window closed
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        pygame.quit()
                        return  # Exit program if ESC pressed
                    elif event.key == pygame.K_RETURN:  # Start the game loop when Enter is pressed
                        running = True
                    elif event.key == pygame.K_o:
                        exit_settings = False
                        while True:
                            keybinding_rects = display_keybindings_menu(window)  # Display the keybindings menu
                            for settings_event in pygame.event.get():
                                if settings_event.type == pygame.KEYDOWN:
                                    if settings_event.key == pygame.K_1:
                                        exit_settings = True  # Set the flag to True when you want to exit
                                        break
                                elif settings_event.type == pygame.MOUSEBUTTONDOWN:
                                    if settings_event.button == 1:
                                        # Check if mouse click is within the bounding rectangle of any keybinding text
                                        for rect_top_left, keybinding in keybinding_rects.items():
                                            if pygame.Rect(rect_top_left, (100, 30)).collidepoint(settings_event.pos):  # Use 100x30 as width and height of text
                                                print("Keybinding selected:", keybinding)
                                                change_keybinding(keybinding)  # Change the selected keybinding
                            if exit_settings:  # Check the flag after the inner loop
                                break
                    elif event.key == pygame.K_d: # select beatmap from beatconnect.io
                        beatmap_info = get_beatmap_info()
                        names = list(beatmap_info.keys())
                        exit_names = False
                        scroll_offset = 0

                        while True:
                            name_rects = display_names_menu(window, names, scroll_offset)

                            for names_event in pygame.event.get(): 
                                if names_event.type == pygame.KEYDOWN:
                                    if names_event.key == pygame.K_1:
                                        exit_names = True  # Set the flag to True when you want to exit
                                        break
                                elif names_event.type == pygame.MOUSEWHEEL:
                                    if names_event.y > 0:
                                        print("scrolled up")
                                        scroll_offset -= 1  # Scroll up
                                    elif names_event.y < 0:
                                        print("scrolled down")
                                        scroll_offset += 1  # Scroll down
                                elif names_event.type == pygame.MOUSEBUTTONDOWN:
                                    if names_event.button == 1:
                                        # Check if mouse click is within the bounding rectangle of any name
                                        for rect_top_left, name in name_rects.items():
                                            if pygame.Rect(rect_top_left, (100, 30)).collidepoint(names_event.pos):  # Use 100x30 as width and height of text
                                                print("name selected:", name)
                                                link = beatmap_info.get(name)
                                                d_url = generate_download_link(link)
                                                print(d_url)
                                                download_and_import_file(d_url)
                            if exit_names:  # Check the flag after the inner loop
                                break

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
                    width, height = window.get_size()
                    CENTER = (width // 2, height // 2)

        else:  # Game loop

            dt = 1 / clock.get_fps()

            if not music_playing:
                # Start playing the music
                pygame.mixer.music.play()
                music_playing = True
            
            if current_time and not running:
                current_time = 0

            current_time = pygame.time.get_ticks() - start_time

            if last_time < current_time:
                pygame.mixer.music.stop()
                music_playing = False
                running = False

            #update cursor position
            new_cursor_position = pygame.mouse.get_pos()
            cursor_instance.update_position(new_cursor_position)

            # Update the current timing point
            current_timing_point = TimingPoints.get_current_timing_point(current_time, timing_points_list)

            # Rendering
            window.fill((0, 0, 0))  # Clear the screen

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        print("exit from game")
                        pygame.mixer.music.stop()
                        music_playing = False
                        running = False

                elif event.type == settings['right_click'] or settings['left_click']:
                    handle_mouse_click(event, cursor_instance, hit_objects_list, current_time, OverallDifficulty, hit_sound, sorted_hit_object_list, hit_something)

            hit_something = False

            # do hit objects
            for hit_object in hit_objects_list:
                hit_object.update(current_time)
                hit_object.draw(window, OSU_HEIGHT, OSU_HEIGHT, VERTICAL_SHIFT)

            main_game_logic(hit_objects_list, event, current_time, initial_pos, dt, current_timing_point, CENTER)
            

            # display current time in ms
            current_time_str = "Current Time: {} ms".format(current_time)
            draw_text(current_time_str, font, TEXT_COL, 50, 50)

            # display current score
            current_score_str = get_current_score()
            draw_text(current_score_str, font, TEXT_COL, 50, 200)

            # display current index
            current_index = str(starting_index_var)
            draw_text(current_index, font, TEXT_COL, 50, 300)

            # Update the display
            pygame.display.flip()

        clock.tick(60)

if __name__ == "__main__":
    main()

pygame.quit()

