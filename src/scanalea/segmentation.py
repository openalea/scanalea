from openalea.plantgl.scenegraph import Material, Shape, FaceSet, Tapered, Cylinder, Translated
import numpy as np
from math import sqrt

def organs(scene, first_leaf_index = 99, split_stem=False):
    """ Extract organs from a segmented mesh. """
    leaves = {}
    stems = {}

    def stem_shape(geom, color=(20,130,20)):
        return Shape(geom,Material(color))

    def leaf_shape(geom, color=None):
        if not color:
            color = np.random.randint(0,255,3).tolist()
        return Shape(geom,Material(color))

    for shape in scene:
        geom = shape.geometry
        shape_id = shape.id
        if shape_id < first_leaf_index:
            stems[shape_id] = stem_shape(geom)
            stems[shape_id].id = shape_id
        else:
            leaves[shape_id] = leaf_shape(geom)
            leaves[shape_id].id = shape_id

    # Group leaves
    # Idea: If two shapes share the same points, they belong to the same leaf

    group = {}
    queue = sorted(leaves)
    parents = {}
    while queue:
        leaf = queue.pop(0)
        if leaf not in group:
            group[leaf] = []

        for lid in queue:
            if lid in group[leaf]:
                continue
            if closed(leaves[leaf], leaves[lid]):
                group[leaf].append(lid)
                group.setdefault(lid,[]).append(leaf)

    connected_components = {}
    visited = {}
    for leaf in group:
        if leaf in visited:
            continue
        neigh = [leaf]
        connected_components[leaf]= []
        while neigh:
            x = neigh.pop()
            if x in visited:
                continue
            connected_components[leaf].append(x)
            neigh.extend(group[x])
            visited[x] = True

    for leaf in connected_components:
        mat = leaves[leaf].appearance
        for lid in connected_components[leaf]:
            leaves[lid].appearance = mat

    # Group leaves
    bigstem = group_shapes(stems)
    
    group_leaves = {}
    for lid in connected_components:
        _leaves = dict((leaf_id, leaves[leaf_id]) for leaf_id in connected_components[lid])
        group_leaves[lid] = group_shapes(_leaves)
        group_leaves[lid].id = lid

    #leaves = group_leaves(connected_components, leaves)
    # Order leaves
    points = np.array(bigstem.geometry.pointList)
    coords = []
    for lid in group_leaves:
        sh = group_leaves[lid]
        frontier = points[intersect(sh,bigstem)]
        if len(frontier)==0:
            print 'no frontier between leaf %d and stem'
            continue
        x,y,z  = frontier.T
        coords.append((lid, z.min(), z.mean(), z.max()))

    sorted_coords = sorted(coords, key= lambda coord: coord[1])

    if not split_stem:
        k0 = min(list(stems))
        group_stems = {k0: bigstem}
        return group_stems, group_leaves, connected_components, sorted_coords

    # Group Stems
    # compute the z_min of each stem
    # then associate the stem id with the leaf
    stem_bbox = []
    for sid in stems:
        faces = np.array(stems[sid].geometry.indexList)
        pts = points[faces]
        x, y, z = pts.T
        stem_bbox.append((sid, z.min(), z.max()))

    stem_bbox = sorted(stem_bbox, key= lambda coord: coord[2])

    print "stem_box : ",stem_bbox
    print "sorted_coords : ",sorted_coords
    index = 0
    _stems = {}
    lid, lmin, lmean, lmax = sorted_coords.pop(0)
    for i in range(len(stem_bbox)):
        stem_id, smin, smax = stem_bbox[i]
        if smax <= lmin:
            _stems.setdefault(lid,[]).append(stem_id)
            continue
        else:
            while sorted_coords and smax > lmin:
                lid, lmin, lmean, lmax = sorted_coords.pop(0)
            else:
                if not sorted_coords:
                    index = i
                    break
                else:
                    _stems.setdefault(lid,[]).append(stem_id)
    if index != 0:
        # last stems are a leaf
        last_stems = dict((s[0],stems[s[0]]) for s in stem_bbox[index:])
        new_leaf_id = max(group_leaves.keys())+1
        sid = last_stems.keys()[0]
        last_stems[new_leaf_id] = last_stems[sid]
        del last_stems[sid]
        sh = group_shapes(last_stems,new_leaf_id)
        sh.id = new_leaf_id
        group_leaves[new_leaf_id] = sh
        print last_stems
        
    print _stems

    group_stems = {}
    for lid in _stems:
        stem_shapes = dict((sid,stems[sid]) for sid in _stems[lid])
        group_stems[lid] = group_shapes(stem_shapes)
        group_stems[lid].id = lid


    return group_stems, group_leaves, connected_components, sorted_coords


def intersect(shape1, shape2):
    mesh1, mesh2 = shape1.geometry, shape2.geometry
    x = np.unique(np.array(mesh1.indexList))
    y = np.unique(np.array(mesh2.indexList))

    commons = np.intersect1d(x,y)
    if len(commons):
        return commons
    return []

def closed(shape1, shape2):
    frontier = intersect(shape1, shape2)
    return len(frontier) != 0

def group_shapes(shapes, shape_id=None):
    
    if shape_id is None:
        keys = list(shapes)
        shape_id = keys[0]
    sh0 = shapes[shape_id] 
    points = sh0.geometry.pointList
    color = sh0.appearance

    faces = []
    for shape in shapes:
        mesh = shapes[shape].geometry
        faces.extend(list(mesh.indexList))

    return Shape(FaceSet(points, faces),color)


def group_leaves(components, shapes):
    pass

def big_stem(stems):
    keys = list(stems)
    points = stems[keys[0]].geometry.pointList

    faces = []
    for stem in stems:
        mesh = stems[stem].geometry
        faces.extend(list(mesh.indexList))

    return Shape(FaceSet(points, faces),stems[keys[0]].appearance)

def bbox(shape):
    mesh = shape.geometry
    points = np.array(mesh.pointList)
    faces = np.array(mesh.indexList)
    pts = points[np.unique(faces)]
    x, y, z = pts.T
    return ((x.min(), x.mean(), x.max()),
            (y.min(), y.mean(), y.max()),
            (z.min(), z.mean(), z.max()))


    
def create_mtg(stems, leaves, ordered_leaves):
    from openalea.mtg import mtg
    mesh = None
    if len(stems) > 1:
        mesh = big_stem(stems)
    else:
        mesh = stems[stems.keys()[0]]
    mesh = mesh.geometry
    points = np.array(mesh.pointList)
    faces = np.array(mesh.indexList)

    pts = points[np.unique(faces)]
    x, y, z = points.T #coordinates of the pts in the mesh
    xf, yf, zf = pts.T
    zmin = z[faces].min()
    zmax = z[faces].max()    

    g = mtg.MTG()
    vid = g.add_component(g.root, label='plant1')
    mid = g.add_component(vid, label='mainstem')


    stem_elt = []
    previous_metamer = 0
    vid_metamer = None
    vid_stem = None

    last_leaf = ordered_leaves[-1][0]
    for lid, _min, _mean, _max in ordered_leaves:
        height = _min-zmin
        dz = height/10.
        mask = (zf>=zmin) & (zf <=zmin+dz)
        xlayer, ylayer = xf[mask], yf[mask]
        diameter_base = sqrt((xlayer.max()-xlayer.min())*(ylayer.max()-ylayer.min()))

        if lid == last_leaf:
            mask = (zf>=_min-dz)
        else:
            mask = (zf>=_min-dz) & (zf <=_min)
            
        xlayer, ylayer = xf[mask], yf[mask]
        diameter_top = sqrt((xlayer.max()-xlayer.min())*(ylayer.max()-ylayer.min()))


        if lid == last_leaf:
            face_mask = (z>=zmin)[faces].any(axis=1)
        else:
            face_mask = ((z>=zmin) & (z <=_min))[faces].any(axis=1)
        my_faces = (faces[face_mask]).tolist()
        stem_mesh = Shape(FaceSet(pointList=mesh.pointList,indexList=my_faces),
                          leaves[lid].appearance)

        new_metamer = g.add_component(mid, label='metamer%d'%(previous_metamer+1))
        if previous_metamer == 0:
            vid_metamer = new_metamer
        else:
            vid_metamer =  g.add_child(vid_metamer, child=new_metamer, edge_type='<')

        #stem_mesh = Shape(Translated((0,0,zmin),Tapered(diameter_base/2., diameter_top/2., Cylinder(1,height))),  leaves[lid].appearance)
        new_stem = g.add_component(vid_metamer, label='StemElement', 
                                   length=height, geometry=stem_mesh,
                                   diameter_base=diameter_base,
                                   diameter_top=diameter_top)
        if previous_metamer == 0:
            vid_stem = new_stem
        else:
            vid_stem =  g.add_child(vid_stem, child=new_stem, edge_type='<')

        # Add leaf
        g.add_child(vid_stem, edge_type='+', label='LeafElement', geometry=leaves[lid])
        zmin = _min
        previous_metamer+=1
        

    return mtg.fat_mtg(g)
        
    
def add_leaves_data(g, fn):
    data= np.genfromtxt(fn,delimiter=',' ,names=True)
    key='Leaf_Number'
    data.sort(order='height')
    
    leaves = sorted(vid for vid in g.vertices() if g.label(vid) == 'LeafElement')
    for i, lid in enumerate(leaves):
        n = g.node(lid)
        for k in data.dtype.names:
            if k==key: continue
            n.__setattr__(k.lower(),data[k][i])
    return g

    
