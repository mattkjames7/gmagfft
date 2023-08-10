import numpy as np
import PyFileIO as pf
from .. import Globals
import os

def readAvailability(stn):
	
	
	fpath = Globals.DataPath + '/Availability'	
	fname = fpath + '/{:s}.bin'.format(stn)
	
	if not os.path.isfile(fname):
		return np.array([],dtype='int32')
	
	f = open(fname,'rb')
	dates = pf.ArrayFromFile('int32',f)
	f.close()
	
	return dates