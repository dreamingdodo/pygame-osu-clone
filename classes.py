import pygame
from pygame.sprite import Sprite, Group
import json

# Set cursor dimensions
cursor_width, cursor_height = 20, 20

class HitObject(pygame.sprite.Sprite):
    
    def __init__(self, position, time, type, hitSound, ApproachRate, CircleSize, addition=None, sliderType=None, curvePoints=None, slides=None, length=None, edgeSounds=None, edgeSets=None, endTime=None, washit=None, wasmissed=None):
        super().__init__()
        self.position = position
        self.time = time
        self.type = type
        self.hitSound = hitSound
        self.addition = addition if addition is not None else []
        self.sliderType = sliderType
        self.curvePoints = curvePoints
        self.slides = slides
        self.length = length
        self.edgeSounds = edgeSounds
        self.edgeSets = edgeSets
        self.endTime = endTime
        self.visible = False
        self.washit = False
        self.wasmissed = False
        self.circle_size = self.calculate_circle_size(CircleSize)
        self.circle_radius = self.circle_size + 30  # Initial radius of the circle
        self.APPEARANCE_TIME_BEFORE_HIT = self.calculate_appearance_time(ApproachRate)
        self.circle_speed = self.calculate_circle_speed()  # Speed at which the circle radius reduces
        self.image = pygame.Surface((2 * self.circle_radius, 2 * self.circle_radius))
        self.rect = self.image.get_rect(center=position)
        
        

    def calculate_circle_size(self, CircleSize):
        radius = 54.4 - 4.48 * CircleSize
        print(radius)
        return radius

    def calculate_appearance_time(self, ApproachRate):
        if ApproachRate < 5:
            return 1200 + 600 * (5 - ApproachRate) / 5
        elif ApproachRate == 5:
            return 1200
        else:
            return 1200 - 750 * (ApproachRate - 5) / 5

    def calculate_circle_speed(self):
        # Calculate distance to cover
        distance_to_cover = self.circle_radius - self.circle_size # - the radius of the hit object

        # Calculate circle speed to cover the distance in the time before hit
        circle_speed = distance_to_cover / self.APPEARANCE_TIME_BEFORE_HIT

        # Convert circle speed from pixels per millisecond to pixels per frame
        circle_speed_per_frame = circle_speed * (1000 / 60)

        print("circle speed", circle_speed_per_frame)

        return circle_speed_per_frame

    def update(self, current_time):
        # Calculate time difference between current time and hit object's time
        time_diff = self.time - current_time
        
        # If the hit object's appearance time has passed but it's not hit yet, mark as missed
        if time_diff <= -self.APPEARANCE_TIME_BEFORE_HIT and not self.washit and not self.wasmissed:
            self.miss()
        
        # If the current time is past the hit object's appearance time, make it visible
        if current_time >= self.time - self.APPEARANCE_TIME_BEFORE_HIT and not self.washit and not self.wasmissed:
            self.visible = True

        
        # Reduce the circle radius if hit object is visible
        if self.visible:
            self.circle_radius -= self.circle_speed

    def draw(self, window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT):
        # If the hit object is visible, draw it on the screen
        if self.visible:
            # Calculate the position of the hit object within the window
            playfield_x = (window.get_width() - OSU_WIDTH) // 2
            playfield_y = (window.get_height() - OSU_HEIGHT) // 2 + VERTICAL_SHIFT
            
            screen_position = (self.position[0] + playfield_x, self.position[1] + playfield_y)
            pygame.draw.circle(window, (255, 255, 255), screen_position, self.circle_size) # Draw hit object
            pygame.draw.circle(window, (255, 255, 255), screen_position, self.circle_radius, 1) # Draw approach circle


    def hit(self, hit_time):
        if self.visible:
            print(f'Hit object at {self.time} was hit at time {hit_time}')
            self.visible = False
            self.washit = True
            # ... rest of hit logic ...
            return True  # Return True indicating successful hit
        return False  # Return False indicating miss

    def miss(self):
        if self.visible:
            print(f'Hit object at {self.time} was missed')
            self.visible = False
            self.wasmissed = True
            # ... rest of miss logic ...
            return True  # Return True indicating missed
        return False  # Return False indicating already missed


class Beatmap:
    def __init__(self, general, editor, metadata, difficulty, events, timing_points, hit_objects):
        self.general = general
        self.editor = editor
        self.metadata = metadata
        self.difficulty = difficulty
        self.events = events
        self.timing_points = [TimingPoint(data) for data in timing_points]
        self.hit_objects = [HitObject(data) for data in hit_objects]

    def save_to_file(self, filename):
        data = {
            'general': self.general,
            'editor': self.editor,
            'metadata': self.metadata,
            'difficulty': self.difficulty,
            'events': self.events,
            'timing_points': [tp.to_dict() for tp in self.timing_points],
            'hit_objects': [ho.to_dict() for ho in self.hit_objects],
        }
        with open(filename, 'w') as file:
            json.dump(data, file)

    @staticmethod
    def load_from_file(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        return Beatmap(
            data['general'],
            data['editor'],
            data['metadata'],
            data['difficulty'],
            data['events'],
            [TimingPoint.from_dict(tp) for tp in data['timing_points']],
            [HitObject.from_dict(ho) for ho in data['hit_objects']],
        )

#button class
class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

class Cursor:
    def __init__(self, position):
        self.pos = position
        self.rect = pygame.Rect(position[0], position[1], cursor_width, cursor_height)

    def update_position(self, new_position):
        self.pos = new_position
        self.rect.topleft = new_position  # Update rect position


class Playfield:
    def __init__(self, base_resolution=(640, 480)):
        self.base_resolution = base_resolution
        self.screen_resolution = pygame.display.get_surface().get_size()
        self.scale_factor_x = self.screen_resolution[0] / self.base_resolution[0]
        self.scale_factor_y = self.screen_resolution[1] / self.base_resolution[1]

    def to_game_pixels(self, pixels):
        game_pixels_x = pixels[0] * self.scale_factor_x
        game_pixels_y = pixels[1] * self.scale_factor_y
        return int(game_pixels_x), int(game_pixels_y)

    def to_screen_pixels(self, game_pixels):
        screen_pixels_x = game_pixels[0] / self.scale_factor_x
        screen_pixels_y = game_pixels[1] / self.scale_factor_y
        return int(screen_pixels_x), int(screen_pixels_y)
