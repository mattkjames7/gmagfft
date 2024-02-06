import numpy as np
from .getMagData import getMagData
from .processMagData import processMagData
from .getSpectrogram import getSpectrogram
from .. import profile
from ..tools.checkPath import checkPath
import PyFileIO as pf
import wavespec as ws
import groundmag as gm
import DateTimeTools as TT
import os
import traceback

def _processData(date,stn):

    cfg = profile.get()
    window = cfg['window']

    print('Reading {:s} Data'.format(stn))
    data0 = getMagData(stn,date)
    print('Processing {:s} Data'.format(stn))
    data = processMagData(data0,date)


    return data

def _fftData(date,data):

    cfg = profile.get()

    print('Spectrogram')
    spec = getSpectrogram(data,date)

    return spec


def _magPos(date,stn,tspec):

    Date,ut = TT.ContUTtoDate(tspec)
    print('Mag Pos')
    px,py,pz = gm.Trace.MagTracePos(stn,Date,ut)
    st = gm.GetStationInfo(stn,date)

    mlat = st.mlat[0]
    mlon = st.mlon[0]
    glat = st.glat[0]
    glon = st.glon[0]

    out = {
        'px' : px,
        'py' : py,
        'pz' : pz,
        'mlat' : mlat,
        'mlon' : mlon,
        'glat' : glat,
        'glon' : glon,
    }
    return out


def saveSpec(date,stn,debug=False):
    
    cfg = profile.get()
    checkPath(cfg['specPath'])

    pairPath = cfg['specPath'] + '/{:s}'.format(stn)
    if not os.path.isdir(pairPath):
        os.makedirs(pairPath)

    fname = pairPath + '/{:08d}.bin'.format(date)

    try:
        #process the data
        data = _processData(date,stn)

        #fft the data
        spec = _fftData(date,data)



        #get the magnetometer position for tracing
        pos = _magPos(date,stn,spec["utc"])

        out = {
            'data' : data,
            'spec' : spec,
            'pos' : pos
        }

        #save

        pf.SaveObject(out,fname)
        print('Saved: ',fname)
    except Exception as e:
        print('Saving {:s} failed, creating empty file...'.format(fname))
        os.system('touch '+fname)
        if debug:
            print(f"Error: {e}")
            print(traceback.format_exc())