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
vel = [random.uniform(-1, 1) + score/50, random.uniform(-1, 1) + score/50]
ang_vel = random.uniform(-0.1, 0.1)
a_missile = None
rock_group = []
missile_group = []
explosion_group = []
started = False

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

debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui._load_local_image(os.path.join(dir, "debris2_blue.png"))
debris1_info = ImageInfo([320, 240], [640, 480])
debris1_image = simplegui._load_local_image(os.path.join(dir, "debris4_blue.png"))

ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui._load_local_image(os.path.join(dir, "double_ship.png"))

missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
missile_image = simplegui._load_local_image(os.path.join(dir, "shot2.png"))

asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui._load_local_image(os.path.join(dir, "asteroid_blue.png"))

explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui._load_local_image(os.path.join(dir, "explosion_alpha.png"))

nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui._load_local_image(os.path.join(dir, "ngc602.png"))

splash_info = ImageInfo([200, 112], [400, 224])
splash_image = simplegui._load_local_image(os.path.join(dir, "splash.png"))

soundtrack = simplegui.load_sound(os.path.join(dir, "Converted_file_d781eb32.ogg"))
soundtrack.set_volume(.8)

missile_sound = simplegui.load_sound(os.path.join(dir, "sci_fi_lazer_shot.ogg"))
missile_sound.set_volume(.3)

ship_thrust_sound = simplegui.load_sound(os.path.join(dir, "flame.ogg"))
ship_thrust_sound.set_volume(.5)
explosion_sound = simplegui.load_sound(os.path.join(dir, "explosion_single_large_07.ogg"))
explosion_sound.set_volume(.4)


def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
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

    def speedUpTurn(self):
        self.angle_vel += self.TURN_SPEED

    def speedDownTurn(self):
        self.angle_vel -= self.TURN_SPEED

    def fly(self):
        self.moving = True
        self.angle_stop = self.angle_fly

    def stop(self):
        self.moving = False

    def shoot(self):
        global a_missile, missile_group
        vel = angle_to_vector(self.angle_fly)
        a_missile = Sprite([self.pos[0] + 45 * vel[0], self.pos[1] + 45 * vel[1]], [vel[0] * 12, vel[1] * 12], 0, 0, missile_image, missile_info, missile_sound)
        missile_group.append(a_missile)

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

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius


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
        self.update()

        if self.animated:
            canvas.draw_image(self.image, [self.image_size[0] * self.age + self.image_center[0], self.image_center[1]], self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size, self.angle)

    def collide(self, other_object):
        radius = other_object.get_radius()
        pos = other_object.get_position()
        distance = dist(self.pos, pos)
        if distance <= self.radius + radius:
            return True
        else:
            return False

    def update(self):
        self.age += 1
        self.angle += self.angle_vel
        self.pos[0] = (self.pos[0] + self.vel[0]) % WIDTH
        self.pos[1] = (self.pos[1] + self.vel[1]) % HEIGHT
        if self.age > self.lifespan:
            return True
        else:
            return False

    def get_position(self):
        return self.pos

    def get_radius(self):
        return self.radius


def draw(canvas):
    global time_draw, score, lives, rock_group, missile_group, explosion_group, started
    new_rock_group = group_collide(rock_group, my_ship)
    new_missile_group = group_group_collide(missile_group, rock_group)

    time_draw += 1
    wtime = (time_draw / 4) % WIDTH
    center = debris_info.get_center()
    center1 = debris1_info.get_center()
    size = debris_info.get_size()
    size1 = debris1_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    canvas.draw_text('Lives: ' + str(lives), [WIDTH - 750, HEIGHT - 550], 50, 'Red')
    canvas.draw_text('Score: ' + str(score), [WIDTH - 200, HEIGHT - 550], 50, 'White')

    wtime1 = (time_draw / 8) % WIDTH

    canvas.draw_image(debris1_image, center1, size1, (wtime1 - WIDTH / 4, HEIGHT / 4), (WIDTH / 2, HEIGHT / 2))
    canvas.draw_image(debris1_image, center1, size1, (wtime1 + WIDTH / 4, HEIGHT / 4), (WIDTH / 2, HEIGHT / 2))

    if lives == 0:
        started = False
        score = 0
        my_ship.sound.rewind()
        missile_group = []
        rock_group = []
        soundtrack.rewind()
        explosion_group = []
        my_ship.angle_fly = 0
        my_ship.acceleration = 0
        my_ship.pos = [WIDTH / 2, HEIGHT/ 2]

    if started:
        my_ship.draw(canvas)
        my_ship.update()

        for missile in new_missile_group:
            if missile.update():
                missile_group.pop(missile_group.index(missile))
            missile.draw(canvas)

        for rock in new_rock_group:
            rock.draw(canvas)
            rock.update()

        for explosion in explosion_group:
            explosion.draw(canvas)
            explosion.update()
    else:
        canvas.draw_image(splash_image, splash_info.get_center(), splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], splash_info.get_size())


def group_collide(group, other_object):
    global lives, explosion_group
    new_group = group
    for i in group:
        if i.collide(other_object):
            new_group.pop(new_group.index(i))
            explosion_group.append(Sprite(i.get_position(), (0, 0), 0, 0, explosion_image, explosion_info, explosion_sound))
        if i.collide(my_ship):
            lives -= 1
            explosion_group.append(Sprite(i.get_position(), (0, 0), 0, 0, explosion_image, explosion_info, explosion_sound))
    return new_group


def group_group_collide(group1, group2):
    global score
    new_group = group1
    for i in group1:
        for j in group2:
            if i.collide(j):
                new_group.pop(new_group.index(i))
                group2.pop(group2.index(j))
                explosion_group.append(Sprite(i.get_position(), (0, 0), 0, 0, explosion_image, explosion_info, explosion_sound))
                score += 1
    return new_group


def rock_spawner():
    global time, WIDTH, HEIGHT, pos, vel, ang_vel, rock_group, score, started
    time += 1
    pos_ship = my_ship.get_position()

    if len(rock_group) < 9 and started:
        pos = [random.randint(0, WIDTH), random.randint(0, HEIGHT)]

        if dist(pos, pos_ship) > 150:
            vel = [random.randrange(-150, 150) / 100 * (1 + score / 100), random.randrange(-150, 150) / 100 * (1 + score / 100)]
            ang_vel = random.uniform(-0.1, 0.1)
            a_rock = Sprite(pos, vel, 0, ang_vel, asteroid_image, asteroid_info)
            rock_group.append(a_rock)


def keydown(key):
    if key == simplegui.KEY_MAP['right']:
        my_ship.speedUpTurn()
    elif key == simplegui.KEY_MAP['left']:
        my_ship.speedDownTurn()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.fly()
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()


def keyup(key):
    if key == simplegui.KEY_MAP['right']:
        my_ship.speedDownTurn()
    elif key == simplegui.KEY_MAP['left']:
        my_ship.speedUpTurn()
    elif key == simplegui.KEY_MAP['up']:
        my_ship.stop()


def click(pos):
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    width = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    height = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and width and height:
        started = True
        lives = 3
        score = 0
        soundtrack.play()

frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)
my_ship = Ship([WIDTH / 2, HEIGHT / 2], 0, ship_image, ship_thrust_sound, ship_info)

frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)

timer = simplegui.create_timer(1000.0, rock_spawner)

timer.start()
frame.start()

