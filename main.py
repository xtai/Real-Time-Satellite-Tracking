# Homework for UB DMS 423 - Fall 14
# by Xiaoyu Tai
#
# Real-time Satellite Visualization
# Input Data type: TLS(Two-line element set)
# Can be found at http://www.celestrak.com/NORAD/elements/
# 
# How to control:
# Click a satellite to display its orbit.
# Press H to show/hide all orbits on-screen.
# Press UP/DOWN to change satellite category.
# Press LEFT/RIGHT to adjust orbit interval for line drawing.
# 


import ephem, datetime, math, urllib
from pyglet.gl import *

resource = [["Space Stations", 			"stations"],
			["NOAA Weather Satellites", "noaa"],
			["GPS Operational", 		"gps-ops"],
			["Intelsat Satellites", 	"intelsat"],
			["Science Satellites", 		"science"],
			["Miscellaneous Military",	"military"],
			["Last 30 Days' Launches", 	"tle-new"]]

window   = pyglet.window.Window(1024,576)
total    = 50
interval = 20

class Background:
	def __init__(self, x,y, xoffset,yoffset, texturefile):
		self.texture = pyglet.image.load(texturefile).get_texture()
		self.vlist = pyglet.graphics.vertex_list(4, ('v2f', [xoffset,yoffset, xoffset+x,yoffset, xoffset,yoffset+y, xoffset+x,yoffset+y]), ('t2f', [0,0, 1,0, 0,1, 1,1]))
	def draw(self):
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glColor3f(1,1,1)
		glEnable(GL_TEXTURE_2D)
		glBindTexture(GL_TEXTURE_2D, self.texture.id)
		glPushMatrix()
		self.vlist.draw(GL_TRIANGLE_STRIP)
		glPopMatrix()
		glBindTexture(GL_TEXTURE_2D, 0)
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_BLEND)

class Satellite:
	def __init__(self, name, l1, l2, yoffset):
		self.e        = ephem.readtle(name, l1, l2)
		self.vlist    = pyglet.graphics.vertex_list(4, ("v2f",[-1,1, -1,-1, 1,-1, 1,1]))
		self.size     = 4
		self.showline = 0
		self.yoffset  = yoffset
	def compute(self):
		self.e.compute(datetime.datetime.utcnow())
		self.long  = math.degrees(float(self.e.sublong))
		self.lat   = math.degrees(float(self.e.sublat))
		self.x     = (self.long * 128/45) + 512
		self.y     = (self.lat * 128/45) + 256 + self.yoffset
		self.label = pyglet.text.Label(self.e.name, x=7,y=0, anchor_y="center", color=(255,255,255,255))
	def draw(self):
		glEnable(GL_BLEND)
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
		glColor4f(1,0,0,1)
		glPushMatrix()
		glTranslatef(self.x, self.y, 0)
		glRotatef(30, 0, 0, 1)
		self.label.draw()
		glScalef(self.size, self.size, self.size)
		self.vlist.draw(GL_TRIANGLE_FAN)
		glPopMatrix()
		glDisable(GL_TEXTURE_2D)
		glDisable(GL_BLEND)
	def draw_line(self):
		self.init_line()
		glEnable(GL_BLEND)
		glColor4f(1,0,0,self.showline)
		glPushMatrix()
		for x in self.vline_list:
			x.draw(GL_LINE_STRIP)
		glPopMatrix()
		glDisable(GL_BLEND)
	def init_line(self):
		self.lines, self.vline_list, current_line = [], [], []
		for x in xrange(-total,total):
			temp = datetime.datetime.utcnow() + datetime.timedelta(seconds=interval*x)
			self.e.compute(temp)
			x = (math.degrees(float(self.e.sublong)) * 128/45) + 512
			y = (math.degrees(float(self.e.sublat)) * 128/45) + 256 + self.yoffset
			if len(current_line) > 1:
				# TO AVOID LINE FROM LEFT TO RIGHT
				temp_x, temp_y = current_line[-2], current_line[-1]
				if temp_x - x > 600:
					# From right edge to left edge
					current_line.extend((x+1024,y))
					self.lines.append(current_line)
					current_line = []
					current_line.extend((temp_x-1024,temp_y))
				elif temp_x - x < -600:
					# From left edge to right edge
					current_line.extend((x-1024,y))
					self.lines.append(current_line)
					current_line = []
					current_line.extend((temp_x+1024,temp_y))
			current_line.extend((x,y))
		self.lines.append(current_line)
		for x in self.lines:
			self.vline_list.append(pyglet.graphics.vertex_list(len(x)/2, ("v2f", x)))

def init():
	global background_map, background_banner, category_num
	global text_current_set, text_current_time, text_infos, text_infos_2, text_infos_3
	open_new_file(0)
	category_num      = 0
	background_map    = Background(1024,512,0,64,"assets/blue.jpg")
	background_banner = Background(1024,128,0,0,"assets/bg.png")
	text_current_set  = pyglet.text.Label("Satellites Category on Screen: " + resource[category_num][0], x=15, y=42, anchor_y="center", color=(255,255,255,200))
	text_current_time = pyglet.text.Label("Current UTC Time: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), x=15, y=22, anchor_y="center", color=(255,255,255,200))
	text_infos        = pyglet.text.Label("Click a satellite to display its orbit, Press H to show/hide all orbits on-screen.", x=460, y=50, anchor_y="center", color=(255,255,255,200))
	text_infos_2      = pyglet.text.Label("Press UP/DOWN to change satellite category.", x=460, y=32, anchor_y="center", color=(255,255,255,200))
	text_infos_3      = pyglet.text.Label("Press LEFT/RIGHT to adjust orbit interval for line drawing.", x=460, y=14, anchor_y="center", color=(255,255,255,200))

@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT)
	background_map.draw()
	background_banner.draw()
	text_current_set.draw()
	text_current_time.draw()
	text_infos.draw()
	text_infos_2.draw()
	text_infos_3.draw()
	for x in sats:
		x.draw()
		x.draw_line()

def update(dt):
	global text_current_time, text_current_set
	text_current_time = pyglet.text.Label("Current UTC Time: " + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), x=15, y=22, anchor_y="center", color=(255,255,255,200))
	text_current_set  = pyglet.text.Label("Satellites Category on Screen: " + resource[category_num][0], x=15, y=42, anchor_y="center", color=(255,255,255,200))
	for x in sats:
		x.compute()

def distance(a, b):
	return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

def open_new_file(num):
	global source, lines, sats, show_all_line
	source = open("data/"+resource[num][1] + ".txt")
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

@window.event
def on_mouse_press(x,y, dx,dy):
	global show_all_line
	show_all_line = 0
	refresh_all_line([None])
	for o in sats:
		if distance((o.x,o.y), (x,y)) <= o.size ** 2:
			o.showline = int(not o.showline)
			refresh_all_line([o])

def refresh_all_line(withouts):
	for o in sats:
		for w in withouts:
			if o!= w:
				o.showline = show_all_line

@window.event
def on_key_press(symbol, modifiers):
	global show_all_line, category_num, interval
	if symbol == pyglet.window.key.H:
		show_all_line = not show_all_line
		refresh_all_line([None])
	elif symbol == pyglet.window.key.UP:
		category_num += 1
		if category_num == len(resource):
			category_num = 0
		open_new_file(category_num)
		update(0)
	elif symbol == pyglet.window.key.DOWN:
		category_num -= 1
		if category_num == -1:
			category_num = len(resource)-1
		open_new_file(category_num)
		update(0)
	elif symbol == pyglet.window.key.LEFT:
		interval -= 20
		if interval < 10:
			interval = 10
	elif symbol == pyglet.window.key.RIGHT:
		interval += 20
		if interval > 500:
			interval = 500

init()
pyglet.clock.schedule_interval(update, 1/1.0)
pyglet.app.run()