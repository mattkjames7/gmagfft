import numpy as np
from .readSpec import readSpec
import DateTimeTools as TT


def _combineData(dataList):

    out = {}

    n = 0
    for d in dataList:
        if d is not None:
            dtype = d['data'].dtype
            n += d['data'].size
    
    if n == 0:
        return None

    out['data'] = np.recarray(n,dtype=dtype)

    p = 0
    for d in dataList:
        if d is not None:
            l = d['data'].size
            out['data'][p:p+l] = d['data']
            p += l
    
    for d in dataList:
        if d is not None:
            skeys = list(d['spec'].keys())
            break

    if len(skeys) > 0:
    
        spec = {}
        for key in skeys:
            tmp = [d['spec'][key] for d in dataList if d is not None]
            if isinstance(tmp[0],int):
                spec[key] = sum(tmp)
            elif len(tmp) > 0:
                sh = tmp[0].shape

                if key in ['freq','freqax']:
                    spec[key] = tmp[0]
                elif key in ['nf']:
                    spec[key] = tmp[0]
                elif key in ['nw']:
                    spec[key] = np.sum(tmp)
                elif key == 'utcax':
                    spec[key] = np.concatenate([t[:-1] for t in tmp]+[[tmp[-1][-1]]])
                elif len(sh) == 1:
                    spec[key] = np.concatenate(tmp)
                else:
                    spec[key] = np.concatenate(tmp,axis=0)
        out['spec'] = spec

        for d in dataList:
            if d is not None:
                out['pos'] = {
                    'mlon' : d['pos']['mlon'],
                    'mlat' : d['pos']['mlat'],
                    'glon' : d['pos']['glon'],
                    'glat' : d['pos']['glat'],
                }
                break

    pos = ['px','py','pz']
    for p in pos:
        out['pos'][p] = np.concatenate([d['pos'][p] for d in dataList])

    return out

def getSpecs(date,stn):

    ndate = np.size(date)
    if np.size(date) != 2:
        dates = np.zeros(ndate,dtype='int32') + date
    else:
        dates = TT.ListDates(date[0],date[1])

    data = [readSpec(d,stn) for d in dates if d is not None]
    if len(data) == 0:
        return None

    return _combineData(data)