import pygame
from pygame.sprite import Sprite, Group
import json

# Set cursor dimensions
cursor_width, cursor_height = 20, 20

class HitObject(Sprite):
    
    last_selftime = 0

    def __init__(self, position, time, type, hitSound, addition=None, sliderType=None, curvePoints=None, slides=None, length=None, edgeSounds=None, edgeSets=None, endTime=None, washit=None):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 255))  # White rectangle representing hit object
        self.rect = self.image.get_rect(topleft=position)
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
        self.visible = False  # Whether the hit object is currently visible
        self.washit = False



    def update(self, current_time):
        # If the current time is past the hit object's time, make it visible
        if current_time >= self.time and self.washit == False:
            self.visible = True

        # If the hit object is visible, update its position
        if self.visible:
            self.position = self.calculate_position()

    def draw(self, window):
        # If the hit object is visible, draw it on the screen
        if self.visible:
            pygame.draw.circle(window, (255, 255, 255), self.position, 10)

    def calculate_position(self):
        return (self.position)
    
    def hit(self):
        if self.visible and self.time >= HitObject.last_selftime:
            print(f'Hit object at {self.time} was hit')
            self.visible = False
            self.washit = True


    def miss(self):
        print(f'Hit object at {self.time} was missed')
        # ... rest of miss logic ...

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
    