# coding=utf-8
from robofab import *
from mojo.UI import *
from mojo.events import addObserver, removeObserver
from mojo.drawingTools import *
from vanilla import *
from lib.tools.defaults import getDefault, setDefault
from lib.tools.notifications import PostNotification
from lib.eventTools.eventManager import publishEvent
from mojo.extensions import getExtensionDefault, setExtensionDefault, getExtensionDefaultColor, setExtensionDefaultColor
from random import choice
from mojo.roboFont import CurrentFont, CurrentGlyph
from AppKit import NSImageNameRefreshTemplate, NSColor
from lib.UI.toggleImageButton import ToggleImageButton
from mojo.roboFont import RGlyph
from drawBot import BezierPath
from mojo.UI import CurrentGlyphWindow
from vanilla.dialogs import askYesNo, getFile
from defconAppKit.windows.baseWindow import BaseWindowController
import os

f = CurrentFont()
g = CurrentGlyph()

from mojo.events import postEvent

event = "drawBackground" 

import morflib, morfdsd
reload(morflib)
reload(morfdsd)
from morflib import GetMorfGlyph 
from morfdsd import MakeDSD 

def writePathInGlyph(path, glyph):
	pen = glyph.getPen()
	path.drawToPen(pen)
	#glyph.width = w*widthBy


class GlyphMorf(BaseWindowController):
		
	def __init__(self):
		self.font = CurrentFont()
		if not self.font:
			print "Open a font, and try again."
			return
		self.prepareFont(self.font)
		self.w = FloatingWindow((250, 390), "GlyphMorf", closable = True)
		smax = 61
		y=2
		self.w.recipeTitle = TextBox((2,y,-0,15), "recipe:", sizeStyle='mini')
		y+=15
		self.w.recipe = PopUpButton((10,y,-10,22), self.font.lib['morf']['recipes'], callback=self.recipeCallback)
		y+=30
		self.w.newRecipe = SquareButton((10,y,30,30),u"🌟",callback=self.newRecipe)
		self.w.delRecipe = SquareButton((50,y,30,30),u"⛔",callback=self.delRecipe)
		self.w.default = SquareButton((90,y,30,30), u"🔹", callback=self.setDefaultRecipe)
		self.w.getDefault = SquareButton((130,y,30,30), u"⚡", callback=self.setDefaultValuesToSliders)
		#self.w.setFontAsRecipe = SquareButton((170,y,30,15), u"🔺", callback=self.getUFO4Recipe)
		#self.w.delFontAsRecipe = SquareButton((170,y+15,30,15), u"🔻", callback=self.delUFO4Recipe)
		self.w.setIndiValue = SquareButton((170,y,30,30), u"▪️", callback=self.setIndiValues)
		self.w.delIndiValue = SquareButton((-40,y,30,30), u"▫️", callback=self.delIndiRecipe)
		y+=50

		self.w.widthTitle = TextBox((2,y,-0,15), "width by:", sizeStyle='mini')
		y+=15
		self.w.width=Slider((2,y,-50,22),minValue=0, maxValue=2, value=1,callback=self.update,tickMarkCount=smax,stopOnTickMarks=True)
		self.w.widthRead=TextBox((-40,y,-2,22),self.w.width.get())
		y+=30
		
		self.w.heightTitle = TextBox((2,y,-0,15), "height by:", sizeStyle='mini')
		y+=15
		self.w.height=Slider((2,y,-50,22),minValue=0, maxValue=2, value=1,callback=self.update,tickMarkCount=smax,stopOnTickMarks=True)
		self.w.heightRead=TextBox((-40,y,-2,22),self.w.height.get())
		y+=30
		
		self.w.weightTitle = TextBox((2,y,-0,15), "weight by: (x,y)", sizeStyle='mini')
		y+=15
		self.w.weightx=Slider((2,y,-50,22),minValue=0, maxValue=2, value=1,callback=self.update,tickMarkCount=smax,stopOnTickMarks=True)
		self.w.weightxRead=TextBox((-40,y,-2,22),self.w.weightx.get())
		y+=30
		self.w.weighty=Slider((2,y,-50,22),minValue=0, maxValue=2, value=1,callback=self.update,tickMarkCount=smax,stopOnTickMarks=True)
		self.w.weightyRead=TextBox((-40,y,-2,22),self.w.weighty.get())
		y+=30
		self.w.centerTitle = TextBox((2,y,-0,15), "center factor:", sizeStyle='mini')
		y+=15
		self.w.centerr=Slider((2,y,-50,22),minValue=0, maxValue=1, value=.5,callback=self.update,tickMarkCount=41,stopOnTickMarks=True)
		self.w.centerRead=TextBox((-40,y,-2,22),self.w.centerr.get())
		# self.w.colorFill = ColorWell((7,7,-7,23), callback = self.changeColor)
		# self.w.colorFill.set(NSColor.colorWithCalibratedRed_green_blue_alpha_(*self.fillColor))
		y+=30
		self.w.onOff = CheckBox((10,y,100,22),"on/off",value=1,callback=self.update,)
		# self.w.rec = CheckBox((120,y,-10,22),"rec", value=0)
		y+=40

		self.w.makeDSD = SquareButton((10,y,40,30),u"""DSD""", sizeStyle='mini', callback=self._makeDSD)
		self.w.getMorfFont = SquareButton((60,y,40,30),u"""get\nfont""", sizeStyle='mini', callback=self.getMorfFont)
	
		
		addObserver(self, "mainFunction", event)
		addObserver(self, "glyphChanged", "currentGlyphChanged")
		self.setUpBaseWindowBehavior()
		self.w.open()
		self.updateView(None)
		
		#self.hasLib()

		
	# def hasLib(self):
	# 	if 'morf' in self.font.lib.keys():
	# 		if 'recipes' in self.font.lib['morf'].keys():
	# 			self.w.recipe.setItems(self.font.lib['morf']['recipes'])
	# 			return True
	# 		else:
	# 			self.w.recipe.setItems([])
	# 	else:
	# 		self.w.recipe.setItems([])
				
	
	def getUfo(self, sinder):
		ufoPath = getFile()[0]
		self.ufo = OpenFont(ufoPath, showUI=False)
		PostNotification('doodle.updateGlyphView')
	
	def changes(self,sender):
		PostNotification('doodle.updateGlyphView')
			
	def windowCloseCallback(self, sender):
		self.w.hide()
		removeObserver(self, event)
		removeObserver(self, "currentGlyphChanged")
		PostNotification('doodle.updateGlyphView')

	def _close(self,sender):
		self.w.hide()
		removeObserver(self, event)
		removeObserver(self, "currentGlyphChanged")
		PostNotification('doodle.updateGlyphView')

	def mainFunction(self, info):
		if info['glyph']:
			# self.prepareFont(info)
			#if not getExtensionDefault(settingsWindow):
			#	self.settingsWindow(onOff=True)
			
			#self.w = getExtensionDefault(settingsWindow)	
			g = info['glyph']
			if 1:#self.w.onOff.get():
				if not len(self.font.lib['morf']['recipes'].keys()):
					self.currentRecipe = None
				else:
					self.currentRecipe = self.font.lib['morf']['recipes'].keys()[self.w.recipe.get()]
				
					
					###
					#glyphStruc = getStrucGlyph(g, self.w.centerr.get())
					#glyphPath = getMorfGlyphAsPath(glyphStruc, (self.w.weightx.get(), self.w.weighty.get()), self.w.width.get(), self.w.height.get())
					
				glyphPath = GetMorfGlyph(g, self.w.centerr.get(), self.w.weightx.get(), self.w.weighty.get(), self.w.width.get(), self.w.height.get()).path
				badTypes = [type(""), type(None)]
				if type(glyphPath) not in badTypes:
					self.drawMorf(g,glyphPath)
				else:
					self.drawError(g)
				
				self.widthBy = self.w.width.get()
				self.heightBy = self.w.height.get()
				self.weigtByX = self.w.weightx.get()
				self.weigtByY = self.w.weighty.get()
				self.factor = self.w.centerr.get()

				
				
				# if 'morf' in g.lib:
				# 	if self.currentRecipe in g.lib['morf'].keys():
				# 		l = g.lib['morf'][self.currentRecipe]
				# 		self.widthByMem = l['widthBy']
				# 		if 'heightBy' in l.keys():
				# 			self.heightByMem = l['heightBy']
				# 		else:
				# 			self.heightByMem = 1
				# 		self.weigtByMen = l['weightBy']
				# 		self.factorMem = l['factor']

				# prep glyph

	def setIndiValues(self, sender):
		self.roundValues()
		g = CurrentGlyph()
		if 'morf' not in g.lib.keys(): 
			g.lib['morf'] = {}
		g.lib['morf'][self.currentRecipe] = {}

		l = g.lib['morf'][self.currentRecipe]

		l['widthBy'] = self.width
		l['heightBy'] = self.height
		l['weightByX'] = self.weightx
		l['weightByY'] = self.weighty
		l['factor'] = self.factor
			

	def drawMorf(self, g, path):
		if self.w.onOff.get():
			save()
			translate(g.width,0)
			fill(0)
			#stroke(1,0,0)
			q = RGlyph()
			writePathInGlyph(path, q)
			drawGlyph(q)
			restore()

	def drawError(self,g):
		if self.w.onOff.get():
			save()
			translate(g.width,0)
			fill(1,0,0)
			font("Verdana-Bold",100)
			text("X",(30,30,))
			restore()


	def getDefaultValues(self):
		if self.w.recipe.get() != -1:
			self.currentRecipe = self.font.lib['morf']['recipes'].keys()[self.w.recipe.get()]
			defValDict = self.font.lib['morf']['recipes'][self.currentRecipe]['default']
			self.widthBy=defValDict['widthBy']
			self.heightBy=defValDict['heightBy']
			self.weightByX=defValDict['weightByX']
			self.weightByY=defValDict['weightByY']
			self.factor=defValDict['factor']

	def setDefaultValuesToSliders(self, sender):
			self.getDefaultValues()
			self.w.width.set(self.widthBy)
			self.w.height.set(self.heightBy)
			self.w.weightx.set(self.weightByX)
			self.w.weighty.set(self.weightByY)
			self.w.centerr.set(self.factor)
			self.update(None)
			self.updateView(None)

	def setDefaultRecipe(self, sender):
		
		self.roundValues()
		self.currentRecipe = self.font.lib['morf']['recipes'].keys()[self.w.recipe.get()]
		l = self.font.lib['morf']['recipes'][self.currentRecipe]['default']
		l['widthBy'] = self.width
		l['heightBy'] = self.height
		l['weightByX'] = self.weightx
		l['weightByY'] = self.weighty
		l['factor'] = self.factor

	def newRecipe(self,sender):
		self.sheet = Sheet((200, 70), self.w)
		self.sheet.et = EditText((10,10,-10,22),callback=self.checkValidNewRecipe)
		self.sheet.ok = SquareButton((10,40,-10,22),"ok", callback=self.makeRecipe)
		self.sheet.open()

	def checkValidNewRecipe(self,sender):
		if self.sheet.et.get() not in self.font.lib['morf']['recipes'].keys():
			return True
		else:
			return False

	def makeRecipe(self, sender):
		if self.checkValidNewRecipe(None):
			self.font.lib['morf']['recipes'][str(self.sheet.et.get())] = {'default':{
			'widthBy':1,
			'heightBy':1,
			'weightByX': 1,
			'weightByY': 1,
			'factor': .5,
			}} 
		
		self.w.recipe.setItems(self.font.lib['morf']['recipes'].keys())
		# set new rec as cur
		self.w.recipe.set( self.w.recipe.getItems().index( str(self.sheet.et.get())))
		self.sheet.close()

	def delRecipe(self, sender):
		self.currentRecipe = self.font.lib['morf']['recipes'].keys()[self.w.recipe.get()]
		answer = askYesNo(messageText="Really want to DELETE recipe: %s" % self.currentRecipe, informativeText="No undo here!")
		if answer:
			#pass
			del self.font.lib['morf']['recipes'][self.currentRecipe]
			self.font.update()
			for g in self.font:
				if 'morf' in g.lib.keys():
					for k in g.lib['morf'].keys():
						if k == self.currentRecipe:
							del g.lib['morf'][k]
							g.update()
		self.w.recipe.setItems(self.font.lib['morf']['recipes'].keys())
		self.mainFunction({"glyph":CurrentGlyph()})

	def getUFO4Recipe(self, sender):
		self.currentRecipe = self.font.lib['morf']['recipes'].keys()[self.w.recipe.get()]
		self.sheet = Sheet((300, 100), self.w)
		self.sheet.recipe = TextBox((10,10,-10,13), self.currentRecipe)
		self.sheet.et = EditText((10,35,-10,22))
		self.sheet.ok = SquareButton((10,65,-40,22),"set ufo", callback=self.setUFO2Recipe)
		self.sheet.cancel = SquareButton((-30,65,-10,22),"x", callback=self.setUFO2RecipeCancel)
		self.sheet.open()
		# self.ufo = getFile(messageText="Where is that ufo?", title="UFO as recipe", directory=None, fileTypes=['ufo'], parentWindow=self.w, resultCallback=self.setUFO2Recipe)
		#self.font.lib['morf']['recipes'][self.currentRecipe]['ufo'] = ""

	def setUFO2Recipe(self, sender):
		self.font.lib['morf']['recipes'][self.currentRecipe]['ufo'] = self.sheet.et.get()
		self.sheet.close()

	def setUFO2RecipeCancel(self, sender):
		self.sheet.close()

	def delUFO4Recipe(self, sender):
		del self.font.lib['morf']['recipes'][self.currentRecipe]['ufo']

	def delIndiRecipe(self, sender):
		self.w.rec.set(False)
		if self.currentRecipe in self.glyph.lib['morf'].keys():
			del self.glyph.lib['morf'][self.currentRecipe]
		self.updateView(None)

	def recipeCallback(self, sender):
		if not len(self.font.lib['morf']['recipes'].keys()):
			self.currentRecipe = None
		else:
			self.setDefaultValuesToSliders(None)
			self.update(None)

	def roundValues(self):
		self.width=(round(self.w.width.get(),2))
		self.height=(round(self.w.height.get(),2))
		self.weightx=(round(self.w.weightx.get(),2))
		self.weighty=(round(self.w.weighty.get(),2))
		self.factor=(round(self.w.centerr.get(),2))

	def update(self, sender):
		self.roundValues()

		self.w.widthRead.set(self.width)
		self.w.heightRead.set(self.height)
		self.w.weightxRead.set(self.weightx)
		self.w.weightyRead.set(self.weighty)
		self.w.centerRead.set(self.factor)
		self.updateView(None)

	def _makeDSD(self, sender):
		f = CurrentFont()
		if 'morf' in f.lib.keys():
			if 'recipes' in f.lib['morf'].keys():
				#pass
				MakeDSD(f, f.lib['morf']['recipes'].keys())


	def getMorfFont(self, sender):
		f = CurrentFont()
		self.font = f
		self.currentRecipe = self.font.lib['morf']['recipes'].keys()[self.w.recipe.get()]
		recipe = self.currentRecipe
		nf = f.copy()
		nf.info.styleName = self.currentRecipe

		glyphs = f.keys()		
		
		for gn in glyphs:
			g = f[gn]
			#if 1:
			if 'morf' in g.lib.keys() and recipe in g.lib['morf'].keys():
				self.widthBy = g.lib['morf'][recipe]['widthBy']
				self.heightBy = g.lib['morf'][recipe]['heightBy']
				self.factor = g.lib['morf'][recipe]['factor']
				self.weightByX = g.lib['morf'][recipe]['weightByX']
				self.weightByY = g.lib['morf'][recipe]['weightByY']
			else:
				self.getDefaultValues()
			# self.getDefaultValues()
			path = GetMorfGlyph(g, self.factor, self.weightByX, self.weightByY, self.widthBy, self.heightBy).path
			if path and type(path) != type(""):
				# print g
				nf.newGlyph(g.name)
				nf[g.name].width = g.width*self.widthBy

				writePathInGlyph(path, nf[g.name])
				nf[g.name].round()
			else:
				continue
		nf.showUI()

	def updateView(self, sender):
		PostNotification('doodle.updateGlyphView')
			
			
	def prepareFont(self,curfont):
		"""
		make 'morf' in lib and make first 'Neutral' recipe
		"""
		if 'morf' not in self.font.lib:
				self.font.lib['morf'] = {}
		if 'recipes' not in self.font.lib['morf'].keys():
			self.font.lib['morf']['recipes'] = {} #dict {"RecName":{defaultValues}}
			self.font.lib['morf']['recipes']["Neutral"] = {'default':{
				'widthBy':1,
				'heightBy':1,
				'weightByX': 1,
				'weightByY': 1,
				'factor': .5,}} 

	def glyphChanged(self, info):
		#self.mainFunction(info)
		g = info['glyph']
		self.glyph = info['glyph']
		self.prepareFont(info)

		if hasattr(self, 'w'):

			if not len(self.font.lib['morf']['recipes'].keys()):
				self.currentRecipe = None
			else:
				self.currentRecipe = self.font.lib['morf']['recipes'].keys()[self.w.recipe.get()]

			self.widthByMem = self.w.width.get()
			self.heightByMem = self.w.height.get()
			self.weigtByXMem = self.w.weightx.get()
			self.weigtByYMem = self.w.weighty.get()
			self.factorMem = self.w.centerr.get()


			indi = False
			if 'morf' in g.lib.keys():
				if self.currentRecipe in g.lib['morf'].keys():
					l = g.lib['morf'][self.currentRecipe]
					self.widthByMem = l['widthBy']
					if 'heightBy' in l.keys():
						self.heightByMem = l['heightBy']
					else:
						self.heightByMem = 1
					self.weigtByXMem = l['weightByX']
					self.weigtByYMem = l['weightByY']
					self.factorMem = l['factor']
					indi = True
		
					self.w.width.set(self.widthByMem)
					self.w.height.set(self.heightByMem)
					self.w.weightx.set(self.weigtByXMem)
					self.w.weighty.set(self.weigtByYMem)
					self.w.centerr.set(self.factorMem)

			if not indi:
				self.setDefaultValuesToSliders(None)

			self.update(None)
	





GlyphMorf()

