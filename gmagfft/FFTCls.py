import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from .tools.checkPath import checkPath
import wavespec as ws
from .data.getSpecs import getSpecs
from . import globs
import os
import DateTimeTools as TT
import PyFileIO as pf
import groundmag as gm
from .tools.figText import figText
from . import profile


class FFTCls(object):
	def __init__(self,stn,Date):
		self.stn = stn.upper()
		self.date = Date
		
		try:
			self.data = getSpecs(Date,stn)
			self.spec = self.data['spec']
			self.pos = self.data['pos']
			for k in self.pos.keys():
				setattr(self,k,self.pos[k])
			self.data = self.data['data']
			self.freq = self.spec['freq']
			self.freqax = self.spec['freqax']
			self.utc = self.spec['utc']
			self.utcax = self.spec['utcax']
		except Exception as e:
			print('Something went wrong')
			print(e)
			self.fail = True
			return None

				
	def PlotData(self,date=None,ut=[0.0,24.0],Comp=['x','y','z'],fig=None,maps=[1,1,0,0],nox=False,noy=False,Filter=None,ShowLegend=False,subtractMean=True):
		
		if date is None:
			date = [np.min(self.date),np.max(self.date)]
		

		cols = {'x':'red',
				'y':'lime',
				'z':'blue'}
		
		utclim = TT.ContUT(date,ut)
		
		use = np.where((self.data.utc >= utclim[0]) & (self.data.utc <= utclim[1]))[0]
		data = self.data[use]
		
	
		if fig is None:
			fig = plt
			fig.figure()
		if hasattr(fig,'Axes'):	
			ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		else:
			ax = fig
					
		for c in Comp:
			b = data['B'+c]
			if not Filter is None:
				b = ws.Filter.Filter(b,1.0,1/Filter[0],1/Filter[1])
			if subtractMean:
				mu = np.nanmean(b)
				b -= mu
			ax.plot(data.utc,b,color=cols[c],label='$B_'+c+'$')
		
		ax.set_xlim(utclim)


		if nox:
			ax.set_xlabel('')
			n = len(ax.get_xticks())
			lab = ['']*n
			ax.set_xticklabels(lab)
		else:
			ax.set_xlabel('UT')
			TT.DTPlotLabel(ax)
		
		if noy:
			ax.set_ylabel('')
			n = len(ax.get_yticks())
			lab = ['']*n
			ax.set_yticklabels(lab)
		else:
			ax.set_ylabel('')

		ylim = ax.get_ylim()

					
						
		ax.set_xlim(utclim)
		ax.set_ylim(ylim)
		if ShowLegend:
			ax.legend()

		title = '{:s} mlat={:5.2f}, mlon={:5.2f}'.format(self.stn.upper(),self.mlat,self.mlon)
		figText(ax,0.01,0.99,title,color='black',transform=ax.transAxes,ha='left',va='top')

						
		return ax


		

	def _Plot(self,xg,yg,grid,fig=None,maps=[1,1,0,0],zlog=False,scale=None,zlabel='',cmap='gnuplot',ShowColorbar=True):
		'''
		Plot a 2D grid
		
		Inputs
		======
		xg : float
			1-D array length nx+1 defining edges of horizontal color mesh 
			boxes
		yg : float
			1-D array length ny+1 defining the vertical edges of the color 
			mesh boxes
		grid : float
			2D array, shape (nx,ny) of values to be plotted
		fig : object
			None - new figure will be created
			matplotlib.pyplot instance - new Axes to be created on current 
			plot
			matplotlib.pyplot.Axes instance - current axes will be plotted 
			over
		maps : list|tuple
			4-element array denoting the number of horizontal (xmaps) and
			vertical (ymaps) subplots on the figure, and the position of
			the current subplot horizontally (xmap) and vertically (ymap)
			from the top left. maps = [xmaps,ymaps,xmap,ymap]
		zlog : bool
			If True, the color scale will be logarithmic
		scale : None|list
			Color scale min/max limits
		zlabel : str
			Color bar label
		cmap : str
			Name of color map to use
			
		Returns
		=======
		ax : object
			Axes instance
		
			
		'''

		#get the scale
		if scale is None:
			if zlog:
				scale = [np.nanmin(grid[grid > 0]),np.nanmax(grid)]
			else:
				scale = [np.nanmin(grid),np.nanmax(grid)]
		
		
		#set norm
		if zlog:
			norm = colors.LogNorm(vmin=scale[0],vmax=scale[1])
		else:
			norm = colors.Normalize(vmin=scale[0],vmax=scale[1])	
		

		
		if fig is None:
			fig = plt
			fig.figure()
		if hasattr(fig,'Axes'):	
			ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		else:
			ax = fig
			
		sm = ax.pcolormesh(xg,yg,grid.T,cmap=cmap,norm=norm)

		fig.subplots_adjust(right=0.9)
		
		if ShowColorbar:
			box = ax.get_position()
			cax = plt.axes([0.01*box.width + box.x1,box.y0+0.1*box.height,box.width*0.0125,box.height*0.8])
			cbar = fig.colorbar(sm,cax=cax)
			cbar.set_label(zlabel)
			
		return ax


	def GetSpectrum(self,date,ut,Param):
		
		
		utc = TT.ContUT(date,ut)[0]
		dt = np.abs(utc - self.utc)
		I = np.argmin(dt)		
		
		spec = self.spec[Param]
		
		return self.utc[I],self.freq,spec[I]
	
	
	def PlotSpectrum(self,date,ut,Param,flim=None,fig=None,maps=[1,1,0,0],
				nox=False,noy=False,ylog=False,label=None,dy=0.0):
		
		utc,freq,spec = self.GetSpectrum(date,ut,Param)
		
		if fig is None:
			fig = plt
			fig.figure()
		if hasattr(fig,'Axes'):	
			ax = fig.subplot2grid((maps[1],maps[0]),(maps[3],maps[2]))
		else:
			ax = fig
		
		ax.plot(freq*1000,spec+dy,label=label)
		
		if nox:
			ax.set_xlabel('')
			n = len(ax.get_xticks())
			lab = ['']*n
			ax.set_xticklabels(lab)
		else:
			ax.set_xlabel('$f$ (mHz)')
		
		if noy:
			ax.set_ylabel('')
			n = len(ax.get_yticks())
			lab = ['']*n
			ax.set_yticklabels(lab)
		else:
			ax.set_ylabel('')
		
		if ylog:
			ax.set_yscale('log')
		
		if flim:
			ax.set_xlim(flim)
		else:
			ax.set_xlim(self.freq[0]*1000.0,self.freq[-1]*1000.0)
			
		return ax		
		
		
		
	def Plot(self,Param,date=None,ut=[0.0,24.0],flim=None,fig=None,maps=[1,1,0,0],zlog=False,scale=None,
				cmap='gnuplot2',zlabel='',nox=False,noy=False,ShowPP=True,ShowColorbar=True):
		

		if date is None:
			date = [np.min(self.date),np.max(self.date)]
		
	
		utclim = TT.ContUT(date,ut)


		#get ut range
		uset = np.where((self.utc >= utclim[0]) & (self.utc <= utclim[1]))[0]
		t0 = uset[0]
		t1 = uset[-1] + 1
		utc = self.utcax[t0:t1+1]
				
		#and frequency range
		if flim is None:
			f0 = 0
			f1 = self.freq.size
			flim = np.array([self.freqax[0],self.freqax[-1]])*1000.0
		else:
			usef = np.where((self.freq*1000.0 >= flim[0]) & (self.freq*1000.0 <= flim[1]))[0]
			f0 = usef[0]
			f1 = usef[-1] + 1
		freq = self.freqax[f0:f1+1]*1000.0
		
		spec = self.spec[Param]
		spec = spec[t0:t1,f0:f1]	
		
		
		ax = self._Plot(utc,freq,spec,fig=fig,maps=maps,zlog=zlog,
				scale=scale,zlabel=zlabel,cmap=cmap,ShowColorbar=ShowColorbar)
		
		
		utclim = TT.ContUT(np.array([self.date,self.date]),np.array(ut))
		ax.set_xlim(utclim)
		ax.set_ylim(flim)
		
		if nox:
			ax.set_xlabel('')
			n = len(ax.get_xticks())
			lab = ['']*n
			ax.set_xticklabels(lab)
		else:
			ax.set_xlabel('UT')
			TT.DTPlotLabel(ax)
		
		if noy:
			ax.set_ylabel('')
			n = len(ax.get_yticks())
			lab = ['']*n
			ax.set_yticklabels(lab)
		else:
			ax.set_ylabel('$f$ (mHz)')



		
		title = '{:s} mlat={:5.2f}, mlon={:5.2f}'.format(self.stn.upper(),self.mlat,self.mlon)
		figText(ax,0.01,0.99,title,color='black',transform=ax.transAxes,ha='left',va='top')
		
		return ax
	
	
		
	def _PowPeaks(self,Comp,flim):
		
		
		n = np.size(self.utc)
		t = np.copy(self.utc)
		ti = np.arange(n)
		
		
		if flim is None:
			usef = np.arange(self.freq.size)
		elif np.size(flim) == 1:
			df = np.abs(flim - self.freq)
			fi = np.zeros(n,dtype='int32') + df.argmin()
			f = self.freq[fi]
			return t,ti,f,fi		
		else:
			usef = np.where((self.freq >= flim[0]) & (self.freq <= flim[1]))[0]
			
		P = np.array(self.spec[Comp+'Pow'])
		Pf = P[:,usef]
		
		fi = usef[Pf.argmax(axis=1)]
		f = self.freq[fi]
		
		return t,ti,f,fi
		
		
	def PlotPol(self,date=None,ut=[0.0,24.0],flim=None,fig=None,maps=[1,1,0,0],
					Comp='x',nox=False,noy=False,Mult=None,MinAmp=0.0):
						
		if date is None:
			date = [np.min(self.date),np.max(self.date)]
		
		#get the peak power within frequency range
		t,ti,f,fi = self._PowPeaks(Comp,flim)
		
		#limit time
		tlim = TT.ContUT(date,ut)
		use = np.where((t >= tlim[0]) & (t <= tlim[1]))[0]
		t = t[use]
		ti = ti[use]
		f = f[use]
		fi = fi[use]
		
		#get polarization parameters
		kdotB = self.spec['kdotB'][ti,fi]
		Axi = self.spec['Axi'][ti,fi]
		Ax = self.spec['Ax'][ti,fi]
		Ay = self.spec['Ay'][ti,fi]
		Px = self.spec['xPha'][ti,fi]
		Py = self.spec['yPha'][ti,fi]
		
		Dir = kdotB >= 0
		bad = np.where(Axi < MinAmp)[0]
		Ax[bad] = np.nan
		Ay[bad] = np.nan
		
		if Mult is None:
			Mult = 1.0


		#create the plot
		ax = ws.Tools.PlotPolarization(t,Ax,Ay,Px,Py,Dir,fig=fig,maps=maps,Multiplier=Mult,nox=nox,trange=None,TimeAxisUnits='s')	
			

		

		#set the y label and the position text
		
		ax.set_xlim(tlim)
		if nox:
			ax.set_xlabel('')
			n = len(ax.get_xticks())
			lab = ['']*n
			ax.set_xticklabels(lab)
		else:
			ax.set_xlabel('UT')
		yl = ax.get_ylim()
		ax.set_ylim(yl)
		if noy:
			ax.set_ylabel('')
			n = len(ax.get_yticks())
			lab = ['']*n
			ax.set_yticklabels(lab)
		else:
			ax.set_ylabel('')
		
		ax.set_xlim(tlim)		
		
		ax.set_ylim(yl)
	
		title = '{:s} mlat={:5.2f}, mlon={:5.2f}'.format(self.stn,self.mlat,self.mlon)
		figText(ax,0.01,0.99,title,color='black',transform=ax.transAxes,ha='left',va='top')
	
		
		return ax
	
	def _GetTraceFP(self):
		
		if not hasattr(self,'Trace'):
			self.Trace = gm.Trace.InterpMagFP(self.stn,self.utc)
			if self.Trace is None:
				gm.Trace.SaveMagTrace(self.stn,self.utc)
				self.Trace = gm.Trace.InterpMagFP(self.stn,self.utc)
		
		return self.Trace


	def PlotEqFP(self,ut=[0.0,24.0],fig=None,maps=[1,1,0,0]):
		
		return PlotEqMagFP(self.stn,self.date,ut=ut,fig=fig,maps=maps)
