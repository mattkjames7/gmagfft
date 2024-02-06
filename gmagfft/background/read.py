import numpy as np
from .. import profile
import PyFileIO as pf
import os


def read(stn):

    cfg = profile.get()
    bgPath = cfg['path'] + '/background'
    fname = bgPath + '/{:s}.bin'.format(stn)

    if not os.path.isfile(fname):
        return None
    
    return pf.LoadObject(fname)