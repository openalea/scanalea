# -*- utf-8 -*-
#
#       VPlants.PlantGL
#
#       Copyright 2013-2013 INRIA - CIRAD - INRA
#
#       File author(s): Christophe Pradal <christophe.pradal@cirad.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite: http://openalea.gforge.inria.fr
#
###############################################################################
""" `PLY`_ codec for PlantGL

This module provide a codec for PLY file format.
`PLY`_ is a file format for 3D meshes known as the Standford Triangle format.

This codec allow to read and write `PLY`_ file format. 

.. _PLY: http://en.wikipedia.org/wiki/Wavefront_.obj_file
"""

__license__ = "Cecill-C"
__revision__ = " $Id: actor.py 2242 2010-02-08 17:03:26Z cokelaer $ "

import os
import warnings
from random import randint
from itertools import izip_longest

import openalea.plantgl.math as mt
import openalea.plantgl.scenegraph as sg
import openalea.plantgl.algo as alg
#from openalea.plantgl.ext import color


class PlyCodec (sg.SceneCodec):
    """ PLY File Format 

    The PLY file format is a simple data-format that represents 3D geometry alone: 
        - the position of each vertex, 
        - the UV position of each texture coordinate vertex, 
        - normals, 
        - the faces that make each polygon defined as a list of vertices, 
        - and texture vertices. 

    File example::

        # List of Vertices, with (x,y,z[,w]) coordinates, w is optional.
        v 0.123 0.234 0.345 1.0
        ...
        
        # Texture coordinates, in (u,v[,w]) coordinates, w is optional.
        vt 0.500 -1.352 [0.234]
        ...
        
        # Normals in (x,y,z) form; normals might not be unit.
        vn 0.707 0.000 0.707
        vn ...
        
        # Face Definitions (see below)
        f 1 2 3
        f 3/1 4/2 5/3
        f 6/4/1 3/5/3 7/6/5
        f ...
    """
    
    def __init__(self):
        """
        Initialisation of the codec info
        """
        sg.SceneCodec.__init__(self,"PLY",sg.SceneCodec.Mode.ReadWrite)

    def formats(self):
        """ return formats """
        return [ sg.SceneFormat("PLY Codec",["ply"],"The ply file format") ]


    def read(self,fname):
        """ read a ply file """

        tag = 'header' # element

        types = {}
        types['char'] = types['uchar'] = int
        types['short'] = types['ushort'] = types['int'] = types['uint'] = int
        types['float'] = types['double'] = float

        # define data
        vertices = []
        faces= []
        textures= []
        texture_files = []
        line = 0
        nb_vertices = 0
        nb_faces = 0
        elements = []
        properties = {}
        format = 'ascii'

        counter = 0
        # read the obj file
        with open(fname,"r") as f:
            l = f.readline().strip()
            if l != 'ply':
                return sg.Scene()
            for l in f:
                l = l.strip()
                fields = l.split()
                if not fields:
                    continue

                if tag == 'header':
                    key = fields[0]
                    if key == 'end_header':
                        tag_index = 0
                        tag = elements[tag_index]
                        continue
                    # format
                    elif key == 'format':
                        format = fields[1]
                    # comment
                    elif key == 'comment':
                        if fields[1] != 'TextureFile':
                            continue
                        else:
                            texture_files.append(fields[2])
                    elif key == 'element':
                        if fields[1] == 'vertex':
                            nb_vertices = int(fields[2])
                            elements.append('vertex')
                        elif fields[1] == 'face':
                            nb_faces = int(fields[2])
                            elements.append('face')
                    elif key == 'property':
                        name = elements[-1]
                        key = fields[-1]
                        _types = [fields[1]]
                        if fields[1] == 'list':
                            _types = fields[2:-1]
                        _types = [types[t] for t in _types]
                        properties.setdefault(name,[]).append((key,_types))

                else:
                    counter += 1
                    p = properties[tag]

                    if tag == 'vertex':
                        v = []
                        i = 0
                        for t in p:
                            assert len(t[1]) <= 1
                            v.append(t[1][0](fields[i]))
                            i+=1
                        vertices.append(v)
                        if counter == nb_vertices:
                            tag_index +=1 
                            tag = elements[tag_index]
                            counter = 0

                    elif tag == 'face':
                        f = []
                        tex = []
                        vv = f
                        i = 0
                        for t in p:
                            if len(t[1]) == 1:
                                pass #TODO
                            else:
                                # list
                                assert len(t[1]) == 2
                                name = t[0]
                                if name.startswith('vertex'):
                                    vv = f
                                elif name.startswith('tex'):
                                    vv = tex
                                else:
                                    print 'UNKNOWN property: ', name

                                n = t[1][0](fields[i])
                                i+=1
                                for j in range(n):
                                    vv.append(t[1][1](fields[i]))
                                    i+=1

                        if f:
                            faces.append(f)
                        if tex:
                            textures.append(tex)
                                
                        if counter == nb_faces:
                            tag_index +=1 
                            counter = 0
                    


       # Build the scene
        scene = sg.Scene()
        tset = sg.FaceSet(pointList=vertices, indexList=faces)
        scene+= tset


        return scene



    #############################################################################
    #############################################################################
    # PlantGL -> PLY codec
    def write(self,fname,scene):
        """ Write an OBJ file from a plantGL scene graph.

        This method will convert a PlantGL scene graph into an OBJ file.
        It does not manage  materials correctly yet.

        :Examples:
            import openalea.plantgl.scenegraph as sg
            scene = sg.Scene()"""
        print("Write "+fname)
        d = alg.Discretizer()
        f = file(fname,'w')

        

        line = '# File generated by PlantGL'
        f.write(line+'\n')

        vertices = [] # List of point List
        normals= [] # List of normal List
        texcoords= [] # List of texture List
        faces = [] # list  of tuple (offset,index List)

        counter = 0
        for i in scene:
            if i.apply(d):
                p = d.discretization
                pts = p.pointList
                ns = p.normalList
                ts = p.texCoordList
                indices = p.indexList
                n = len(p.pointList)
                if n > 0:
                    vertices.append(pts)
                    if ns:
                        normals.append(ns)
                    if ts:
                        texcoords.append(ts)
                    faces.append(Faces(i.name, counter+1, p))
                counter += n

        for pts in vertices:
            for x, y, z in pts:
                f.write('v    %f %f %f\n'%(x, y, z))
            f.write('\n')
        for pts in normals:
            for x, y, z in pts:
                f.write('vn    %f %f %f\n'%(x, y, z))
            f.write('\n')

        for pts in texcoords:
            for x, y in pts:
                f.write('vt    %f %f \n'%(x, y))
            f.write('\n')

        mtl_file = os.path.basename(fname)
        mtl_file = os.path.splitext(mtl_file)[0]+'.mtl'
        f.write('mtllib %s'%(mtl_file))
        for face in faces:
            face.obj(f)

        f.close()
    

codec = PlyCodec()
sg.SceneFactory.get().registerCodec(codec)
