import SimpleGUICS2Pygame.simpleguics2pygame as simplegui

WIDTH = 600
HEIGHT = 400
BALL_RADIUS = 20
frame = simplegui.create_frame("Мячик", WIDTH, HEIGHT)

class Balls:

    def __init__(self, width, height):
        self.ball_pos = [width / 2, height / 2]
        self.ball_vel = [0, 1]

    def update(self):
        self.ball_pos[1] += self.ball_vel[1]
        self.ball_vel[1] += 0.1

        if self.ball_pos[1] <= BALL_RADIUS or self.ball_pos[1] >= HEIGHT - BALL_RADIUS - 1:
            self.ball_vel[1] *= -1

    def draw(self, canvas):
        canvas.draw_circle(self.ball_pos, BALL_RADI§US, 5, "Blue", "White")

def draw(canvas):
    ball.draw(canvas)
    ball.update()

ball = Balls(WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.start()
