import pyglet
import keyboard as kb
import math
import random


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Circle:
    def __init__(self, center, radius, colour):
        self.center = center
        self.dia = radius*2
        self.radius = radius
        self.colour = colour

    def draw_circle(self):
        coordinates = []
        for i in range(0, self.dia):
            angle = (math.pi * 2 * i) / self.dia
            x = self.radius * math.cos(angle)+self.center.x
            y = self.radius * math.sin(angle)+self.center.y
            coordinates.append(x)
            coordinates.append(y)
        pyglet.graphics.draw(self.dia, pyglet.gl.GL_TRIANGLE_FAN, ("v2f", tuple(coordinates)), ("c4B", tuple(self.colour*(len(coordinates)//2))))


class Player:
    def __init__(self, center, ctrls, colour):
        self.center = center
        self.velocity = Point(0, 0)
        
        self.size = 20
        self.colour = colour
        
        self.ctrls = ctrls
        self.score = 0

    def draw_player(self):
        Circle(self.center, int(self.size / 2), self.colour).draw_circle()

    def move_player(self):
        if kb.is_pressed(self.ctrls[0]):
            self.velocity.x -= 15/20 
        if kb.is_pressed(self.ctrls[1]):
            self.velocity.x += 15/20
        if kb.is_pressed(self.ctrls[2]):
            self.velocity.y += 15/20     
        if kb.is_pressed(self.ctrls[3]):
            self.velocity.y -= 15/20


    def update_player(self):
        self.center.x += self.velocity.x
        self.center.y += self.velocity.y

        self.velocity.x *= 0.87
        self.velocity.y *= 0.87

        width = window.get_size()[0]
        height = window.get_size()[1]

        if (self.center.x - self.size/2)<0:
            self.center.x = self.size/2
        if (self.center.x + self.size/2)>width:
            self.center.x = width - self.size/2
        if (self.center.y - self.size/2)<0:
            self.center.y = self.size/2
        if (self.center.y + self.size/2)>height:
            self.center.y = height - self.size/2 
            
    

class Particle:
    def __init__(self, center, size, colour):
        self.center = Point(center.x, center.y) 
        self.velocity = Point(0,0)
        self.acc = Point(0, -0.001)
        self.life_span = 320
        self.size = size
        self.colour = colour

    def update(self):
        self.center.x += self.velocity.x
        self.center.y += self.velocity.y
        self.velocity.x += self.acc.x
        self.velocity.y += self.acc.y
        self.life_span -= 2

    def add_force(self, force):
        self.velocity.x += force.x
        self.velocity.y += force.y

    def draw_particle(self):
        Circle(self.center, int(self.size/2), self.colour + [self.life_span]).draw_circle()

    def particle_dead(self):
        check = self.life_span <= 0
        return check

    def collision(self, other):
        x = other.center.x - self.center.x
        y = other.center.y - self.center.y
        distance = math.sqrt(x**2 + y**2)
        result = (other.size/2 + self.size/2)>distance

        return result


class ParticleSystem:
    def __init__(self, source):
        self.source_x, self.source_y = source
        self.particles = []
        self.score = 0
        self.immunity = False
        self.freeze_time = 0
        self.game_over = False

    def update(self):
        x = random.uniform(self.source_x - 400, self.source_x + 400)
        y = self.source_y
        
        if self.immunity:
            if frames>(self.freeze_time+100):
                self.immunity = False

        if frames % random.randint(1, 35) == 0:
            self.particles.append(Particle(Point(x, y), random.uniform(7, 37), [0,255,0]))

        if frames % 100 == 0:
            if random.randint(0,1) == 1:
                self.particles.append(Particle(Point(x, y), random.uniform(7, 37), [0,0,0]))

        if frames % 150 == 0:
            self.particles.append(Particle(Point(x, y), random.uniform(7, 37), [255,0,0]))

        if frames % 70 == 0:
            self.score += 1

        if frames % 500 == 0:
            self.particles.append(Particle(Point(x, y), random.uniform(7, 37), [255,255,0]))


        for i in range(len(self.particles)-1, -1, -1):
            self.particles[i].draw_particle()
            self.particles[i].update()

            self.particles[i].add_force(Point(random.uniform(-0.25, 0.25), random.uniform(-0.12, 0.01)))
            if self.particles[i].particle_dead():
                self.particles.pop(i)


    def collision(self, other):
        if not self.game_over:
            for i in range(len(self.particles) - 1, -1, -1):
                if self.particles[i].collision(other):
                    if self.particles[i].colour == [255,0,0]:
                        self.score += 5
                    elif self.particles[i].colour == [255,255,0]:
                        other.size = 20
                    elif self.particles[i].colour == [0,0,0]:
                        self.immunity = True
                        self.freeze_time = frames
                    elif self.immunity:
                        pass
                    else:
                        other.size += self.particles[i].size * 0.25
                        self.score -= 5
                    self.particles.pop(i)


frames = 0

class MyWindow(pyglet.window.Window):
    def __init__(self):
        super().__init__(800, 800, "Game")

        pyglet.clock.schedule_interval(self.update, 1 / 60)

        self.particle_system = ParticleSystem((400, 800))
        self.player = Player(Point(400, 400), ("LEFT", "RIGHT", "UP", "DOWN"), (0, 0, 255, 255))

    def update(self, dt):
        pass

    def on_draw(self):
        self.clear()
        global frames
        frames += 1
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.particle_system.collision(self.player)
        self.particle_system.update()
        self.player.draw_player()
        self.player.move_player()
        self.player.update_player()
        pyglet.text.Label(f'score: {str(self.particle_system.score)}', font_size = 16, x = 700, y = 750, anchor_x = "center", anchor_y = "center", color = (0, 0, 0, 255)).draw()

        if self.player.size > 200:
            self.particle_system.game_over = True
            pyglet.text.Label("Game over!", font_size = 40, x = 400, y = 400, anchor_x = "center", anchor_y = "center", color = (0, 0, 0, 255)).draw()


    

window = MyWindow()
pyglet.app.run()