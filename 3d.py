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
# Press UP/DOWN/LEFT/RIGHT to rotate the globe
# Drag the mouse to feel the 
# 

import ephem, datetime, urllib2, json, math
from pyglet.gl import *
from math import *

window = pyglet.window.Window(700,700)
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)

resource = [["Space Stations",		"stations"],
	["NOAA Weather Satellites",	"noaa"],
	["GPS Operational", 		"gps-ops"],
	["Intelsat Satellites", 	"intelsat"],
	["Science Satellites", 		"science"],
	["Miscellaneous Military",	"military"],
	["Last 30 Days' Launches", 	"tle-new"]]

def open_new_file(num):
	global source, lines, sats, show_all_line
	source = open("data/"+resource[num][1] + ".txt")
	print resource[num][0]
	# Uncomment following lines for online access
	# name = resource[num][1]
	# url = "http://www.celestrak.com/NORAD/elements/" + name +".txt"
	# source = urllib.urlopen(url)
	lines = [line.replace("\r\n", "") for line in source]
	sats = []
	show_all_line = 0
	for x in xrange(len(lines) / 3):
		e = Satellite(lines[x * 3], lines[x * 3 + 1], lines[x * 3 + 2], 64)
		e.compute()
		sats.append(e)

class Satellite:
	def __init__(self, name, l1, l2, yoffset):
		self.e        = ephem.readtle(name, l1, l2)
		self.size     = 4
		self.showline = 0
		self.yoffset  = yoffset
	def compute(self):
		self.e.compute(datetime.datetime.utcnow())
		self.long   = math.degrees(float(self.e.sublong))
		self.lat    = math.degrees(float(self.e.sublat))
		self.height = abs(int(self.e.elevation))
		r = 6378150 + self.height
		self.r = float(r)/1000000
		self.x      = -cos(radians(self.lat)) * cos(radians(self.long)) * self.r
		self.y      = sin(radians(self.lat)) * self.r
		self.z      = cos(radians(self.lat)) * sin(radians(self.long)) * self.r
		self.vlists  = sat_shape
		self.label = pyglet.text.Label(self.e.name, y=15, anchor_x="center", color=(255,255,255,200))
	def draw(self):
		glLoadIdentity()
		glTranslatef(0,0,-zoom+6.37815)
		glRotatef(ro, 1, 0, 0)
		glRotatef(rocc, 0, 0, 1)
		glTranslatef(0,0,-6.37815)
		glRotatef(-angle_y, 1, 0, 0)
		glRotatef(angle_x, 0, 1, 0)
		glTranslatef(self.x,self.y,self.z)
		glColor3f(1,0,0)
		glScalef(zoom/65, zoom/65, zoom/65)
		for v in self.vlists:
			v.draw(GL_TRIANGLE_STRIP)
		glScalef(0.01, 0.01, 0.01)
		glRotatef(-angle_x, 0, 1, 0)
		glRotatef(angle_y, 1, 0, 0)
		glRotatef(-rocc, 0, 0, 1)
		glRotatef(-ro, 1, 0, 0)
		self.label.draw()
		self.draw_line()
	def draw_line(self):
		self.init_line()
		glLoadIdentity()
		# glEnable(GL_BLEND)
		glTranslatef(0,0,-zoom+6.37815)
		glRotatef(ro, 1, 0, 0)
		glRotatef(rocc, 0, 0, 1)
		glTranslatef(0,0,-6.37815)
		glRotatef(-angle_y, 1, 0, 0)
		glRotatef(angle_x, 0, 1, 0)
		# glColor3f(1,0,0)
		glColor4f(1,0,0,0)
		for x in self.vline_list:
			x.draw(GL_LINE_STRIP)
		# glDisable(GL_BLEND)
	def init_line(self):
		self.lines, self.vline_list, current_line = [], [], []
		for x in xrange(-20,20):
			temp = datetime.datetime.utcnow() + datetime.timedelta(seconds=80*x)
			self.e.compute(temp)
			lon   = math.degrees(float(self.e.sublong))
			lat    = math.degrees(float(self.e.sublat))
			r = 6378150 + abs(int(self.e.elevation))
			r = float(r)/1000000
			x      = -cos(radians(lat)) * cos(radians(lon)) * r
			y      = sin(radians(lat)) * r
			z      = cos(radians(lat)) * sin(radians(lon)) * r
			current_line.extend((x,y,z))
		self.lines.append(current_line)
		for x in self.lines:
			self.vline_list.append(pyglet.graphics.vertex_list(len(x)/3, ("v3f", x)))


def init():
	global resource, tex, tex2, step, vlists
	global angle_x, angle_y, v_x, v_y, v_dx, v_dy, zoom
	global geo, sat_shape, ro, rocc
	ro,rocc = 0,0
	sat_shape = satellite_shape()
	open_new_file(1)
	geo = 1
	tex = pyglet.image.load('assets/map_4096.jpg').get_texture()
	tex2 = pyglet.image.load('assets/s.png').get_texture()
	step = 6
	vlists = []
	r = 6.37815
	for lat in range(-90,90,step):
		verts = []
		texc = []
		noramls = []
		for lon in range(-180,181,step):
			x = -cos(radians(lat)) * cos(radians(lon)) * r
			y = sin(radians(lat)) * r
			z = cos(radians(lat)) * sin(radians(lon)) * r
			s = (lon+180) / 360.0
			t = (lat+90) / 180.0
			verts += [x,y,z]
			texc += [s,t]
			noramls += [x,y,z]
			x = -cos(radians((lat+step))) * cos(radians(lon)) * r
			y = sin(radians((lat+step))) * r
			z = cos(radians((lat+step))) * sin(radians(lon)) * r
			s = (lon+180) / 360.0
			t = ((lat+step)+90) / 180.0
			verts += [x,y,z]
			texc += [s,t]
			noramls += [x,y,z]
		vlist = pyglet.graphics.vertex_list(len(verts)/3, ('v3f', verts), ('t2f', texc), ('n3f', noramls))
		vlists.append(vlist)

	#42.8864468, -78.78897	

	angle_x = 168.78897
	angle_y = -43.000809
	v_x = 0
	v_y = 0
	v_dx = 0
	v_dy = 0
	zoom = 65

	glEnable(GL_DEPTH_TEST)
	# glEnable(GL_LIGHTING)
	# glEnable(GL_LIGHT0)


@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	# glOrtho(-1,1,-1,1,-1,1)
	gluPerspective(10, 1, 0.1, 10000.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslatef(0,0,-zoom+6.37815)
	glRotatef(ro, 1, 0, 0)
	glRotatef(rocc, 0, 0, 1)
	glTranslatef(0,0,-6.37815)
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
	glBindTexture(GL_TEXTURE_2D, tex2.id)
	for s in sats:
		s.draw()
	glDisable(GL_TEXTURE_2D)

def update(dt):
	global angle_x, angle_y, zoom, ro, rocc
	# angle_x += 0.5
	for x in sats:
		x.compute()
	keys_control()
	velocity_control()
	if (-angle_x+90) > 180:
		angle_x = 180+90
	if (-angle_x+90) < -180:
		angle_x = -180+90
	if zoom < 8:
		zoom = 8
	elif zoom > 1000:
		zoom = 1000
	if ro < -90:
		ro = -90
	elif ro > 90:
		ro = 90
	if rocc < -180:
		rocc = 180
	elif rocc > 180:
		rocc = -180
	if not geo:
		print "lat: "+str(-angle_y)+", long: "+str(-angle_x+90)
		print formatted_address(geocoding(-angle_y,-angle_x+90))

def keys_control():
	global angle_x, angle_y, keys, zoom, geo, ro, rocc
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
	if keys[pyglet.window.key.A]:
		ro += 1
	elif keys[pyglet.window.key.S]:
		ro -= 1
	elif keys[pyglet.window.key.D]:
		ro = 0
	if keys[pyglet.window.key.Q]:
		rocc += 1
	elif keys[pyglet.window.key.W]:
		rocc -= 1
	elif keys[pyglet.window.key.E]:
		rocc = 0
	if keys[pyglet.window.key.N]:
		angle_x,angle_y,zoom = -170,-30,80
	if keys[pyglet.window.key.G]:
		geo = 0

def velocity_control():
	global angle_x, angle_y, v_x, v_y, v_dx, v_dy
	global x_plus, y_plus, zoom
	temp = 0.012 * zoom
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
	if abs(v_x) < temp:
		v_dx,v_x = 0,0
	else:
		v_dx = x_plus
	if abs(v_y) < temp:
		v_dy,v_y = 0,0
	else:
		v_dy = y_plus

def geocoding(lat, lng):
	global geo
	data = json.dumps([])
	APIkey = "AIzaSyB4J_tdS0mjqgE1QwdYwPu-EFYyp6ZpGng"
	url = "https://maps.googleapis.com/maps/api/geocode/json?latlng="+str(lat)+","+str(lng)+"&key="+APIkey
	req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
	f = urllib2.urlopen(req)
	response = f.read()
	d = json.loads(response)
	f.close()
	geo = 1
	return d

def formatted_address(d):
	if len(d['results']):
		return d['results'][0]['formatted_address'].encode('utf-8')
	else:
		return "nowhere"

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
		x_plus = temp*-2
	else:
		x_plus = temp*2
	if dy > 0:
		y_plus = temp*-2
	else:
		y_plus = temp*2
	v_x,v_y = temp*dx, temp*dy

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
	global angle_x, angle_y, zoom, v_x, v_y, x_plus, y_plus
	temp = 0.005 * zoom
	angle_x += temp*scroll_x*5
	if angle_y + temp*-scroll_y > 88:
		angle_y = 88
	elif angle_y + temp*-scroll_y < -88:
		angle_y = -88
	else:
		angle_y += temp*-scroll_y*5
	if scroll_x > 0:
		x_plus = temp*-2
	else:
		x_plus = temp*2
	if -scroll_y > 0:
		y_plus = temp*-2
	else:
		y_plus = temp*2
	v_x,v_y = temp*scroll_x*5, temp*-scroll_y*5

def satellite_shape():
	# step = 60
	# vlists = []
	# for lat in range(-90,90,step):
	# 	verts = []
	# 	texc = []
	# 	noramls = []
	# 	r = 0.07
	# 	for lon in range(-180,181,step):
	# 		x = -cos(radians(lat)) * cos(radians(lon)) * r
	# 		y = sin(radians(lat)) * r
	# 		z = cos(radians(lat)) * sin(radians(lon)) * r
	# 		s = (lon+180) / 360.0
	# 		t = (lat+90) / 180.0
	# 		verts += [x,y,z]
	# 		texc += [s,t]
	# 		noramls += [x,y,z]
	# 		x = -cos(radians((lat+step))) * cos(radians(lon)) * r
	# 		y = sin(radians((lat+step))) * r
	# 		z = cos(radians((lat+step))) * sin(radians(lon)) * r
	# 		s = (lon+180) / 360.0
	# 		t = ((lat+step)+90) / 180.0
	# 		verts += [x,y,z]
	# 		texc += [s,t]
	# 		noramls += [x,y,z]
		

	# 	vlist = pyglet.graphics.vertex_list(len(verts)/3, ('v3f', verts), ('t2f', texc), ('n3f', noramls))
	# 	vlists.append(vlist)
	# return vlists
	r = 0.07
	vlists = []
	verts = []
	texc = []
	noramls = []
	verts += [-r,r,r]
	verts += [-r,-r,r]
	verts += [r,r,r]
	verts += [r,-r,r]
	verts += [r,-r,-r]
	verts += [r,r,r]
	verts += [r,r,-r]
	verts += [-r,r,r]
	verts += [-r,r,-r]
	verts += [-r,-r,r]
	verts += [-r,-r,-r]
	verts += [r,-r,r]
	verts += [r,-r,-r]
	verts += [r,r,-r]
	verts += [-r,-r,-r]
	verts += [-r,r,-r]

	noramls = verts
	vlist = pyglet.graphics.vertex_list(len(verts)/3, ('v3f', verts), ('n3f', noramls))
	vlists.append(vlist)
	return vlists

init()
pyglet.clock.schedule_interval(update,1/60.0)
pyglet.app.run()