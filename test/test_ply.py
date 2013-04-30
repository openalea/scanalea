from openalea.plantgl.all import *
from scanalea import segmentation as seg
from scanalea.codecs import read, ply
import numpy as np

from time import time

fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented/segmentedMesh_manualseg.vtk'
fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented2/segmentedMesh.vtk'
scene = read(fn)
Viewer.display(scene)

scene1, stems, leaves, coords = seg.organs(scene)


"""
from scanalea.light import caribu, display, turtle

caribu_scene, res = caribu(scene, source=turtle(16))
display(scene, res)
"""

leaves_data = '/media/pradal/DONNEES/pradal/data/plantscan/segmented2/leaves_data.csv'
g = seg.create_mtg(stems, leaves,coords, leaves_data=leaves_data)
Viewer.display(Scene(g.property('geometry').values()))

from scanalea.maize import inferMaize
parameters=inferMaize(leaves_data)

rank = parameters['ranks']['rank'] # starting from 1
first_leaf_index = rank[0]
if first_leaf_index > 1:
    s = '%d '%(first_leaf_index-1) + (' leaves ' if first_leaf_index>2 else 'leaf ') + 'missing at the base'
    print s

stage = parameters['stage']
ligulated_leaves = int(np.round(stage['col'])[0]-first_leaf_index)+1
total_leaves = int(np.round(stage['tip'])[0]-first_leaf_index)+1

nb_leaves = g.nb_vertices(scale=3)
print 'Segmented leaves: %d but Predicted leaves: %d'%(nb_leaves, total_leaves)

metamer_ids = sorted(g.vertices(scale=3))
whorled_metamers = metamer_ids[-(nb_leaves- ligulated_leaves):]

for mid in metamer_ids[:ligulated_leaves]:
    stem_id = g.components(mid)[0]
    assert g.label(stem_id).startswith('Stem')
    m = g.node(stem_id).geometry.appearance
    g.node(stem_id).geometry.appearance = m.DEFAULT_MATERIAL
    

Viewer.display(Scene(g.property('geometry').values()))

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

