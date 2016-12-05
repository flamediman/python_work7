import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random
import numpy
import os

WIDTH = 800
HEIGHT = 600
score = 0
lives = 3
time = 0
time_draw = 0.5
pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
vel = [random.uniform(-3, 3), random.uniform(-3, 3)]
ang_vel = random.uniform(-0.1, 0.1)
a_missile = None
dir = os.path.dirname(os.path.abspath(__file__))


class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

# Фон с космическим мусором - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui._load_local_image(os.path.join(dir, "debris2_blue.png"))

# Корабль
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui._load_local_image(os.path.join(dir, "double_ship.png"))

# Ракета - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
missile_image = simplegui._load_local_image(os.path.join(dir, "shot2.png"))

# Астероиды - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui._load_local_image(os.path.join(dir, "asteroid_blue.png"))

# Анимированные взрывы - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui._load_local_image(os.path.join(dir, "explosion_alpha.png"))

# Туманность - ngc602.png, Andromeda.png, ngc346.png, ngc602.png, tarantula-nebula.png. Фотографии NASA.
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui._load_local_image(os.path.join(dir, "ngc602.png"))

# Заставка. На основе графики NASA.
splash_info = ImageInfo([200, 112], [400, 224])
splash_image = simplegui._load_local_image("img/splash.png")

# Фоновая музыка для игры. Emitremmus. Welcome To Nova.
soundtrack = simplegui.load_sound(os.path.join(dir, "Converted_file_d781eb32.ogg"))
soundtrack.set_volume(.8)
soundtrack.play()
# Спецэффекты с сайта http://www.freesfx.co.uk
missile_sound = simplegui.load_sound(os.path.join(dir, "sci_fi_lazer_shot.ogg"))
missile_sound.set_volume(.5)

ship_thrust_sound = simplegui.load_sound(os.path.join(dir, "flame.ogg"))
ship_thrust_sound.set_volume(.5)
explosion_sound = simplegui.load_sound("snd/explosion_single_large_07.ogg")


def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
    """Вычислить расстояние между точками."""
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)


class Ship:
    MAX_ACCELERATION = 8
    MIN_ACCELERATION = 0
    TURN_SPEED = 0.07
    MOVING_IMAGE_OFFET = numpy.array([91, 0])
    def __init__(self, pos, angle, image, sound, info):
        self.pos = [pos[0], pos[1]]
        self.angle_vel = 0
        self.acceleration = 0
        self.angle_fly = angle
        self.angle_stop = angle
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.sound = sound
        self.moving = False
        self.fire = None

    def draw(self, canvas):
        image_center = numpy.array(self.image_center)
        if self.moving:
            image_center += self.MOVING_IMAGE_OFFET
            self.sound.play()
        else:
            self.sound.rewind()
        canvas.draw_image(self.image, image_center.tolist(), self.image_size, self.pos, self.image_size, self.angle_fly)

        if self.fire:
            a_missile.draw(canvas)
            a_missile.update()

    def speedUpTurn(self):
        self.angle_vel += self.TURN_SPEED

    def speedDownTurn(self):
        self.angle_vel -= self.TURN_SPEED

    def fly(self):
        self.moving = True
        self.angle_stop = self.angle_fly

    def stop(self):
        self.moving = False

    def shoot(self, fire):
        global a_missile
        self.fire = fire
        vel = angle_to_vector(self.angle_fly)
        a_missile = Sprite([self.pos[0] + 45 * vel[0], self.pos[1] + 45 * vel[1]], [vel[0] * 12, vel[1] * 12], 0, 0, missile_image, missile_info, missile_sound)

    def update(self):
        self.angle_fly += self.angle_vel

        if self.moving:
            self.acceleration = min([self.acceleration + 0.1, self.MAX_ACCELERATION])
            vel = angle_to_vector(self.angle_fly)
            self.pos[0] = (self.pos[0] + vel[0] * self.acceleration) % WIDTH
            self.pos[1] = (self.pos[1] + vel[1] * self.acceleration) % HEIGHT
            self.angle_stop += self.angle_vel
        else:
            self.acceleration = max([self.acceleration - 0.1, self.MIN_ACCELERATION])
            vel = angle_to_vector(self.angle_stop)
            self.pos[0] = (self.pos[0] + vel[0] * self.acceleration) % WIDTH
            self.pos[1] = (self.pos[1] + vel[1] * self.acceleration) % HEIGHT


class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()

    def draw(self, canvas):
        canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def update(self):
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT


def draw(canvas):
    global time_draw, score, lives

    # Анимация фона.
    time_draw += 1
    wtime = (time_draw / 4) % WIDTH
    center = numpy.array(debris_info.get_center()) + [0.1, 0]
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center.tolist(), size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center.tolist(), size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_text('Lives: ' + str(lives), [WIDTH - 750, HEIGHT - 550], 50, 'Red')
    canvas.draw_text('Score: ' + str(score), [WIDTH - 200, HEIGHT - 550], 50, 'White')

    my_ship.draw(canvas)
    a_rock.draw(canvas)

    my_ship.update()
    a_rock.update()


def rock_spawner():
    global time, a_rock, WIDTH, HEIGHT, pos, vel, ang_vel
    time += 1
    pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]
    vel = [random.uniform(-3, 3), random.uniform(-3, 3)]
    ang_vel = random.uniform(-0.1, 0.1)
    if time % 5 == 0:
        a_rock = Sprite(pos, vel, 0, ang_vel, asteroid_image, asteroid_info)


def keydown(key):
    if key == simplegui.KEY_MAP['right']:
        my_ship.speedUpTurn()
    elif key == simplegui.KEY_MAP['left']:
        my_ship.speedDownTurn()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.fly()
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot(True)


def keyup(key):
    if key == simplegui.KEY_MAP['right']:
        my_ship.speedDownTurn()
    elif key == simplegui.KEY_MAP['left']:
        my_ship.speedUpTurn()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.stop()


frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

a_rock = Sprite(pos, vel, 0, ang_vel, asteroid_image, asteroid_info)
my_ship = Ship([WIDTH / 2, HEIGHT / 2], 0, ship_image, ship_thrust_sound, ship_info)

frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)

timer = simplegui.create_timer(1000.0, rock_spawner)

timer.start()
frame.start()

