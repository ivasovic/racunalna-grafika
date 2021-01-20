import numpy as np
import sys
from pyglet.gl import *
from pyglet.window import key
from pyglet.window import mouse

alpha = 0
point_t = 0
seg = 0

bspline_vertices = []
width = 1200
height = 780
window = pyglet.window.Window(width, height)
cameraPositon = (1.0, 1.0, 1.0)
lookAt = (0.0, 0.0, 0.0)
upVector = (0.0, 1.0, 0.0)


def bspline_parse():
	f_bsplin = open('bspline.obj', 'r')
	bspline_vertices = []
	for l in f_bsplin:
		if l.startswith('v'):
			line = l.rstrip('\n').split()
			bspline_vertices.append([float(line[1]), float(line[2]), float(line[3])])
	f_bsplin.close()


	x = []
	y = []
	z = []

	for i in bspline_vertices:
		x.append(i[0])
		y.append(i[1])
		z.append(i[2])

	x_min_b = min(x)
	y_min_b = min(y)
	z_min_b = min(z)

	x_max_b = max(x)
	y_max_b = max(y)
	z_max_b = max(z)

	x_trans_b = ((x_max_b+x_min_b)/2)
	y_trans_b = ((y_max_b+y_min_b)/2)
	z_trans_b = ((z_max_b+z_min_b)/2)

	scale_b = max(x_max_b-x_min_b, y_max_b-y_min_b, z_max_b-z_min_b)

	return bspline_vertices, scale_b


def tangent(t, i_):
	T2 = np.array([t*t, t, 1])
	B_d = (1/2)*np.array([[-1, 3, -3, 1], [2, -4, 2, 0], [-1, 0, 1, 0]])
	Ri = np.array([bspline_vertices[i_-1], bspline_vertices[i_], bspline_vertices[i_+1], bspline_vertices[i_+2]])
	dp_dt = np.dot(np.dot(T2, B_d), Ri)
	return dp_dt


def rotate(start_, end_):
	os = np.cross(start_, end_)
	br = np.dot(start_, end_)
	naz = np.linalg.norm(start_)*np.linalg.norm(end_)
	angle_rad = np.arccos(br/naz)
	angle_deg = np.rad2deg(angle_rad)
	return os, angle_deg

def ith_segment(t, i_):
	T3 = np.array([t*t*t, t*t, t, 1])
	B = 1/6 * np.array([[-1, 3, -3, 1],[3, -6, 3, 0],  [-3, 0, 3, 0],  [1, 4, 1, 0]])
	Ri = np.array([bspline_vertices[i_-1], bspline_vertices[i_], bspline_vertices[i_+1], bspline_vertices[i_+2]])

	p_t = np.dot(np.dot(T3, B), Ri)
	return p_t





def object_parse():
	f = open('panda.obj', 'r')
	#polje vrhova [[x1, y1, z1], [x2, y2, z2], ..., [xn, yn, zy]]
	vertices = []

	#polygon - pokazivaci na vrhove[[3, 2, 1], [1, 4, 5], ...]
	polygons = []

	i = 0

	for l in f:
		if l.startswith('#') or l.startswith('g'):
			pass
		else:
			line = l.rstrip('\n').split()

			if line[0] == 'v':
				vertices.append([float(line[1]), float(line[2]), float(line[3])])
			if line[0] == 'f':
				polygons.append([int(line[1]), int(line[2]), int(line[3])])


	f.close()

	x = []
	y = []
	z = []

	width=0
	height=0
	for i in vertices:
		x.append(i[0])
		y.append(i[1])
		z.append(i[2])

	x_min = min(x)
	y_min = min(y)
	z_min = min(z)

	x_max = max(x)
	y_max = max(y)
	z_max = max(z)

	x_trans = ((x_max+x_min)/2)
	y_trans = ((y_max+y_min)/2)
	z_trans = ((z_max+z_min)/2)

	scale = max(x_max-x_min, y_max-y_min, z_max-z_min)


	for i in vertices:
		i[0] = (i[0]-x_trans)/scale
		i[1] = (i[1]-y_trans)/scale
		i[2] = (i[2]-z_trans)/scale

	return vertices, polygons



def vertex(i):
	x1 = (vertices[i[0]-1][0])
	y1 = (vertices[i[0]-1][1])
	z1 = (vertices[i[0]-1][2])

	x2 = (vertices[i[1]-1][0])
	y2 = (vertices[i[1]-1][1])
	z2 = (vertices[i[1]-1][2])

	x3 = (vertices[i[2]-1][0])
	y3 = (vertices[i[2]-1][1])
	z3 = (vertices[i[2]-1][2])

	return x1, y1, z1, x2, y2, z2, x3, y3, z3



def draw_curve(scale_b):
	dots = []
	glBegin(GL_LINE_STRIP)
	for i in range(len(bspline_vertices)-3+1):
		for j in np.linspace(0, 1, 20):
			temp = ith_segment(j, i)
			temp2 = tangent(j, i)
			dots.append(temp)
			glVertex3f(temp[0]/scale_b, temp[1]/scale_b, temp[2]/scale_b)
			glVertex3f(temp[0]/scale_b + temp2[0]/scale_b, temp[1]/scale_b + temp2[1]/scale_b, temp[2]/scale_b+temp2[2]/scale_b)
	glEnd()



def update(x, dt): 
	global point_t, seg
	point_t += 0.1
	if point_t > 1.0:
		point_t = 0.0
		seg += 1
	if seg >= (len(bspline_vertices) - 3 + 1):
		seg = 0

def draw_object(vertices, polygons):
	glBegin(GL_TRIANGLES)
	for points in polygons:
		for vid in points:
			glColor3f(1.0, 0.0, 0.0)
			glVertex3f(vertices[vid-1][0], vertices[vid-1][1], vertices[vid-1][2])
	glEnd()

@window.event
def on_draw():
	global width
	global height
	global alpha
	global timer
	global seg

	orientation = np.array([0,0,1])
	vertex_ = ith_segment(point_t, seg)
	tangent_ = tangent(point_t, seg)

	os, deg = rotate(orientation, tangent_)
	orientation = tangent_

	glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(75, float(width)/float(height), 0.05, 1000)
	gluLookAt(cameraPositon[0], cameraPositon[1], cameraPositon[2], 
			lookAt[0], lookAt[1], lookAt[2], 
			upVector[0], upVector[1], upVector[2])
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glClearColor(1.0, 1.0, 1.0, 0.0) 
	glClear(GL_COLOR_BUFFER_BIT) 
	glLoadIdentity() 
	draw_curve(scale_b)

	glTranslatef(vertex_[0]/scale_b, vertex_[1]/scale_b, vertex_[2]/scale_b)
	glScalef(1/5, 1/5, 1/5)
	glRotatef(deg, os[0], os[1], os[2])
	draw_object(vertices, polygons)

	

if __name__ == "__main__":	
	bspline_vertices, scale_b = bspline_parse()

	vertices, polygons = object_parse()

	pyglet.clock.schedule(update, 1/20.0)

	pyglet.app.run()
