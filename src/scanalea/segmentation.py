from openalea.plantgl.scenegraph import Material, Shape, FaceSet
import numpy as np

def organs(scene, first_leaf_index = 99):
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
    

    # Group Stems

    return stems, group_leaves, connected_components


def closed(shape1, shape2):
    mesh1, mesh2 = shape1.geometry, shape2.geometry
    x = np.unique(np.array(mesh1.indexList))
    y = np.unique(np.array(mesh2.indexList))

    commons = np.intersect1d(x,y)
    if len(commons):
        return True
    return False

def group_shapes(shapes):
    keys = list(shapes)
    sh0 = shapes[keys[0]]
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


