Real-Time-Satellite-Tracking
============================

Tracking satellites in real time form TLS data.  

Using Python + [pyglet](http://www.pyglet.org) OpenGL library + [PyEphem](http://rhodesmill.org/pyephem/) library

## Input

Data type: TLS (Two-line element set)  
Can be found at [www.celestrak.com](http://www.celestrak.com/NORAD/elements/)

## 2D version

file: `2d.py`  

How to control:  

- Click a satellite to display its orbit.
- Press H to show/hide all orbits on-screen.
- Press UP/DOWN to change satellite category.
- Press LEFT/RIGHT to adjust orbit interval for line drawing.

## 3D version

file: `3d.py`  

Current Control:  

- Press Z/X to zoom in or out.
- Press arrow keys to rotate the global.

## Sample Data

Satellites Category | File Name (inside `/data/`)
------------ | ------------- 
Space Stations | stations.txt
NOAA Weather Satellites | noaa.txt
GPS Operational | gps-ops.txt
Intelsat Satellites | intelsat.txt
Science Satellites | science.txt
Miscellaneous Military | military.txt
Last 30 Days' Launches | tle-new.txt

## License

MIT
