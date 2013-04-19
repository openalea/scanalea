from openalea.plantgl.all import *
from scanalea.segmentation import *
from scanalea.codecs import read, ply

from time import time

fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented/segmentedMesh.vtk'
scene = read(fn)
Viewer.display(scene)

stems, leaves, groups = organs(scene)

print len(groups)
scene = Scene(leaves.values())
scene.add(big_stem(stems))

Viewer.display(scene)


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

