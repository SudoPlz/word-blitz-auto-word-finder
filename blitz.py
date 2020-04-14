import time


# importing screen screenshot mechanisms
import pyautogui
import pyautogui._pyautogui_osx as platformModule
from pytweening import *

# ocr
import pytesseract

import unicodedata as ud

# importing "copy" for copy operations 
import copy 
import sys
from multiprocessing.dummy import Pool
from functools import partial
from itertools import repeat
from pprint import pprint

import timeit

from threading import Lock, Thread
import re
import readline

screenResolution = pyautogui.size()
screenshotSizes = pyautogui.screenshot().size
lock = Lock()
DRAG_SPEED = 0.1
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/pytesseract'

print("@@@ Move mouse to the left side of the top left rectangle")
time.sleep(3) # Delay for 2 seconds.


mousePos = pyautogui.position()
startX = leftSideX = mousePos[0]
startY = mousePos[1]
print("@@@ Move mouse to the right side of the top left rectangle")
time.sleep(2) # Delay for 2 seconds.
mousePos = pyautogui.position()
rightSideX = mousePos[0]

programStartTimestamp = timeit.default_timer()

rectSize = rightSideX - leftSideX
marginSize = 0.110 * rectSize
padding = 0.255 * rectSize

screenshotSizeRendered = rectSize-(padding*2)
screenshotSizePrerendered = (screenshotSizeRendered / screenResolution[0])*screenshotSizes[0]



def getButtonCoordinates(row, column, extraPadding, usePreRenderedSizing=False):
	x = startX + (rectSize + marginSize) * column + extraPadding
	y = startY + (rectSize + marginSize) * row + extraPadding
	if(usePreRenderedSizing):
		x = (x / screenResolution[0])*screenshotSizes[0]
		y = (y / screenResolution[1])*screenshotSizes[1]
	return [x,y]

screenshotCoords = [
	getButtonCoordinates(0,0, padding, True),
	getButtonCoordinates(0,1, padding, True),
	getButtonCoordinates(0,2, padding, True),
	getButtonCoordinates(0,3, padding, True),

	getButtonCoordinates(1,0, padding, True),
	getButtonCoordinates(1,1, padding, True),
	getButtonCoordinates(1,2, padding, True),
	getButtonCoordinates(1,3, padding, True),

	getButtonCoordinates(2,0, padding, True),
	getButtonCoordinates(2,1, padding, True),
	getButtonCoordinates(2,2, padding, True),
	getButtonCoordinates(2,3, padding, True),

	getButtonCoordinates(3,0, padding, True),
	getButtonCoordinates(3,1, padding, True),
	getButtonCoordinates(3,2, padding, True),
	getButtonCoordinates(3,3, padding, True),
]
centerOfRectOffset = rectSize*0.5
mouseCoords = [
	[
		getButtonCoordinates(0,0, centerOfRectOffset),
		getButtonCoordinates(0,1, centerOfRectOffset),
		getButtonCoordinates(0,2, centerOfRectOffset),
		getButtonCoordinates(0,3, centerOfRectOffset), 
	],
	[
		getButtonCoordinates(1,0, centerOfRectOffset),
		getButtonCoordinates(1,1, centerOfRectOffset),
		getButtonCoordinates(1,2, centerOfRectOffset),
		getButtonCoordinates(1,3, centerOfRectOffset),
	],
	[
		getButtonCoordinates(2,0, centerOfRectOffset),
		getButtonCoordinates(2,1, centerOfRectOffset),
		getButtonCoordinates(2,2, centerOfRectOffset),
		getButtonCoordinates(2,3, centerOfRectOffset), 
	],
	[
		getButtonCoordinates(3,0, centerOfRectOffset),
		getButtonCoordinates(3,1, centerOfRectOffset),
		getButtonCoordinates(3,2, centerOfRectOffset),
		getButtonCoordinates(3,3, centerOfRectOffset), 
	],
]
print("@@@ Calculated positions")

characterInput = []
# print("@@@ Screenshot: "+str(screenshotCoords[3][0])+", "+str(screenshotCoords[3][1]))

# for row in range(0, 4):
# 	for column in range(0, 4):
# 		coords = getButtonCoordinates(row,column, padding+screenshotSizeRendered, False)
# 		pyautogui.moveTo(coords[0], coords[1], 0.3)
		

def dragMouse(x, y, button, duration):
	width, height = platformModule._size()
	startx, starty = platformModule._position()

	# None values means "use current position". Convert x and y to ints.
	x = startx if x is None else int(x)
	y = starty if y is None else int(y)

	# Make sure x and y are within the screen bounds.
	if x < 0:
		x = 0
	elif x >= width:
		x = width - 1
	if y < 0:
		y = 0
	elif y >= height:
		y = height - 1

	segments = max(width, height)
	timeSegment = float(duration) / segments
	while timeSegment < 0.05: # if timeSegment is too short, let's decrease the amount we divide it by. Otherwise the time.sleep() will be a no-op and the mouse cursor moves there instantly.
		segments = int(segments * 0.9) # decrease segments by 90%.
		timeSegment = float(duration) / segments

	for n in range(segments):
		time.sleep(timeSegment)
		pointOnLine = linear(float(n) / segments)
		tweenX, tweenY = getPointOnLine(startx, starty, x, y, pointOnLine)
		tweenX, tweenY = int(tweenX), int(tweenY)
		# only OS X needs the drag event specifically
		platformModule._dragTo(tweenX, tweenY, button)

	# Ensure that no matter what the tween function returns, the mouse ends up
	# at the final destination.
	platformModule._dragTo(x, y, button)



# Return the base character of char, by "removing" any diacritics like accents or curls and strokes and the like.
def normalizeChar(char):
	

	try:
		desc = ud.name(char)
	except:
		desc = char

	cutoff = desc.find(' WITH ')
	if cutoff != -1:
		desc = desc[:cutoff]
		try:
			char = ud.lookup(desc)
		except KeyError:
			pass  # removing "WITH ..." produced an invalid name

	re.sub('[^ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]+', '', char)

	if (len(char) > 1):
		char = char[0]

	return char

def dragWord(coordinates):
	# print("dragging coordinates: "+ str(coordinates))
	lock.acquire()
	startColumn = coordinates[0][0]
	startRow = coordinates[0][1]
	startCoordinates = mouseCoords[startRow][startColumn]
	pyautogui.moveTo(startCoordinates[0], startCoordinates[1])
	pyautogui.mouseDown(button='left', _pause=False)

	

	for i in range(0, len(coordinates)):
		if (i + 1 < len(coordinates)):
			nextCol = coordinates[i+1][0]
			nextRow = coordinates[i+1][1]
			# print("row: "+ str(nextRow)+", col: "+ str(nextCol))
			nextCoordinates = mouseCoords[nextRow][nextCol]
			# print("x: "+ str(nextCoordinates[0])+", y: "+ str(nextCoordinates[1]))
			dragMouse(nextCoordinates[0], nextCoordinates[1], 'left', DRAG_SPEED)
			# print("Mouse dragging from x: "+ str(nextCoordinates))
	pyautogui.mouseUp(button='left', _pause=False)
	lock.release()

def next_character(visited, current_row, current_column, dictionary):
	counter = 0
	if((len(visited) > 7) or ((current_column, current_row) in visited)):
		return counter
	word = ""
	visited.append((current_column, current_row))
	for letter in visited:
		word+=board[letter[1]][letter[0]]
	if(word.upper() in dictionary and len(word) > minWordLen):
		word_candidates.append({
			'word': word,
			'coordinates': visited
		})
		print(word + " in coordinates: ")
		dragWord(visited)
	prev_row = current_row - 1
	next_row = current_row + 1
	prev_column = current_column - 1
	next_column = current_column + 1
	# print(word)
	# Adds the charcter S the current pos
	if(len(board[current_row]) > next_row and ((next_row, current_column) not in visited)):
		counter += next_character(copy.deepcopy(visited), next_row, current_column, dictionary)
	#Adds the character SE the current pos
	if(len(board[current_row]) > next_row and len(board) > next_column) and ((next_row, next_column) not in visited):
		counter += next_character(copy.deepcopy(visited), next_row, next_column, dictionary)
	# Adds the charcter E of the current pos
	if(len(board) > next_column and ((current_row, next_column) not in visited)):
		counter += next_character(copy.deepcopy(visited), current_row, next_column, dictionary)
	#Adds the character NE the current pos
	if(len(board) > next_column and prev_row >= 0 and ((prev_row, next_column) not in visited)):
		counter += next_character(copy.deepcopy(visited), prev_row, next_column, dictionary)
	# Adds the charcter N the current pos
	if(prev_row >= 0 and ((current_row -1, current_column) not in visited)):
		counter += next_character(copy.deepcopy(visited), prev_row, current_column, dictionary)
	# Adds the charcter NW of the current pos
	if(prev_row >= 0 and prev_column >= 0 and ((prev_row, prev_column) not in visited)):
		counter += next_character(copy.deepcopy(visited), prev_row, prev_column, dictionary)
	# Adds the charcter W of the current pos
	if(prev_column >= 0 and ((current_row, prev_column) not in visited)):
		counter += next_character(copy.deepcopy(visited), current_row, prev_column, dictionary)
	# Adds the charcter SW of the current pos
	if(prev_column >= 0 and len(board[current_row]) > next_row and ((next_row, prev_column) not in visited)):
		counter += next_character(copy.deepcopy(visited), next_row, prev_column, dictionary)
	return counter

def create_board(input):
	arr = [
		[input[0], input[1], input[2], input[3]],
		[input[4], input[5], input[6], input[7]],
		[input[8], input[9], input[10], input[11]],
		[input[12], input[13], input[14], input[15]]
	]
	return arr

def printBoard():
	if (len(characterInput) >= 16):
		print(characterInput[0], characterInput[1], characterInput[2], characterInput[3])
		print(characterInput[4], characterInput[5], characterInput[6], characterInput[7])
		print(characterInput[8], characterInput[9], characterInput[10], characterInput[11])
		print(characterInput[12], characterInput[13], characterInput[14], characterInput[15])

def readBoard():
	it = 0
	for coord in screenshotCoords:
		xCoord = coord[0]
		yCoord = coord[1]
		fileName = 'screenshot' + str(it) + '.png'
		# print("x: " + str(xCoord) + ", y: " + str(yCoord) + fileName +" w/ screenshot size: "+str(screenshotSizePrerendered))

		# take screenshot
		tmpImage = pyautogui.screenshot(fileName, region=(xCoord,yCoord, screenshotSizePrerendered, screenshotSizePrerendered))

		# OCR
		recognizedChar = pytesseract.image_to_string(tmpImage, lang='grc', config=" --psm 10")
		# -c tessedit_char_whitelist=ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΥΦΧΨΩ

		tmpChar = normalizeChar(recognizedChar.upper())

		print("char: "+str(tmpChar))

		characterInput.append(tmpChar)

		it += 1
	# print(" list: " + str(characterInput))
	recognitionEndTimestamp = timeit.default_timer()
	print("Recognition finished in: " + str(recognitionEndTimestamp-programStartTimestamp) + " seconds")

def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result


# dragWord([(0, 1), (1, 2), (1, 1), (2, 0), (3, 1)])
# readBoard()

# Word finding
sys.setrecursionlimit(5000)
minWordLen = 3


f = open('Greek.txt', 'r')
# f = open('Eng.txt', 'r')
dictionary = set(f.read().splitlines())

printBoard()

prefilledInput = "".join(str(x) for x in characterInput)
if (len(prefilledInput) >= 16):
	prefilledInput = prefilledInput[0]+prefilledInput[1]+prefilledInput[2]+prefilledInput[3]+"\n"+prefilledInput[4]+prefilledInput[5]+prefilledInput[6]+prefilledInput[7]+"\n"+prefilledInput[8]+prefilledInput[9]+prefilledInput[10]+prefilledInput[11]+"\n"+prefilledInput[12]+prefilledInput[13]+prefilledInput[14]+prefilledInput[15]+"\n"

typedInput = input_with_prefill("Enter the letters (example: qwertyuyasdgwadf)\n", prefilledInput)
characterInput = list(typedInput.replace(" ", "").replace("\\n", ""))

board = create_board(characterInput)
word_candidates = []
iterator = []
for row in range(0, 4):
	for column in range(0, 4):
		iterator.append(([], row, column, dictionary))
results = []
with Pool(4) as pool:
	results = pool.starmap(next_character, iterator)
# word_candidates.sort(key=len, reverse=False)
wordFindEndTimestamp = timeit.default_timer()
print("Finding words finished in: " + str(wordFindEndTimestamp-programStartTimestamp) + " seconds")
# print(sum(results))

# for curWord in word_candidates:
# 	word = curWord['word']
# 	coordinates = curWord['coordinates']
# 	pprint(word + " IN coordinates: "+ str(coordinates))
	
pprint(word_candidates)
programEndTimestamp = timeit.default_timer()
print("Finished in: " + str(programEndTimestamp-programStartTimestamp) + " seconds")