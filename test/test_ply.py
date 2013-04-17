from openalea.plantgl.all import *
from scanalea.codecs import read, ply

from time import time

fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented/segmentedMesh.vtk'
scene = read(fn)
Viewer.display(scene)

fn = '/media/pradal/DONNEES/pradal/data/plantscan/663_4_tp/FourTPsec_20130326_3199_663_res1280_full_vh_smoothed_textured.ply'
t1 = time()
scene = read(fn)
t2 = time()
print 'Case1 ', t2-t1
Viewer.display(scene)


fn = '/media/pradal/DONNEES/pradal/data/plantscan/663_4_tp/FourTPsec_20130326_3199_663_res1280_full_vh_smoothed_textured.ply'
c=ply.PlyCodecVTK()
t1 = time()
scene=c.read(fn)
t2 = time()
Viewer.display(scene)
print 'Case VTK ', t2-t1
t1=t2


fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented/segmentedMesh.vtk'
import numpy as np
from mayavi.sources.vtk_file_reader import VTKFileReader

"""
r = VTKFileReader()
r.initialize(fn)
mesh = r.outputs[0] 
points = mesh.points.to_array()
x, y, z = points.T
points = np.array((x,y,z)).T
polys = mesh.polys
faces = polys.to_array()

faces = faces.reshape((polys.number_of_cells,polys.max_cell_size+1))
ids, index_1, index_2, index_3 = faces.T

scalars = mesh.point_data.scalars.to_array()
set_scalars = set(scalars)

idxs = np.indices((len(points),))[0]
s = 0
mask = idxs[scalars==s]

for s in set_scalars:
    mask = idxs[scalars==s]
    
"""
