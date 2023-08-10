import numpy as np
from .listNetworkMags import listNetworkMags
from .readAvailability import readAvailability

def networkAvailabilityDate(Date,Network):
	

	stns = listNetworkMags(Network)
	
	n = len(pairs)
	avail = []
	stn = []
	for s in stns:
		stn.append(s)
		dates = readAvailability(s)
		avail.append(Date in dates)
		
	return np.array(stn),np.array(avail)
