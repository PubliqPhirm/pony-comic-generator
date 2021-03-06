# coding=UTF-8
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# vim: set fileencoding=UTF-8 :

# A collection of utility functions that don't need to be specific to any part of the program

import random
import os
import textwrap
import math
from pprint import pprint
from PIL import Image
import re

# Something about finding if first and last are in that order in s?
def findBetween(s, first, last):
	try:
		start = s.index(first) + len(first)
		end = s.index(last, start)
		return s[start:end]
	except ValueError:
		return ""

# Draw text centered?
def drawCenteredText(startY, text, draw, fnt, panelSize):
	MAX_W, MAX_H = panelSize[0], panelSize[1]
	current_h, pad = startY, 10
	if text is not None:
		para=textwrap.wrap(text, width=12)
		print('para:')
		pprint(para)
		#draw.text((5,5),para[0],font=fnt)
		for line in para:
			w, h = draw.textsize(line, font=fnt)
			draw.text(
				((MAX_W - w) / 2, current_h),
				line,
				font = fnt,
				fill=(0, 0, 0, 255)
				)
			current_h += h + pad
	return current_h

# Checks that the ponies are under the correct line of dialogue
def isCorrectOrder(txtLine1, txtLine2, nameorder):
	print(('comparing nameorder '+str(nameorder)+" "+txtLine2['name']))
	for name in nameorder:
		if name == txtLine2['name']:
			return False
		if name == txtLine1['name']:
			return True
	return True

# picks a file from a directory
# if the file is also a directory, pick a file from the new directory
# this might choke up if it encounters a directory only containing invalid files
def pickNestedFile(directory, bad_files, seed=None):
	if seed is not None:
		random.seed(seed)
	file = None
	while file is None or file in bad_files:
		file = random.choice(os.listdir(directory))
	#file = directory + file # use the full path name
	print(("Trying " + file))
	if os.path.isdir(os.path.join(directory, file))==True:
		print("It's a directory!")
		return pickNestedFile(directory+"/"+file, bad_files)
	else:
		return directory+"/"+file

# does a 2-pass check through PIL's im.transform() to access all 8 possible outcomes of one rotation optionally followed by one rotation
def imageFlip(image):
	tr = getTransform()
	image = image.transpose(tr)
	tr = getTransform(20)
	if tr is None:
		return image
	else:
		return image.transpose(tr) # 2 passes for best results

# rolls an n-sided die and lets you know if the result is 0
def rollOdds(n, seed=None):
	if seed is not None:
		random.seed(seed)
	n = int(n) # in case you're some wiseguy who uses a non-int to get yourself an error
	if n < 1:
		return false # rolling a die with no sides or negative sides will return false, rather than an error (for now)
	return random.randint(0, n-1) == 0

# give a float decimal for odds
def rollFraction(odds, seed=None):
	if seed is not None:
		random.seed(seed)
	if odds > 1:
		return random.random() < (1.0/float(odds))
	else:
		return random.random() < odds

# generates a list of transformations to feed to PIL's im.transform()
# nullWeight is the relative (to the size of transform_D) likelihood that you don't do any transformation for that step
def getTransformList(length, nullWeight=10):
	list = []
	for i in (1, length):
		list.append(getTransform(nullWeight))
	return list

# applies a list of transformations to an image
def applyTransformList(list, image):
	for transformation in list:
		if transformation is not None:
			image = image.transpose(Image.ROTATE_180)
			# eval(transformation), so we're not relying on the hard-coded internal numbers in the Image module
	return image

# Possibly transforms an image
def possiblyTransform(image, odds, length=2):
	if rollOdds(odds):
		return applyTransformList(getTransformList(length), image)
	else:
		return image

# does the opposite transpositions as applyTranformList
# if these two functions are called immediately after one another, the original image should be returned
# have to go in reverse order for it to work consistently
def undoTransformList(list, image):
	undoList = []
	for transformation in list:
		if transformation is not None:
			undoList.insert(0, undoTransform_D[transformation])
	return applyTransformList(undoList, image)

# picks which transformation will be applied to the image
# really just a wrapper for weightedDictPick that always uses transform_D
def getTransform(allowNothing=None):
	return weightedDictPick(transform_D, int(allowNothing))

# formerly the guts of getTranform, back when that was part of generatePanel.py
# Picks from a weighted probability dictionary
def weightedDictPick(weightedDict, increasedNoneWeight=0, seed=None):
	if seed is not None:
		random.seed(seed)
	return weightedDict.get(
		random.randint(
			1,
			len(list(weightedDict.keys())) + increasedNoneWeight
			) - 1,
		None
		)

'''
Generates the dicts that contain transforms that can be used with PIL's transpose function.
Flip and rotate are relative odds as to which variety of transformation is chosen:
if you're curious about the odds of *any* rotation or *any* reflection, there are 3 rotations and 2 flips.

The commented numbers are the mappings found in PIL/image.py
'''
def genTransformDict(flip=10,rotate=20):
	undoTransform_D={
		'Image.FLIP_LEFT_RIGHT': 'Image.FLIP_LEFT_RIGHT', #0:0
		'Image.FLIP_TOP_BOTTOM': 'Image.FLIP_TOP_BOTTOM', #1:1
		'Image.ROTATE_180': 'Image.ROTATE_180', #3:3
		'Image.ROTATE_90': 'Image.ROTATE_270', #2:4
		'Image.ROTATE_270': 'Image.ROTATE_90' #4:2
	}
	transform_D={}
	genProbabilityDict(
		{
			'Image.FLIP_LEFT_RIGHT':flip, #0
			'Image.FLIP_TOP_BOTTOM':flip, #1
			'Image.ROTATE_90':rotate, #2
			'Image.ROTATE_180':rotate, #3
			'Image.ROTATE_270':rotate #4
		},
		transform_D,
		0)
	return transform_D, undoTransform_D

# Sets the panel size
def setPanelSizes(ps, closeupMultiplier):
	panelSize = ps
	charHeight = 3*panelSize[1]/7
	charHeightCloseup = int(charHeight*closeupMultiplier)
	smallCharHeight = int(charHeight/closeupMultiplier)
	return charHeight, charHeightCloseup, smallCharHeight

# Breaks text at spaces after it reaches the maximum number of characters in a line
def insertLineBreaks(text, maxCharsPerLine):
	words = text.split(" ")
	newstr = ""
	currentCharCount = 0
	for word in words:
		if currentCharCount + len(word) > maxCharsPerLine:
			newstr += "\n"
			currentCharCount = 0
		else:
			newstr += " "
		currentCharCount += len(word) + 1
		newstr += word
	newstr = newstr.strip()
	return newstr

# draw a circle
def circle(draw, center, radius):
	draw.ellipse(
		(
			center[0] - radius + 1,
			center[1] - radius + 1,
			center[0] + radius - 1,
			center[1] + radius - 1
		),
		fill=(255,255,255),
		outline=None
	)


# This could be replaced with a Gaussian distribution with hard limits slapped on
# This also has some inconsistent behavior about whether or not it will ever return high
def triangularInt(low, high, mode, seed=None):
	if seed is not None:
		random.seed(seed)
	return int(random.triangular(low, high, mode))


# Populates a dictionary for random selection with weights from another dictionary
# I'm really sure there's a better way to do this, but I have no idea what it would be
def genProbabilityDict(probabilityTable, outputDict=None, noneWeight=0):
	if outputDict is None:
		outputDict = {}
	counter = 0
	for entry in probabilityTable:
		weight = int(probabilityTable[entry])
		for i in range(counter, counter+weight):
			outputDict[i] = entry
		counter += weight
	for i in range(counter, counter + noneWeight):
		outuptDict[i] = None
	return outputDict


"""
Could also be used as part of a converter from base 10 to other bases

Output is in the form of a dictonary:
{ exponent1: coefficient1, exponent2: coefficient2, etc… }
"""
def decomposeNumericSwitchList(number, base, omitZero = True):
	list = {}
	maxpower = int(math.log(number, base))
	for power in range(maxpower,-1,-1):
		component = base**power
		coefficient = number/component # integer division is important here
		if coefficient != 0 or omitZero is False:
			list[power] = coefficient
		number%=component
	return list

# Decomposes a number used to represent a list of binary choices
# Output is in the form of a list of the powers of 2 that compose the input number
def decomposeBinarySwitches(number):
	return uniqueSumOfPowersList(number,2)

# Output is similar to decomposeNumericSwitchList except it shows a list of "place-values" instead of exponents
def decomposeNumericComponents(number, base):
	componentList = {}

	# The following True parameter isn't necessary, but is there to be extra-clear
	exponentList = decomposeNumericSwitchList(number, base, True)

	for exponent in list(exponentList.keys()):
		componentList[base**exponent] = exponentList[exponent]
	return componentList

# generic version of decomposeBinarySwitches
def uniqueSumOfPowersList(number, base):
	complist = []
	components = decomposeNumericComponents(number, base)
	for component in list(components.keys()):
		complist.append(component*components[component])
	return complist

# check for joined/quit messages and remove them
def quitline(line):
	quitmessage = [
		'(Quit:',
		'has joined (',
		'has left IRC (',
		'has changed mode:',
		'You have joined',
		'set the topic'
	]
	for msg in quitmessage:
		if msg in line:
			return True
	return False

# checks if a line is just some URL
def soloURL(line):
	webendings = [
		'com',
		'net',
		'org',
		'bat',
		'gif',
		'png',
		'jpg',
		'bmp',
		'htm',
		'asp',
		'gov',
		'mil',
		'mp4',
		'mp3',
		'm4v',
		'mkv',
		'.uk',
		'.co',
		'.tk',
		'.pw',
		'.es',
		'.us',
		'.py',
		'.pl',
		'.nl',
		'.ru',
		'.fr',
		'.ca'
	]
	if len(line.split(" ")) > 1:
		return False
	if len(line) < 11:
		return False
	if line[:4].lower() == "http":
		return True
	if line[-3:].lower() in webendings:
		return True
	return True

# similar to pickNestedFile but returns a directory, the directory list, and an index
# assumes that at least one good file exists within the deepest subdirectory
def pickfileIndex(inputfolder, bad_files, seed=None):
	if seed is not None:
		random.seed(seed)
	file = None
	directoryList = os.listdir(inputfolder)
	while file is None or file in bad_files:
		location = random.randint(0, len(directoryList)-1)
		file = directoryList[location]
	if os.path.isdir(os.path.join(inputfolder, file)) is True:
		return pickfileIndex(inputfolder+'/'+file, bad_files)
	else:
		return inputfolder, directoryList, location


# roll for a color
def rollColor(avgR, avgG, avgB, darkness):
	return (
		triangularInt(0, 256, avgR),
		triangularInt(0, 256, avgG),
		triangularInt(0, 256, avgB),
		triangularInt(0, 256, darkness)
		)


# Recursively searches through lines of text to
# remove any words found in nameList.keys() and replace
# them with the corresponding value
def anonWord(wordIn, nameList, joiner='', recheck=True, debugprint=False):
	masterNameList = {}
	if debugprint is True:
		print(('considering: '+wordIn))

	# Don't bother if the word is too short
	if len(wordIn) < 4:
		return wordIn

	if recheck is False:
		if nameList.get(wordIn.lower(), None) is not None:
			print(("removing a name " + wordIn))
			return nameList[wordIn.lower()][1:] # [1:] to get rid of the + in dialogue
		return wordIn

	if joiner != '': # special case for how to parse space-delimited words
		print(("Splitting into words delimited by \'"+joiner+"\'"))
		parts = wordIn.split(joiner)
		recheck = True
	else:
		parts = re.findall(r"\w+|[^\w\s]", wordIn, re.UNICODE)
		recheck = False
	newparts = []
	for part in parts:
		newparts.append(anonWord(part, nameList, recheck=recheck))
	return joiner.join(newparts)



# Takes a line and spits out a dict of the nick, message, and whether or not it's a /me command
def cleanupline(linein, namelist, ignored_users=[], params={'bot':False,'debug':False}):
	# Skip Raribot commands
	if params['bot'] is True and '> ~' in linein:
		return None

	# Cleanup the line
	linein = linein.strip()
	linein = linein.strip('\n')
	if params['debug'] is True:
		print(('line: '+linein))
	isme = False

	# Process /me commands
	if linein[:2] == "* " and quitline(linein) is False:
		isme = True

		# This could go into another function elsewhere if the display of /me command lines is changed
		linein = linein[2:]
		linein = '<' + linein[:linein.index(' ')] + '> *' + linein[linein.index(' ')+1:] + '*'
		if params['debug'] is True:
			print(('new /me linein '+linein))

	# Throw out malformed lineins
	if linein.count('<')<1 or linein.count('>')<1:
		print("Found malformed line!")
		return None

	# Determine the nick
	name = findBetween(linein, '<', '>').lower()
	if name not in namelist:
		namelist.append(name)

	if name.lower() in ignored_users:
		print(("Skipping ignored user "+name))
		return None

	return {"name":name, "text":linein[linein.index('>')+2:], "meline":isme}



transform_D, undoTransform_D = genTransformDict()
