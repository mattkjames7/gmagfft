import numpy as np
import groundmag as gm

def listNetworkMags(Network=None):
	
	stns = gm.GetStationInfo()
	
	if not Network is None:
		use = np.where(stns.Network == Network)[0]
		stns = stns[use]

	return stns.Code

	
