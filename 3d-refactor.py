# Final Project for UB DMS 423 - Fall 14
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
# Press UP/DOWN/LEFT/RIGHT to rotate the globe
# Drag the mouse to feel the 
# 

import ephem, datetime, urllib2, json
from pyglet.gl import *
from pyglet.window import *
from math import *

window = pyglet.window.Window(700,700)
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)

class Satel:
	def __init__(self, name, line_1, line_2):
		self.ep    = ephem.readtle(name, line_1, line_2)
		self.vlist = satel_vlist
		self.label = pyglet.text.Label(self.ep.name, y=15, anchor_x="center", color=(255,255,255,200))
		self.compute()
	def compute(self):
		self.ep.compute(datetime.datetime.utcnow())
		self.lat    = degrees(float(self.ep.sublat))
		self.long   = degrees(float(self.ep.sublong))
		self.height = abs(int(self.ep.elevation))
		self.radius = (6378150 + self.height)/1000000.0
		self.x      = -cos(radians(self.lat)) * cos(radians(self.long)) * self.radius
		self.y      = sin(radians(self.lat)) * self.radius
		self.z      = cos(radians(self.lat)) * sin(radians(self.long)) * self.radius
	def draw(self):
		glLoadIdentity()
		glTranslatef(0,0,-zoom+6.37815)    # axis rotate by earth's surface
		glRotatef(gyration[1][0], 1, 0, 0) # x-axis rotation 
		glRotatef(gyration[1][1], 0, 0, 1) # z-axis rotation 
		glTranslatef(0,0,-6.37815)            # rotate by earth's center
		glRotatef(gyration[0][0], 1, 0, 0)    # latitude rotation
		glRotatef(90-gyration[0][1], 0, 1, 0) # longitude rotation
		glTranslatef(self.x,self.y,self.z)
		glColor3f(1,0,0)
		glScalef(zoom/100.0, zoom/100.0, zoom/100.0)
		self.vlist.draw(GL_TRIANGLE_STRIP)
		glScalef(0.02, 0.02, 0.02)
		glRotatef(gyration[0][1]-90, 0, 1, 0)
		glRotatef(-gyration[0][0], 1, 0, 0)
		glRotatef(-gyration[1][1], 0, 0, 1)
		glRotatef(-gyration[1][0], 1, 0, 0)
		self.label.draw()
		# self.draw_line()

def init():
	glEnable(GL_DEPTH_TEST)

	global zoom, gyration
	gyration = []
	zoom = 100.0
	gyration.append([43.000809, -78.78897]) # latitude, longitude
	gyration.append([0, 0]) # x-axis, z-axis

	global earth_texture, earth_vlists
	earth_texture = pyglet.image.load('assets/map_4096.jpg').get_texture()
	earth_vlists, step, radius = [], 9, 6.37815
	for lat in range(-90,90,step):
		verts, texc = [], []
		for lon in range(-180,181,step):
			x1 = -cos(radians(lat)) * cos(radians(lon)) * radius
			y1 = sin(radians(lat)) * radius
			z1 = cos(radians(lat)) * sin(radians(lon)) * radius
			s1 = (lon + 180) / 360.0
			t1 = (lat + 90) / 180.0
			x2 = -cos(radians((lat+step))) * cos(radians(lon)) * radius
			y2 = sin(radians((lat+step))) * radius
			z2 = cos(radians((lat+step))) * sin(radians(lon)) * radius
			s2 = (lon + 180) / 360.0
			t2 = ((lat + step) + 90) / 180.0
			verts += [x1,y1,z1, x2,y2,z2]
			texc += [s1,t1, s2,t2]
		earth_vlists.append(pyglet.graphics.vertex_list(len(verts)/3, ('v3f', verts), ('t2f', texc), ('n3f', verts)))

	global satel_vlist
	# Don't panic, it's just a cude below (GL_TRIANGLE_STRIP)
	r = 0.08
	verts = [-r,r,r,-r,-r,r,r,r,r,r,-r,r,r,-r,-r,r,r,r,r,r,-r,-r,r,r,-r,r,-r,-r,-r,r,-r,-r,-r,r,-r,r,r,-r,-r,r,r,-r,-r,-r,-r,-r,r,-r]
	satel_vlist = pyglet.graphics.vertex_list(len(verts)/3, ('v3f', verts), ('n3f', verts))

	load(1)

def load(num):
	global resource, satels
	resource = [["Space Stations",		"stations"],
		["NOAA Weather Satellites",	"noaa"],
		["GPS Operational", 		"gps-ops"],
		["Intelsat Satellites", 	"intelsat"],
		["Science Satellites", 		"science"],
		["Miscellaneous Military",	"military"],
		["Last 30 Days' Launches", 	"tle-new"]]
	name = resource[num][1]
	# Loacl source
	source = open("data/"+name + ".txt")
	# Online source
	# source = urllib.urlopen("http://www.celestrak.com/NORAD/elements/" + name +".txt")
	lines = [line.replace("\r\n", "") for line in source]
	print "Current Satellites Set: " + name
	satels = []
	for x in xrange(len(lines) / 3):
		satels.append(Satel(lines[x * 3], lines[x * 3 + 1], lines[x * 3 + 2]))

@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION)
	draw_earth()
	draw_satellites()
	draw_info()

def draw_earth():
	glLoadIdentity()
	gluPerspective(10, 1, 0.1, 10000.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslatef(0,0,-zoom+6.37815)    # axis rotate by earth's surface
	glRotatef(gyration[1][0], 1, 0, 0) # x-axis rotation 
	glRotatef(gyration[1][1], 0, 0, 1) # z-axis rotation 
	glTranslatef(0,0,-6.37815)            # rotate by earth's center
	glRotatef(gyration[0][0], 1, 0, 0)    # latitude rotation
	glRotatef(90-gyration[0][1], 0, 1, 0) # longitude rotation
	glColor3f(1,1,1)
	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, earth_texture.id)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	for v in earth_vlists:
		v.draw(GL_TRIANGLE_STRIP)
	glDisable(GL_TEXTURE_2D)

def draw_satellites():
	for s in satels:
		s.draw()

def draw_info():
	glDisable(GL_DEPTH_TEST)
	glLoadIdentity()
	title = pyglet.text.Label("DMS 423 Final Project A, Real-time Satellite Visualization", color=(255,255,255,200))
	name = pyglet.text.Label("Xiaoyu Tai (50133396)", color=(255,255,255,100))
	draw_info_d(title, -6.8, 6.5)
	draw_info_d(name, 3.5, 6.5)
	glEnable(GL_DEPTH_TEST)

def draw_info_d(label, x, y):
	glLoadIdentity()
	glTranslatef(x,y,-80)
	glScalef(0.02, 0.02, 0.02)
	label.draw()

def update(dt):
	contorl()
	global zoom, gyration
	zoom           = scope(zoom, 8, 1000)
	gyration[0][0] = scope(gyration[0][0],  -89,  89)
	gyration[0][1] = reach(gyration[0][1], -180, 180)
	gyration[1][0] = scope(gyration[1][0],  -90,  90)
	gyration[1][1] = reach(gyration[1][1], -180, 180)
	for s in satels:
		s.compute()

def scope(current, min, max): # limit then keep
	if   current < min: return min
	elif current > max: return max
	else:               return current

def reach(current, min, max): # limit then swap
	if   current < min: return max
	elif current > max: return min
	else:               return current

def contorl():
	global gyration, zoom
	gyration[0][1] = opposite([keys[key.LEFT], keys[key.RIGHT]], gyration[0][1], 0.5)
	gyration[1][0] = opposite([keys[key.S], keys[key.W]], gyration[1][0], 1)
	gyration[1][1] = opposite([keys[key.A], keys[key.D]], gyration[1][1], 1)
 	
 	# Special Configuration to Prevent QUIVER
	if keys[pyglet.window.key.DOWN]:
		if gyration[0][0]+0.5 >  88: gyration[0][0] = 88
		else:                        gyration[0][0] += 0.5
	elif keys[pyglet.window.key.UP]:
		if gyration[0][0]-0.5 < -88: gyration[0][0] = -88
		else:                        gyration[0][0] -= 0.5
	
	# Special Configuration for zoom
	if keys[pyglet.window.key.Z]: zoom *= 1.03
	elif keys[pyglet.window.key.X]: zoom /= 1.03

	# Reset
	if keys[pyglet.window.key.N]: # Reset all rotation
		gyration, zoom = [[43.000809, -78.78897], [0, 0]], 100
	if keys[pyglet.window.key.Q]: # Reset x-axis rotation
		gyration[1][0] = 0
	if keys[pyglet.window.key.E]: # Reset z-axis rotation
		gyration[1][1] = 0

def opposite(key, var, step):
	if   key[0]: var += step
	elif key[1]: var -= step
	return var

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global gyration
	gyration[0][1] -= 0.0025 * zoom * dx
	d = 0.0025 * zoom * dy

	# Special Configuration to Prevent QUIVER
	if   gyration[0][0] - d > 88:  gyration[0][0]  = 88
	elif gyration[0][0] - d < -88: gyration[0][0]  = -88
	else:                          gyration[0][0] -= d

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
	global zoom
	zoom += scroll_y

init()
pyglet.clock.schedule_interval(update,1/60.0)
pyglet.app.run()