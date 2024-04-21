import pygame
from pygame.sprite import Sprite, Group
import json
import numpy as np
import math
import bisect
import sys


# Set cursor dimensions
cursor_width, cursor_height = 20, 20


# AI assisted code start
def draw_bezier_curve(screen, control_points):
    control_points_array = np.array(control_points, dtype=float)
    # Function to calculate Bezier curve
    def bezier(t, points):
        n = len(points)
        if n == 1:
            return points[0]
        else:
            return (1-t)*bezier(t, points[:-1]) + t*bezier(t, points[1:])

    # Draw the Bezier curve
    for t in np.linspace(0, 1, 100):
        point = bezier(t, control_points_array)
        pygame.draw.circle(screen, (255, 0, 0), point.astype(int), 2)

    # Draw the control points
    for point in control_points_array:
        pygame.draw.circle(screen, (255, 255, 255), point.astype(int), 5)

# AI assist end

def draw_line(screen, points, color=(255, 255, 255)):
    pygame.draw.lines(screen, color, False, points)

def catmull_rom_one_point(x, *points):
    n = len(points) - 1
    c = np.empty(n * 4)

    for i in range(n):
        p0, p1, p2, p3 = points[i:i + 4]
        c[i*4:i*4+4] = [
            0.5 * (-p0 + 3 * p1 - 3 * p2 + p3),
            p0 - 2.5 * p1 + 2 * p2 - 0.5 * p3,
            0.5 * (-p0 + p2),
            2 * p1
        ]

    return sum(c[i] * x ** i for i in range(4))

def catmull_rom(points, res):
    points = [points[0]] + list(points) + [points[-1]]  # Duplicate first and last points
    num_segments = len(points) - 3
    x_intpol = np.empty(res * num_segments + 1)
    y_intpol = np.empty(res * num_segments + 1)
    x_intpol[-1] = points[-1][0]
    y_intpol[-1] = points[-1][1]

    for i in range(num_segments):
        p0, p1, p2, p3 = points[i:i + 4]
        x_intpol[i*res:(i+1)*res] = np.linspace(p1[0], p2[0], res, endpoint=False)
        y_intpol[i*res:(i+1)*res] = [catmull_rom_one_point(x, p0[1], p1[1], p2[1], p3[1]) for x in np.linspace(0., 1., res, endpoint=False)]

    return list(zip(x_intpol, y_intpol))

def draw_spline(screen, points, color=(255, 255, 255)):
    for i in range(len(points) - 1):
        pygame.draw.line(screen, color, points[i], points[i+1])


def calculate_circle(points):
    # Unpack the points
    (x1, y1), (x2, y2), (x3, y3) = points

    # Calculate the determinant of the matrix
    D = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))

    # Calculate the center of the circle
    Ux = ((x1 * x1 + y1 * y1) * (y2 - y3) + (x2 * x2 + y2 * y2) * (y3 - y1) + (x3 * x3 + y3 * y3) * (y1 - y2)) / D
    Uy = ((x1 * x1 + y1 * y1) * (x3 - x2) + (x2 * x2 + y2 * y2) * (x1 - x3) + (x3 * x3 + y3 * y3) * (x2 - x1)) / D

    # Calculate the radius of the circle
    r = np.sqrt((x1 - Ux)**2 + (y1 - Uy)**2)

    return (Ux, Uy, r)

def draw_cricle(window, curve_points):
    center_x, center_y, radius = calculate_circle(curve_points)
    pygame.draw.circle(window, (255, 255, 255), (center_x, center_y), radius)


class HitObject(pygame.sprite.Sprite):
    
    def __init__(self, position, time, type, hitSound, ApproachRate, CircleSize, window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT, addition=None, sliderType=None, curvePoints=None, slides=None, length=None, edgeSounds=None, edgeSets=None, endTime=None, washit=None, wasmissed=None):
        super().__init__()
        self.position = position
        self.adjusted_position = self.get_screen_position(window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT)
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
        self.rect = self.image.get_rect(center=self.get_screen_position(window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT))
        self.has_spinner = False
        self.has_slider = False
        
        

    def calculate_circle_size(self, CircleSize):
        radius = 54.4 - 4.48 * CircleSize
        print("circle radius: ", radius)
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

    def recalculate_adjusted_position(self, window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT):
        self.adjusted_position = self.get_screen_position(window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT)

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
            screen_position = self.adjusted_position
            pygame.draw.circle(window, (255, 255, 255), screen_position, self.circle_size) # Draw hit object
            pygame.draw.circle(window, (255, 255, 255), screen_position, self.circle_radius, 1) # Draw approach circle
            pygame.draw.circle(window, (200, 200, 200), pygame.mouse.get_pos(), 5)

    def get_screen_position(self, window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT):
        # Calculate the position of the hit object within the window
        width, height = window.get_size()
        extra = ((width // 2) - (OSU_WIDTH // 2), (height // 2) - (OSU_HEIGHT // 2))
        
        #screen_position = (self.position[0] + playfield_x, self.position[1] + playfield_y) # old, dont use anymore
        screen_position = (self.position[0] + extra[0], self.position[1] + extra[1]) 

        return screen_position



    def hit(self, hit_time):
        if self.visible:
            print(f'Hit object at {self.time} was hit at time {hit_time}')
            self.visible = False
            self.washit = True
            # ... rest of hit logic ...
            return True
        return False

    def miss(self):
        if self.visible:
            print(f'Hit object at {self.time} was missed')
            self.visible = False
            self.wasmissed = True
            # ... rest of miss logic ...
            return True
        return False

class Spinner(HitObject):
    def __init__(self, hit_object, initial_pos, current_pos, endtime):
        self.__dict__ = hit_object.__dict__.copy()  # Copy attributes from hit_object
        self.initial_pos = initial_pos
        self.current_pos = current_pos
        self.endtime = endtime
        

    def calculate_angular_velocity(self, CENTER, current_pos, dt):

        # Calculate the initial angle
        initial_angle = math.atan2(self.initial_pos[1] - CENTER[1], self.initial_pos[0] - CENTER[0])

        # Calculate the new angle
        new_angle = math.atan2(current_pos[1] - CENTER[1], current_pos[0] - CENTER[0])

        # Calculate the change in angle
        d_angle = new_angle - initial_angle

        angle_threshold = 0.01 # Angel thershold

        if abs(d_angle) < angle_threshold:
            angular_velocity = 0
        else:
            angular_velocity = d_angle / dt

        # Make all rotations positive
        angular_velocity = abs(angular_velocity)

        initial_pos = current_pos

        return (angular_velocity, initial_pos)


class Slider(HitObject):
    def __init__(self, hit_object, curve_type, slides, length, edge_sounds, edge_sets, curve_points):
        self.__dict__ = hit_object.__dict__.copy()  # Copy attributes from hit_object
        self.curve_type = curve_type
        self.slides = slides
        self.length = length
        self.edge_sounds = edge_sounds
        self.edge_sets = edge_sets
        self.curve_points = curve_points
        if self.curve_type == "C":
            self.spline_points = catmull_rom(self.curve_points, 50)


    def calculate_slider_endtime(self, current_timing_point, SliderMultiplier, current_time):
        if current_timing_point.uninherited == 0:
            # a negative inverse slider velocity multiplier, as a percentage
            SV = 100 / (100 + int(current_timing_point.beatLength))
            print("slide velocity multiplier: ", SV)
        else:
            SV = 1
        print("length: ", float(self.length), "slider multiplier: ", SliderMultiplier,"SV: ", SV, float(current_timing_point.beatLength))
        endtime = float(self.length) / (SliderMultiplier * 100 * SV) * abs(float(current_timing_point.beatLength)) #length / (SliderMultiplier * 100 * SV) * beatLength
        self.endtime_relative = endtime
        self.endtime_absolute = endtime + current_time
        return endtime

    def draw_slider(self, window):
        if self.curve_type == "B":   # bézier
            self.curve_points.insert(0, self.position)
            draw_bezier_curve(window, self.curve_points)
        elif self.curve_type == "C": # centripetal catmull-rom
            self.curve_points.insert(0, self.position)
            draw_spline(window, self.curve_points)
        elif self.curve_type == "L": # Linear
            self.curve_points.insert(0, self.position)
            draw_line(window, self.curve_points)
        elif self.curve_type == "P": # Perfect circle
            self.curve_points.insert(0, self.position)
            if len(self.curve_points) > 3:
                draw_bezier_curve(window, self.curve_points)
            else:
                draw_cricle(window, self.curve_points)

    def is_hit(self, x, y):
        pass

    def update(self, dt):
        pass

    def adjust_curve_points(self, window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT):
        for point in self.curve_points:
            point = HitObject.recalculate_adjusted_position(window, OSU_HEIGHT, OSU_WIDTH, VERTICAL_SHIFT)
        return self.curve_points


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
        self.rect.center = new_position  # Update rect position


class Playfield: #not in use
    def __init__(self, base_resolution=(640, 480)):
        self.base_resolution = base_resolution
        self.screen_resolution = pygame.display.get_surface().get_size()
        self.scale_factor_x = self.screen_resolution[0] / self.base_resolution[0]
        self.scale_factor_y = self.screen_resolution[1] / self.base_resolution[1]
        print("scale factor x: ", self.scale_factor_x, "scale factor y: ", self.scale_factor_y)

    def to_game_pixels(self, pixels):
        game_pixels_x = pixels[0] * self.scale_factor_x
        game_pixels_y = pixels[1] * self.scale_factor_y
        return int(game_pixels_x), int(game_pixels_y)

    def to_screen_pixels(self, game_pixels):
        screen_pixels_x = game_pixels[0] / self.scale_factor_x
        screen_pixels_y = game_pixels[1] / self.scale_factor_y
        return int(screen_pixels_x), int(screen_pixels_y)

class TimingPoints:
    def __init__(self, time, beatLength, meter, sampleSet, sampleIndex, volume, uninherited, effects):
        self.time = time
        self.beatLength = beatLength
        self.meter = meter
        self.sampleSet = sampleSet
        self.sampleIndex = sampleIndex
        self.volume = volume
        self.uninherited = uninherited
        self.effects = effects
    
    def get_current_timing_point(current_time, timing_points_list):
        # Use bisect to find the insertion point for current_time in the timing_points_list
        index = bisect.bisect([tp.time for tp in timing_points_list], current_time)
        # Return the timing point with the lowest time attribute that is still higher than current_time
        return timing_points_list[index] if index != len(timing_points_list) else None