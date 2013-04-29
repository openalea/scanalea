from openalea.core.path import path

class CodecError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class FileNameError(CodecError):
    def __init__(self, fn):
        msg = "The file %s does not exists"%fn
        CodecError.__init__(self,msg)

class UnknownCodecError(CodecError):
    def __init__(self, ext):
        msg = "Unable to read %s file format"%ext
        CodecError.__init__(self,msg)

codec_registery= {}

def register(ext, klass):
    """ Register a codec. """
    global codec_registery
    codec_registery[ext] = klass

def read(fname, split=True):
    """ Read 3D meshes based on the file extension.

    :Parameters:
        - fname : 3D mesh file (ply or vtk)

    :Returns:
        - PlantGL Scene
    """
    fn = path(fname).abspath()
    if not fn.isfile():
        raise FileNameError(fname)

    file_ext = fn.ext[1:]
    if file_ext not in codec_registery:
        raise UnknownCodecError(file_ext)

    return codec_registery[file_ext]().read(fn,split=split)

from scanalea import ply, vtk
register('vtk', vtk.VtkCodec)
register('ply', ply.PlyCodec)

