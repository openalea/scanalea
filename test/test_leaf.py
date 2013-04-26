from openalea.plantgl.all import *
from scanalea import segmentation as seg
from scanalea.codecs import read, ply
import numpy as np


fn = '/media/pradal/DONNEES/pradal/data/plantscan/segmented/segmentedMesh.vtk'
scene = read(fn)
Viewer.display(scene)

leaf = [99,100,101,102]
ds = scene.todict()
new_scene = Scene([ds[l][0] for l in leaf])
Viewer.display(new_scene)


up1, up2 = ds[leaf[0]][0], ds[leaf[1]][0]
down1, down2 = ds[leaf[2]][0], ds[leaf[3]][0]

frontier_up = seg.intersect(up1, up2)
frontier_down = seg.intersect(down1, down2)

points = np.array(up1.geometry.pointList)
curve_up = points[frontier_up]
curve_down = points[frontier_down]

xs, ys, zs = curve_up.T

# finding a plane from a set of points

# center of mass
crv = np.array(curve_up.tolist()+curve_down.tolist())

def median_plane(crv):
    origin = crv.sum(0)/len(crv)
    pts = np.mat(crv)
    u,s,vh = np.linalg.linalg.svd(pts)
    v = vh.conj().transpose()
    normal = np.array(v[:,-1].T)[0]
    return origin, normal





import pylab as pl
import numpy as np
from scipy import stats, linalg
from mpl_toolkits.mplot3d import Axes3D
import math


def plot_figs(fig_num, elev, azim):
    a,b,c = crv.T
    _norm = math.sqrt((a.max()-a.min())**2+(b.max()-b.min())**2+(c.max()-c.min())**2)/2.
    a/=_norm; b/=_norm; c/=_norm

    fig = pl.figure(fig_num, figsize=(4, 3))
    pl.clf()
    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=elev, azim=azim)

    ax.scatter(a[::10], b[::10], c[::10], marker='+', alpha=.4)
    Y = np.c_[a, b, c]
    U, pca_score, V = linalg.svd(Y, full_matrices=False)
    x_pca_axis, y_pca_axis, z_pca_axis = V.T * pca_score / pca_score.min()

    x_pca_axis, y_pca_axis, z_pca_axis = 3 * V.T
    x_pca_plane = np.r_[x_pca_axis[:2], - x_pca_axis[1::-1]]
    y_pca_plane = np.r_[y_pca_axis[:2], - y_pca_axis[1::-1]]
    z_pca_plane = np.r_[z_pca_axis[:2], - z_pca_axis[1::-1]]
    x_pca_plane.shape = (2, 2)
    y_pca_plane.shape = (2, 2)
    z_pca_plane.shape = (2, 2)
    ax.plot_surface(x_pca_plane, y_pca_plane, z_pca_plane)
    ax.w_xaxis.set_ticklabels([])
    ax.w_yaxis.set_ticklabels([])
    ax.w_zaxis.set_ticklabels([])

