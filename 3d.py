# Homework for UB DMS 423 - Fall 14
# by Xiaoyu Tai
#
# Real-time Satellite Visualization
# Input Data type: TLS(Two-line element set)
# Can be found at http://www.celestrak.com/NORAD/elements/
# 
# Tweak from global.py from Dr. Dave Pape
# https://gist.github.com/davepape/7324958
#
# Hi-Res Map is from NASA:
# http://earthobservatory.nasa.gov/blogs/elegantfigures/files/2011/10/land_shallow_topo_2011_8192.jpg
#
# How to control:
# Click a satellite to display its orbit.
# Press H to show/hide all orbits on-screen.
# Press UP/DOWN to change satellite category.
# Press LEFT/RIGHT to adjust orbit interval for line drawing.
# 

import ephem, datetime, urllib
from pyglet.gl import *
from math import *

window = pyglet.window.Window(700,700)
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)

def init():
	global resource, tex, step, vlists
	global angle_x, angle_y, v_x, v_y, v_dx, v_dy, zoom
	resource = [["Space Stations",		"stations"],
		["NOAA Weather Satellites",	"noaa"],
		["GPS Operational", 		"gps-ops"],
		["Intelsat Satellites", 	"intelsat"],
		["Science Satellites", 		"science"],
		["Miscellaneous Military",	"military"],
		["Last 30 Days' Launches", 	"tle-new"]]

	# tex = pyglet.image.load('assets/blue.jpg').get_texture()
	tex = pyglet.image.load('assets/c.jpg').get_texture()
	# tex = pyglet.image.load('assets/map.png').get_texture()
	step = 5
	vlists = []
	for lat in range(-90,90,step):
		verts = []
		texc = []
		noramls = []
		for lon in range(-180,181,step):
			x = -cos(radians(lat)) * cos(radians(lon)) 
			y = sin(radians(lat))
			z = cos(radians(lat)) * sin(radians(lon))
			s = (lon+180) / 360.0
			t = (lat+90) / 180.0
			verts += [x,y,z]
			texc += [s,t]
			noramls += [x,y,z]
			x = -cos(radians((lat+step))) * cos(radians(lon))
			y = sin(radians((lat+step)))
			z = cos(radians((lat+step))) * sin(radians(lon))
			s = (lon+180) / 360.0
			t = ((lat+step)+90) / 180.0
			verts += [x,y,z]
			texc += [s,t]
			noramls += [x,y,z]
		vlist = pyglet.graphics.vertex_list(len(verts)/3, ('v3f', verts), ('t2f', texc), ('n3f', noramls))
		vlists.append(vlist)

	angle_x = -170
	angle_y = -30
	v_x = 0
	v_y = 0
	v_dx = 0
	v_dy = 0
	zoom = 80

	glEnable(GL_DEPTH_TEST)
	# glEnable(GL_LIGHTING)
	# glEnable(GL_LIGHT0)

@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	# glOrtho(-1,1,-1,1,-1,1)
	gluPerspective(2, 1, 0.1, 10000.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslatef(0,0,-zoom)
	glRotatef(-angle_y, 1, 0, 0)
	glRotatef(angle_x, 0, 1, 0)
	# glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat*4)(*[0, -0.4, -1, 0]))
	# glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (GLfloat*4)(*[1, 1, 1, 1]))
	# glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat*4)(*[1.0, 1.0, 1.0, 0]))
	glColor3f(1,1,1)
	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, tex.id)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	for v in vlists:
		v.draw(GL_TRIANGLE_STRIP)
	glDisable(GL_TEXTURE_2D)

def update(dt):
	global angle_x, angle_y, zoom
	# angle_x += 0.5
	keys_control()
	velocity_control()
	if angle_x > 360 or angle_x < -360:
		angle_x = 0
	if zoom < 10:
		zoom = 10
	elif zoom > 300:
		zoom = 300

def keys_control():
	global angle_x, angle_y, keys, zoom
	if keys[pyglet.window.key.LEFT]:
		angle_x += 0.5
	elif keys[pyglet.window.key.RIGHT]:
		angle_x -= 0.5
	if keys[pyglet.window.key.DOWN]:
		if angle_y + 0.5 > 88:
			angle_y = 88
		else:
			angle_y += 0.5
	elif keys[pyglet.window.key.UP]:
		if angle_y - 0.5 < -88:
			angle_y = -88
		else:
			angle_y -= 0.5
	if keys[pyglet.window.key.Z]:
		zoom *= 1.03
	elif keys[pyglet.window.key.X]:
		zoom /= 1.03
	if keys[pyglet.window.key.N]:
		angle_x,angle_y,zoom = -170,-30,80

def velocity_control():
	global angle_x, angle_y, v_x, v_y, v_dx, v_dy
	global x_plus, y_plus
	angle_x += v_x
	angle_y += v_y
	if angle_y - 0.5 < -88:
		angle_y = -88
		v_dy,v_y = 0,0
	elif angle_y + 0.5 > 88:
		angle_y = 88
		v_dy,v_y = 0,0
	v_x += v_dx
	v_y += v_dy
	if abs(v_x) < 1:
		v_dx = 0
		v_x = 0
	else:
		v_dx = x_plus
	if abs(v_y) < 1:
		v_dy = 0
		v_y = 0
	else:
		v_dy = y_plus

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global angle_x, angle_y, zoom, v_x, v_y, x_plus, y_plus
	temp = 0.0025 * zoom
	angle_x += temp*dx
	if angle_y + temp*dy > 88:
		angle_y = 88
	elif angle_y + temp*dy < -88:
		angle_y = -88
	else:
		angle_y += temp*dy
	if dx > 0:
		x_plus = temp*-5
	else:
		x_plus = temp*5
	if dy > 0:
		y_plus = temp*-5
	else:
		y_plus = temp*5
	v_x = temp*dx
	v_y = temp*dy


init()
pyglet.clock.schedule_interval(update,1/60.0)
pyglet.app.run()