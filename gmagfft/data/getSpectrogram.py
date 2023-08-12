import numpy as np
import DateTimeTools as TT
import groundmag as gm
import wavespec as ws
from .. import profile

def _getWindows(data,Date):
	
	cfg = profile.get()
	window = cfg['window']
	slip = cfg['slip']
	res = cfg.get('res',1.0)

	#get current time axis in seconds
	utc0 = TT.ContUT(Date,0.0)[0]
	tsec = (data.utc - utc0)*3600.0
	
	
	#get the number of windows using the imte range
	T0 = -window
	T1 = 86400 + window
	
	nw = np.int32(np.round((T1 - T0 - window)/slip)) + 1
	
	#get the indices of each start and end element of each window
	#(split this up before doing LS or Res != 1.0)
	t0 = np.arange(nw)*slip - window
	t1 = t0 + window
	tc = np.float64(t0) + window/2.0
	
	i0 = np.int32(np.round((t0 + window)/res))
	i1 = np.int32(np.round((t1 + window)/res))

	
	#now the groups of windows for coherence
	nc = np.int32(np.round(window//slip)) + 1
	cnw = nw - nc + 1
	ci0 = np.arange(cnw)
	ci1 = ci0 + nc
	ctc = tc[nc//2:-(nc//2+1)]
	
	return nw,i0,i1,tc,cnw,ci0,ci1,ctc
	
def _getFrequencies():

	cfg = profile.get()
	window = cfg['window']
	res = cfg.get('res',1.0)


	freq = np.arange(window+1,dtype='float64')/(np.float32(window*res))
	nf = np.size(freq) - 1
	nf = nf//2
	freq = freq[:nf]		

	return nf,freq
	
def _magPos(stn,t_utc):
	
	stn = gm.GetStationInfo(stn)
	glat = stn.glat[0]*np.pi/180.0
	glon = stn.glon[0]*np.pi/180.0
	t_date,t_ut = TT.ContUTtoDate(t_utc)
	g_z = np.zeros(t_utc.size) + 1.02*np.sin(glat)
	g_x = np.zeros(t_utc.size) + 1.02*np.cos(glon)*np.cos(glat)
	g_y = np.zeros(t_utc.size) + 1.02*np.sin(glon)*np.cos(glat)

	return g_x,g_y,g_z
	
	
def _getKVectors(xfft,yfft,zfft):


	Jxy = xfft.imag*yfft.real - yfft.imag*xfft.real
	Jxz = xfft.imag*zfft.real - zfft.imag*xfft.real
	Jyz = yfft.imag*zfft.real - zfft.imag*yfft.real
	A = np.sqrt(Jxy**2 + Jxz**2 + Jyz**2)	
	kx = Jyz/A
	ky =-Jxz/A
	kz = Jxy/A		
	
	return kx,ky,kz	

def getSpectrogram(data,Date):

	cfg = profile.get()
	window = cfg['window']
	slip = cfg['slip']
	res = cfg.get('res',1.0)
	freq0 = cfg['freq0']
	freq1 = cfg['freq1']
	detrend = cfg['detrend']

	tsec = (data.utc - TT.ContUT(Date,0.0)[0])*3600.0
	
	#calculate windows
	nw,i0,i1,tc,cnw,ci0,ci1,ctc = _getWindows(data,Date)
	
	#get the frequencies
	nf,freq = _getFrequencies()
	#nf = nf//2
	#freq = freq[:nf+1]

	#get the Fourier spectra
	fft = {}
	Bfield = {}
	fields = ['Bx','By','Bz']
	comps = ['x','y','z']

	for f,c in zip(fields,comps):

		fft[c+'Pow'] = np.zeros((nw,nf),dtype='float64')
		fft[c+'Pha'] = np.zeros((nw,nf),dtype='float64')
		fft[c+'Amp'] = np.zeros((nw,nf),dtype='float64')
		fft[c+'FFT'] = np.zeros((nw,nf),dtype='complex128')		
		Bfield[f] = np.zeros((nw,),dtype='float64')
		for i in range(0,nw):
			ind = np.arange(i0[i],i1[i])
			t = tsec[ind]
			if np.isfinite(data[f][ind]).sum() > 2:
				b = ws.Tools.PolyDetrend(t,data[f][ind],detrend)

				Bfield[f][i] = np.nanmean(data[f][ind])
				
				pw,am,ph,fr,fi,_ = ws.Fourier.FFT(t,b,OneSided=True)
				fft[c+'Pow'][i] = pw
				fft[c+'Amp'][i] = am
				fft[c+'Pha'][i] = ph
				fft[c+'FFT'][i] = fr + 1.0j*fi
			else:
				Bfield[f][i].fill(np.nan)
				fft[c+'Pow'][i].fill(np.nan)
				fft[c+'Amp'][i].fill(np.nan)
				fft[c+'Pha'][i].fill(np.nan)
				fft[c+'FFT'][i].fill(np.nan)

	#limit frequency range
	usef = np.where((freq >= freq0) & (freq <= freq1))[0]
	keys = list(fft.keys())
	for k in keys:
		fft[k] = fft[k][:,usef]
	freq = freq[usef]
	nf = freq.size

	#limit to stuff from this date
	usefft = np.where((tc >= 0.0) & (tc <86400))[0]
	
	#output array
	spec = {}
	spec['nw'] = usefft.size
	spec['i0'] = i0
	spec['i1'] = i1
	spec['tsec'] = tc[usefft]
	spec['utc'] = TT.ContUT(Date,0.0)[0] + tc[usefft]/3600.0
	spec['utcax'] = np.append(spec['utc']-0.5*slip/3600.0,spec['utc'][-1] + 0.5*slip/3600.0)
	spec['nf'] = nf
	spec['freq'] = freq
	df = freq[1]
	spec['freqax'] = np.append(freq,freq[-1]+df)
	
	keys = list(fft.keys())
	for k in keys:
		spec[k] = fft[k][usefft]

	#magnetic field
	spec['Bx'] = Bfield['Bx'][usefft]
	spec['By'] = Bfield['By'][usefft]
	spec['Bz'] = Bfield['Bz'][usefft]
		
	#unit vector for B
	B = np.sqrt(spec['Bx']**2 + spec['By']**2 + spec['Bz']**2)
	uBx = spec['Bx']/B
	uBy = spec['By']/B
	uBz = spec['Bz']/B
		
	#kvector
	spec['kx'],spec['ky'],spec['kz'] = _GetKVectors(spec['xFFT'],spec['yFFT'],spec['zFFT'])
	
	#k.B
	spec['kdotB'] = (spec['kx'].T*uBx + spec['ky'].T*uBy + spec['kz'].T*uBz).T 
	
	#calculate polarizations
	pol = ws.Tools.Polarization2D(spec['xPow'],spec['xPha'],spec['yPow'],spec['yPha'],ReturnType='dict')
	keys = list(pol.keys())
	for k in keys:
		spec[k] = pol[k]
		
				
	return spec
