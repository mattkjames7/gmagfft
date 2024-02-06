import numpy as np
from .. import profile
from .calculate import calculateStation
import PyFileIO as pf
import os

def save(stn):

    data = calculateStation(stn)
    if data is None:
        print('No spectra found for {:s}'.format(stn))
        return

    cfg = profile.get()
    bgPath = cfg['path'] + '/background'

    if not os.path.isdir(bgPath):
        os.makedirs(bgPath)

    fname = bgPath + '/{:s}.bin'.format(stn)
    pf.SaveObject(data,fname)
    print('Saved: {:s}'.format(fname))

def saveAll():

    cfg = profile.get()
    specPath = cfg['specPath']

    stations = os.listdir(specPath)
    stations = [s for s in stations if os.path.isdir(specPath + '/' + s)]

    print('Found {:d} stations'.format(len(stations)))

    for i,s in enumerate(stations):
        print('Station: {:s} ({:d} of {:d})'.format(s,i+1,len(stations)))
        save(s)

