"""
Provides a parametrisation of maize plants compatible with PlantScan data
"""
import scanalea
import numpy as np
from alinea.adel.fitting import fit2
from alinea.adel.AdelR import *

import rpy2.robjects as robj
r = robj.r

from rpy2.robjects.numpy2ri import numpy2ri
try:
    numpy2ri.activate()#force auto-conversion mode of Robject to array
except:
    pass

try: 
    robj.globalEnv = robj.globalenv
except:
    pass

#content of rfiles using setuptools pkg_resources utility
from pkg_resources import resource_string

# Set Numeric Locale value 
r('Sys.setlocale(category="LC_NUMERIC",locale="C")')

#r.source(os.path.join(path,'Adel.R')) : code qui suit plutot a laisser au niveau des fonctions
rcode = resource_string('scanalea', 'Profil.R')
r(rcode)
rcode = resource_string('scanalea', 'inferPlant.R')
r(rcode)
RinferPlant = robj.globalEnv['infer_Plant']

def inferPlant(csvfile, nff=16):
    data = csvAsDict(csvfile)
    data['pos']=[2,4,5,3,1]
    df=dataframe(data)
    res=RinferPlant(df,nff)
    return RdflistAsdicts(res)
    

def adel_tables(nb_phy,leaf_database, 
                    height,
                    pseudostem_height,
                    nb_young_phy,
                    
                    
                    # internode length distribution
                    internode_dist, # raison geometrique
                    sheath_dist,

                    # Phyllotaxy for young and mature phytomer
                    phyllotactic_angle,
                    phyllotactic_young,
                    phyllotactic_mature,

                    # insertion angle
                    basal_insertion,
                    deviation_insertion,
                    diam_base,
                    diam_top, 
                    # leaf area dist function
                    Smax = 1000,
                    leaf_width_ratio = 0.1,
                    A1 = -4.9,
                    A2  = 0.16,
                    pos_max = 0.66,
                    phyl = 33
                    ):
    """
    """
    nb_phy = int(nb_phy)
    nb_young_phy = int(nb_young_phy)
    

    # compute the leaf surface
    nmax = pos_max * nb_phy
    xn = (np.array(range(1,nb_phy + 1)) - nmax) / (nmax - 1)
    leaf_area = Smax * np.exp(A1 * xn**2 + A2 * xn**3)
    
    # compute normalised surface from database
    relative_phytomer_num = np.linspace(1./nb_phy, 1, nb_phy)
    db = leaf_database
    rank_max = max(int(x) for x in db)
    def choose_rank(rank):
        if str(rank) not in db:
            rank = rank+1 if str(rank+1) in db else rank-1
        if str(rank) in db:
            return rank
        
        while str(rank) not in db and rank<rank_max :
            rank+=1
        if str(rank) not in db: 
            rank = rank_max
        return rank

    lindex = ranks = [choose_rank(round(x) * rank_max) for x in relative_phytomer_num]
    norm_surface= np.array([fit2(*db[str(rank)][0])[1] for rank in ranks])

    lengths = np.sqrt(leaf_area/norm_surface/leaf_width_ratio)
    widths = lengths * leaf_width_ratio

    # internode length
    q = internode_dist
    offset = pseudostem_height
    n = nb_phy - nb_young_phy
    if q == 1:
        u0 = (height - offset) / n
    else:
        u0 = (height-offset) * (1-q) / (1-q**(n+1))

    internode_length = [0]*nb_young_phy + [ u0 * q**i for i in range(n)]

    #sheath length
    q = sheath_dist
    ny = nb_young_phy
    if q == 1:
        u0 = pseudostem_height / ny
    else:
        u0 = pseudostem_height * (1-q) / (1-q**(ny+1))

    sheath_length = np.concatenate((np.array([ u0 * q**i for i in range(ny)]).cumsum(), [pseudostem_height] * (nb_phy - ny)))

    # internode and sheath diameters
    diameters = [diam_base] * nb_young_phy + np.linspace(diam_base, diam_top, n).tolist()

    
    #setup of dictionaries to build  setAdel's dataframes
    NaN = float('nan')

    #axe table
    startdate = 0
    tip_lig_delay = 0.8 * phyl
    lig_senescence_delay = 10000 #3.6*phyl for a simulation with realistic senescence
    senescence_disparition_delay = 200

    axeTags='plant,axe,nf,end,disp,dimIndex,phenIndex,earIndex,emf1,ligf1,senf1,dispf1'.split(',')
    axeVals = [1,'MS',nb_phy,'NA','NA',1,1,1,
                startdate,
                startdate + tip_lig_delay,
                startdate + tip_lig_delay + lig_senescence_delay,
                startdate + tip_lig_delay + lig_senescence_delay + senescence_disparition_delay]
    axeT = dict(zip(axeTags,axeVals))

    #phen table
    nrel = [0, 0.5, 1]
    tip = np.array([-phyl, phyl * nb_phy *.5, phyl * nb_phy])
    col = np.array([-phyl*1.8, phyl * 1.8 * nb_phy *.5, phyl * 1.8 * nb_phy *.5 + phyl * 0.5 * nb_phy * 0.5])
    phenTags = ["index","nrel","tip","col","ssi","disp"]
    phenVals = [[1] * len(nrel),
                nrel,
                tip,
                col,
                col + lig_senescence_delay,
                col + lig_senescence_delay + senescence_disparition_delay
                ]
    phenT = dict(zip(phenTags,phenVals))
    
    # debFeu (a corriger de 5 cm deja allonge)
    n = np.array(range(1,nb_phy + 1))
    debFeu = (0.85 - 1) * n
    endFeu = (1.8 - 1) * n
    endFeuTop = (1.8 * nb_phy * 0.5 +  0.5 * (n - 0.5 * nb_phy)) - n
    endFeu[n > 0.5 * nb_phy] = endFeuTop[n > 0.5 * nb_phy]
    
    #dim Table
    dimTags = ["index","nrel","Ll","Lw","Gl","Gd","El","Ed","incB","dincB","pAngle","dpAngle"] #last two columns to be tested for existence in setAdel for freeing of geoLeaf function inputs
    dimVals = [[1] * nb_phy,
                relative_phytomer_num,
                lengths,
                widths,
                sheath_length,
                diameters,
                internode_length,
                diameters,
                [basal_insertion] * nb_phy,
                [deviation_insertion] * nb_phy,
                [phyllotactic_angle] * nb_phy,
                [phyllotactic_young] * nb_young_phy + [phyllotactic_mature] * (nb_phy - nb_young_phy)
                ]
    
    dimT = dict(zip(dimTags,dimVals))

    devT = dict(dimT = dimT, phenT = phenT, axeT = axeT, earT = None, ssisenT = None)

    return devT, debFeu, endFeu
    
def fit_adel(csv,db,nff=16,phyl=33):
    fit = inferPlant(csv,nff=nff)
    devT, debFeu,endFeu =  adel_tables(nff,db,200,20,6,1,1.4,180,20,60,40,40,2,1, Smax = fit['fitS']['Smax'], A1 = fit['fitS']['A1'], A2 = fit['fitS']['A2'],phyl=phyl)
    geoLeaf = genGeoLeaf()
    geoAxe = genGeoAxe()
    plant_pars = setAdel(devT,geoLeaf,geoAxe,1,seed = 1)
    return plant_pars

def getString(d):
    from alinea.adel.AdelR import dataframe, genString
    return genString(dataframe(d))
    
def generate_scene(string, symbols):
    from alinea.adel.mtg import CanMTG
    g = CanMTG(symbols, string)
    s = g.to_plantgl()
    return s[0]

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

#ACHTUNG / ADD STEM TO NON LIGULATED LEAVES
db,symbols = load_leaves_db()

def run_adel(fit,stage=6.66*33):
    from openalea.plantgl.all import Viewer
    adel_pars ={'senescence_leaf_shrink' : 0.5,'startLeaf' : -1.2, 'endLeaf' : 3.6, 'stemLeaf' : 1.2,'epsillon' : 1e-6}
    cantable = RunAdel(stage,fit, adel_pars)
    string = getString(cantable)
    scene = generate_scene(string,symbols)
    Viewer.display(scene)