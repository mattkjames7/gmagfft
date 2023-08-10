import PyFileIO as pf
from .. import profile
import os
from .saveSpec import saveSpec

def readSpec(date,stn,autoSave=True):

    cfg = profile.get()
    specPath = cfg['specPath'] + '/{:s}'.format(stn)
    fname = specPath + '/{:08d}.bin'.format(date)

    if os.path.isfile(fname):
        if os.stat(fname).st_size == 0:
            return None
        return pf.LoadObject(fname)
    else:
        print('Spec {:s} on {:d} does not yet exist, attempting to recreate...'.format(stn,date))
        saveSpec(date,stn)
        return readSpec(date,stn)