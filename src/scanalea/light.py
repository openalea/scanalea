from matplotlib import cm
from alinea.caribu.CaribuScene import CaribuScene
import turtle as _turtle

import openalea.plantgl.all as pgl
def caribu(scene, source = (1,(0,0,-1)), infinity=False):
    c_scene = CaribuScene()
    idmap = c_scene.add_Shapes(scene)
    c_scene.addSources(source)
    output = c_scene.runCaribu(infinity=infinity)
    results = c_scene.output_by_id(output, idmap)['Eabsm2']
    return c_scene, results

def display(scene, results, colormap=cm.hot):
    sd = scene.todict()
    r, g, b = colormap(results.values())[:,:-1].T
    r = r.tolist(); g = g.tolist(); b=b.tolist()
    for i, vid in enumerate(results):
        sd[vid][0].appearance = pgl.Material((int(r[i]*255), int(g[i]*255), int(b[i]*255)))
    
    pgl.Viewer.display(scene)
    return scene
    
def turtle(sectors=16):
    energy, emission, direction, elevation, azimuth = _turtle.turtle(sectors=str(sectors), energy=1) 
    sources = zip(energy, direction)
    return sources
