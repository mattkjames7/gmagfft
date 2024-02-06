import numpy as np
from .. import profile
import os
from ..data.readSpec import readSpec
from tqdm import tqdm

def calculateStation(stn):

    cfg = profile.get()
    specPath = cfg['specPath'] + '/{:s}'.format(stn)

    files = os.listdir(specPath)
    files = np.array([f for f in files if f.endswith('.bin')])
    if files.size == 0:
        return None
    dates = []
    for f in files:
        try:
            d = int(f[:8])
            dates.append(d)
        except:
            pass
    dates = np.array(dates)
    print('Found {:d} dates'.format(dates.size))

    fields = ['xPow','yPow','zPow','xAmp','yAmp','zAmp']
    tmpdata = {}
    for f in fields:
        tmpdata[f] = []

    for d in tqdm(dates,desc='Reading spectra:         '):
        data = readSpec(d,stn)
        for f in fields:
            try:
                tmpdata[f].append(data['spec'][f])
            except:
                pass
    combdata = {}
    for f in tqdm(fields,desc='Combining spectra:       '):
        if len(tmpdata[f]) == 0:
            combdata[f] = None
        else:
            combdata[f] = np.concatenate(tmpdata[f],axis=0)

    out = {}
    for f in tqdm(fields,desc='Calculating percentiles: '):
        if combdata[f] is not None:
            out[f] = getSpecBackground(combdata[f])
    
    if len(out) == 0:
        return None    

    return out

def getSpecBackground(x):

    percentiles = np.linspace(5.0,95.0,19)

    out = {p:np.nanpercentile(x,p,axis=0) for p in percentiles}

    return out

