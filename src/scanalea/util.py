from openalea.plantgl.all import Viewer, Scene
from openalea.mtg import io

def display(g):
    s = "MTG : nb_vertices=%d, nb_scales=%d"%(g.nb_vertices(), g.nb_scales())
    s = '\n'.join([s,io.display(g, max_scale=0, display_id=True,
                         display_scale=True, nb_tab=6)])
    return s

def plot(g):
    return Scene(g.property('geometry').values())

