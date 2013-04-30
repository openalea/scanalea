"""
Inference functions for maize from plantscan measurements

These functions allows to make an automatic assesment of a measured plant by using biological knowledge 
"""
import scanalea
from alinea.adel.AdelR import csvAsDict, dataframe, RdflistAsdicts

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
rcode = resource_string('scanalea', 'maize.R')
r(rcode)
RinferMaize = robj.globalEnv['infer_maize']

def inferMaize(csvfile, nff =16):
"""
Infer a plausible maize plant from scanalea measurments at one time

    Parameters : should be a mtg pre-processed by scanalea
    Returns : should be a "corrected" mtg
"""
    data = csvAsDict(csvfile)
    df=dataframe(data)
    res=RinferMaize(df,nff)
    return RdflistAsdicts(res)
 