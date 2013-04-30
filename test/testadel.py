import numpy as np
from openalea.plantgl.all import Viewer
from alinea.adel.AdelR import setAdel,RunAdel,genGeoLeaf,genGeoAxe
import scanalea.PlantScanAdelMaize as ps


def load_leaves_db():
    import cPickle as Pickle
    import alinea.adel.fitting as fitting
    from alinea.adel.symbol import build_symbols
    
    fn = r'leaves_simple.db'
    f = open(fn)
    leaves = Pickle.load(f)
    f.close()
    leaves = fitting.fit_leaves(leaves, 9)
    symbols = build_symbols(leaves[0])
    db = leaves[0]
    return db, symbols


db,symbols = load_leaves_db()
devT, debFeu,endFeu = ps.adel_tables(15,db,200,20,6,1,1.4,180,20,60,40,40,2,1)
geoLeaf = genGeoLeaf()
geoAxe = genGeoAxe()
plant_pars = setAdel(devT,geoLeaf,geoAxe,1,seed = 1)
adel_pars ={'senescence_leaf_shrink' : 0.5,'startLeaf' : debFeu.mean(), 'endLeaf' : endFeu.mean(), 'stemLeaf' : 1.2,'epsillon' : 1e-6}
cantables = map(lambda(x): RunAdel(x,plant_pars, adel_pars), range(0,900,60))
strings = map(ps.getString,cantables)
scenes = map(lambda(x): ps.generate_scene(x,symbols), strings)

def animate(scenes,delay=0.2):
    from time import sleep
    for s in scenes:
        Viewer.display(s)
        sleep(delay)