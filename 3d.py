from pyglet.gl import *
from math import *

tex = pyglet.image.load('assets/map.png').get_texture()

step = 10

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

window = pyglet.window.Window(700,700)
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)

angle_x = -170
angle_x_light = 0
angle_y = -30
zoom = 80


glEnable(GL_DEPTH_TEST)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)

@window.event
def on_draw():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	# glOrtho(-1,1,-1,1,-1,1)
	gluPerspective(zoom, 1, 0.1, 10000.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslatef(0,0,-2)
	glRotatef(-angle_y, 1, 0, 0)
	glRotatef(angle_x, 0, 1, 0)
	glLightfv(GL_LIGHT0, GL_POSITION, (GLfloat*4)(*[0, -0.4, -1, 0]))
	# glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat*4)(*[1, 1, 1, 1]))
	# glMaterialfv(GL_FRONT, GL_SPECULAR, (GLfloat*4)(*[1, 1, 1, 0.5]))
	# glMaterialf(GL_FRONT, GL_SHININESS, 80)
	glRotatef(angle_x_light, 0, 1, 0)
	glColor3f(1,1,1)
	glEnable(GL_TEXTURE_2D)
	glBindTexture(GL_TEXTURE_2D, tex.id)
	glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
	# glShadeModel(GL_FLAT)
	for v in vlists:
		v.draw(GL_TRIANGLE_STRIP)
		# v.draw(GL_LINE_STRIP)
	glDisable(GL_TEXTURE_2D)

def update(dt):
	global angle_x, angle_y, keys, zoom, angle_x_light
	angle_x_light += 0.5
	if keys[pyglet.window.key.LEFT]:
		angle_x += 1
	elif keys[pyglet.window.key.RIGHT]:
		angle_x -= 1
	if keys[pyglet.window.key.SPACE]:
		angle_x_light -= 1
	if keys[pyglet.window.key.UP]:
		if angle_y + 1 > 60:
			angle_y = 60
		else:
			angle_y += 1
	elif keys[pyglet.window.key.DOWN]:
		if angle_y - 1 < -60:
			angle_y = -60
		else:
			angle_y -= 1
	if keys[pyglet.window.key.Z]:
		zoom += 1
	elif keys[pyglet.window.key.X]:
		zoom -= 1

	if keys[pyglet.window.key.N]:
		angle_x,angle_y,zoom = -170,-30,80
	
	if angle_x > 360 or angle_x < -360:
		angle_x = 0
	if zoom < 40:
		zoom = 40
	elif zoom > 160:
		zoom = 160
	print angle_x, angle_y

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
	global angle_x, angle_y
	if abs(dx)>abs(dy):
		angle_x += dx
	else:
		if angle_y + dy > 60:
			angle_y = 60
		elif angle_y + dy < -60:
			angle_y = -60
		else:
			angle_y += dy
			

pyglet.clock.schedule_interval(update,1/60.0)
pyglet.app.run()