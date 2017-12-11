from __future__ import division
import matplotlib.pyplot as plt
import pandas
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
import numpy as np

def plot_panels():
	p = 1
	shading_threshold = .2 # for HALF a panel
	r12 = 2
	t1 = np.radians(-45)
	t2 = np.radians(0)
	h1 = 1.5
	h2 = 1.5
	x = [p/2*np.cos(t1),     0, 0, r12, r12, r12-p/2*np.cos(t1)]
	y = [h1+p/2*np.sin(t1), h1, 0,   0,  h2, h2-p/2*np.sin(t1)]
	det_x = [p*(1-shading_threshold)/2*np.cos(t1)]
	det_y = [p*(1-shading_threshold)/2*np.sin(t1)+h1]
	x2 = [r12, r12-p/2*np.cos(t2)]
	y2 = [h2, h2-p/2*np.sin(t2)]
	l1_x = [det_x[0],x[-1]]
	l1_y = [det_y[0],y[-1]]
	l2_x = [x[0],x2[-1]]
	l2_y = [y[0],y2[-1]]
	a1 = np.degrees(np.arctan((l1_y[1]-l1_y[0])/(l1_x[1]-l1_x[0])))
	a2 = np.degrees(np.arctan((l2_y[1]-l2_y[0])/(l2_x[1]-l2_x[0])))
	plt.plot(x,y,'b-')
	plt.plot(x2,y2,'b--')
	plt.plot(det_x,det_y,'ro')
	plt.plot(l1_x,l1_y,'r--')
	plt.plot(l2_x,l2_y,'r--')
	plt.grid()
	plt.axis('equal')
	plt.title('Angle 1: %.2f, Angle 2: %.2f, Delta: %.2f' % (a1,a2,a1-a2))
	plt.show()

def plot_berkeley():
	csv = pandas.read_csv('berkeley_sun_pos.csv',header=0)
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	norm = mpl.colors.Normalize(vmin=0.,vmax=len(csv))
	cmap = mpl.cm.RdYlBu
	m = mpl.cm.ScalarMappable(norm=norm,cmap=cmap)
	for idx,row in csv.iterrows():
		x = numpy.cos(numpy.deg2rad(row['Azimuth']))*numpy.cos(numpy.deg2rad(row['Altitude']))
		y = numpy.sin(numpy.deg2rad(row['Azimuth']))
		z = numpy.sin(numpy.deg2rad(row['Altitude']))
		ax.plot([0,x],[0,y],[0,z],color=m.to_rgba(idx))
	plt.axis('equal')
	plt.show()

if __name__ == '__main__':
	plot_panels()
# fig = plt.figure()
# ax = fig.add_subplot(212, projcetion='3d')
# m = mpl.cm.ScalarMappable(norm=norm,cmap=cmap)
# for idx,row in csv.iterrows():
# 	x = numpy.cos(numpy.deg2rad(row['Azimuth']))*numpy.cos(numpy.deg2rad(row['Altitude']))
# 	y = 0# numpy.sin(numpy.deg2rad(row['Azimuth']))
# 	z = numpy.sin(numpy.deg2rad(row['Altitude']))
# 	ax.plot([0,x],[0,y],[0,z],color='r')
# plt.axis('equal')
# plt.show()