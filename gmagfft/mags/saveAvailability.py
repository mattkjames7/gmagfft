import numpy as np
import groundmag as gm
import PyFileIO as pf
from ..Tools.checkPath import checkPath
from .. import globs

def saveAvailability(stn):
	'''
	Save the availability for a pair of magnetometers
	
	'''
	dates = gm.GetDataAvailability(stn)
	
	fpath = globs.dataPath + '/availability'
	checkPath(fpath)
	
	fname = fpath + '/{:s}.bin'.format(stn)
	
	f = open(fname,'wb')
	pf.ArrayToFile(dates,'int32',f)
	f.close()
