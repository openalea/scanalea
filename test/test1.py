from openalea.plantgl.all import *
from scanalea import segmentation as seg
from scanalea.codecs import read, ply
import numpy as np

def test_ply():
    fn = '/media/pradal/DONNEES/pradal/data/plantscan/663_4_tp/FourTPsec_20130326_3199_663_res1280_full_vh_smoothed_textured.ply'
    scene = read(fn)

