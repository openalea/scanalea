from openalea.plantgl.all import *
from scanalea import segmentation as seg
from scanalea.codecs import read, ply

from time import time

fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented/segmentedMesh.vtk'
fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented/segmentedMesh_manualseg.vtk'
scene = read(fn)
Viewer.display(scene)

stems, leaves, groups, coords = seg.organs(scene)

shapes = leaves.values()
shapes.extend(stems.values())
scene1 = Scene(shapes)
Viewer.display(scene1)

from scanalea.light import caribu, display, turtle

caribu_scene, res = caribu(scene, source=turtle(16))
display(scene, res)

g = seg.create_mtg(stems, leaves,coords)


"""
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

"""

