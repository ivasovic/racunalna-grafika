import sys
from pyglet.gl import *
import random
import numpy as np
import time

window = pyglet.window.Window()


acc = np.array([0, 10, 0])
# cestica.bmp iskrica.tga
texture_ = pyglet.image.load('cestica.bmp').get_texture()
cameraPositon = (150.0, 0.0, 150.0)
lookAt = (0.0, 0.0, 0.0)
upVector = (0.0, 1.0, 0.0)
width = 1200
height = 780


def rotate(start_, end_):
    os = np.cross(start_, end_)
    br = np.dot(start_, end_)
    naz = np.linalg.norm(start_)*np.linalg.norm(end_)
    angle_rad = np.arccos(br/naz)
    angle_deg = np.rad2deg(angle_rad)
    return os, angle_deg

class particle:
    def __init__(self, position):
        self.position = position.copy()
        self.position[0] += random.gauss(0,5)
        self.position[1] += random.uniform(0,8)
        self.position[2] += random.uniform(0,14)
        self.color = [1,1,1]

        self.velocity = np.array([random.gauss(-7.0,7.0), 70+random.gauss(-8.0,8.0), random.gauss(-14.0,14.0)])
        self.create_time = time.time()
        self.life_span = abs(random.gauss(0.0,0.30))
        self.delete_time = self.create_time + self.life_span
        self.life_fraction = 0.0

        
    def update(self, dt, t):
        self.position = self.position + self.velocity * dt
        self.velocity = self.velocity + acc * dt
        
        self.life_fraction = 1.0 - max(0.0, (self.delete_time - t) / float(self.life_span))
        g = 1.0 - self.life_fraction
        self.color = [1, g, 0]




class particleSystem:
    def __init__(self, n=100):
        self.particles = []
        self.create_particles(n)

    def create_particles_old(self, n):
        for i in range(0,n):
            if n % 2 == 0:
                p = particle(np.array([0,0,0]))
            else:
                p = particle(np.array([100,0,0]))
            self.particles.append(p)

    def create_particles(self, n):
        for i in range(0,n):
            p = self.create_particle(i % 2)
            self.particles.append(p)

    def create_particle(self, pos):
        if pos == 0:
            p = particle(np.array([0,0,0]))
        else:
            p = particle(np.array([100,0,0]))
        return p

    def draw(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, float(width)/float(height), 0.05, 1000)
        gluLookAt(cameraPositon[0], cameraPositon[1], cameraPositon[2], 
                lookAt[0], lookAt[1], lookAt[2], 
                upVector[0], upVector[1], upVector[2])
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        glEnable(texture_.target)
        glBindTexture(texture_.target, texture_.id)
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        for p in self.particles:
            start_ = np.array([0,0,1])
            end_ = np.array([cameraPositon[0], cameraPositon[1], cameraPositon[2]]) - np.array([p.position[0], p.position[1], p.position[2]])
            os_, deg = rotate(start_, end_)

            glLoadIdentity()
            glRotatef(deg, os_[0], os_[1], os_[2])
            glBegin(GL_QUADS)
            glColor3f(p.color[0], p.color[1], p.color[2])
            max_size = 5
            size = max_size * (1 - p.life_fraction)
            
            glTexCoord2f(0,0)
            glVertex3f(p.position[0]-size, p.position[1]-size, p.position[2])
            glTexCoord2f(1,0)
            glVertex3f(p.position[0]+size, p.position[1]-size, p.position[2])
            glTexCoord2f(1,1)
            glVertex3f(p.position[0]+size, p.position[1]+size, p.position[2])
            glTexCoord2f(0,1)
            glVertex3f(p.position[0]-size, p.position[1]+size, p.position[2])
            glEnd()

        glDisable(GL_BLEND)
        glDisable(texture_.target)

    def update(self, dt):
        #print(dt)
        t = time.time()
        for p in self.particles:
            p.update(dt, t)

        for i in range(len(self.particles)):
            if (self.particles[i].delete_time <= t): 
                del self.particles[i]
                p = self.create_particle(i%2)
                self.particles.append(p)


@window.event
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    for s in p_system:
        s.draw()


def update(dt):
    for i in p_system: 
        i.update(dt)

p_system = [particleSystem(300)]

pyglet.clock.schedule_interval(update, 1/60.0)
pyglet.app.run()