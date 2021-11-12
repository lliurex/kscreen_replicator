#!/usr/bin/env python3
#Copyright 2021 LliureX Team
#This script is licensed under GPL-3 license

import dbus,dbus.exceptions
import logging

class kscreenDbus():
	def __init__(self,*args,**kwargs):
		logging.basicConfig(format='%(message)s')
		self.dbg=True
		#Mandatory
		self.maxW=640
		#Optional. 0 for disable
		self.maxH=0
		self.bus=self._getBus()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			logging.warning("ReplicateScreen: %s"%str(msg))
	#def _debug

	def _getBus(self):
		bus=dbus.SessionBus()
		objectBus=bus.get_object("org.kde.KScreen","/backend")
		return(objectBus)
	#def _getBus

	def getConfig(self):
		config=self.bus.getConfig()
		return(config)
	#def getConfig

	def getMaxCommonResolution(self,config):
		outputs=config.get('outputs',{})
		modesDict={}
		sizesDict={}
		if self.maxH==0:
			maxH=99999
		else:
			maxH=self.maxH
		for section in outputs:
			modesDict[section.get('name','*')]=[]
			modes=section.get('modes')
			for mode in modes:
				idMode=mode.get('id')
				sizeMode=mode.get('size')
				if isinstance(sizeMode,dict):
					sizeH=sizeMode.get('height')
					sizeW=sizeMode.get('width')
				modesDict[section.get('name','*')].append(idMode)
				if not sizesDict.get(idMode,None):
					sizesDict[idMode]=(sizeW,sizeH)

		screens=list(modesDict.keys())
		self._debug("Values for {}".format(screens[0]))
		maxRes=(0,0)
		selectId=0
		for modeId in modesDict[screens[0]]:
			print("mode id:{0}".format(modeId))
			if modeId in modesDict[screens[1]]:
				sizes=sizesDict.get(modeId)
				if sizes:
					(w,h)=sizes
					print("* {0} {1}".format(w,h))
					if maxRes[0]<w and w<=self.maxW:
						if maxRes[1]<h  and h<=maxH:
							maxRes=(w,h)
							self._debug("Change {} for {}".format(selectId,modeId))
							selectId=modeId
					self._debug("Common value: {} -> {}x{}".format(modeId,w,h))
		return(selectId)
	#def getMaxCommonResolution

	def setResolution(self,config,selectId):
		if self.dbg:
			with open('oldConf','w') as f:
				f.write(str(config))
			self._debug("Generated oldConf with original values")

		self._debug("Setting resolution id {} for monitors".format(selectId))
		for output in config.get('outputs'):
			if output.get('currentModeId'):
				print("Change monitor {} current modeId {} to modeId {}".format(output.get('name'),output.get('currentModeId'),selectId))
				output.update(({dbus.String('currentModeId'):dbus.String(selectId)}))
			pos=output.get('pos')
			if pos:
				pos.update({dbus.String('x'):dbus.Int64(0),dbus.String('y'):dbus.Int64(0)})
		self.bus.setConfig(config)
		if self.dbg:
			with open('newConf','w') as f:
				f.write(str(config))
			self._debug("Generated newConf with actual values")
	#def setResolution
			

bus=kscreenDbus()
config=bus.getConfig()

match={}
for output in config.get("outputs"):
    if (output.get("connected")):
        name = output.get("name")

        for mode in output.get("modes"):
            w=mode.get("size").get("width")
            h=mode.get("size").get("height")
            pixels = w*h

            if not pixels in match:
                match[pixels]={}
            if not name in match[pixels]:
                match[pixels][name]=[]

            match[pixels][name].append(mode.get("id"))

candidate=-1
for m in sorted(match.keys()):
    if (len(match[m].keys())>1):
        candidate=m
        print("pixels:",m)
        for k in match[m]:
            print("* ",k)
            for i in match[m][k]:
                print("\t ",i)

print("selected:",candidate)
cfg = match[candidate]

for output in config.get("outputs"):
    if (output.get("connected")):
        name = output.get("name")
        if name in cfg:
            print("- setting mode {0} to {1}".format(cfg[name][0],name))
            output.update(({dbus.String('currentModeId'):dbus.String(cfg[name][0])}))
            pos=output.get('pos')
            pos.update({dbus.String('x'):dbus.Int64(0),dbus.String('y'):dbus.Int64(0)})

print("setting...")
bus.bus.setConfig(config)
#selectId=bus.getMaxCommonResolution(config)
#bus._debug("Selected mode: {}".format(selectId))
#bus.setResolution(config,selectId)
