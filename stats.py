#!/usr/bin/env python3

# change these if you want
sampleCount = 10000
histogramWidth = 220
histogramHeight = 30
numLabels = 6
rowLabelSpacing = 3
minTitleSpacing = 3

BOX_VERT = u"\u2551"
BOX_HORIZ = u"\u2550"
BOX_ORIGIN = u"\u255A"
BOX_TITLE_TICK = u"\u2567"
BOX_FINAL_TITLE_TICK = u"\u255B"
BLOCK = u"\u2588"

import math

def _sampleGen(fn):
  return [fn() for x in range(sampleCount)]

def average(data):
  if hasattr(data, '__call__'):
    data = _sampleGen(data)
  return sum(data) / len(data)

def standardDeviation(data):
  if hasattr(data, '__call__'):
    data = _sampleGen(data)
  avg = average(data)
  variance = sum((avg - x) ** 2 for x in data) / len(data)
  return math.sqrt(variance)

class _Column(object):
  def __init__(self, width, height, title):
    self.width = width
    self.height = height
    self.title = title

def _continuousColumns(smallest, largest, collection):
  lowerBound = smallest
  for i in range(histogramWidth):
    delta = (largest - smallest)
    upperBound = smallest + delta * (i + 1) / histogramWidth
    sample = list(x for x in collection if (((lowerBound <= x) if (i == 0) else (lowerBound < x)) and x <= upperBound))
    title = "%.2E" % ((lowerBound + upperBound) / 2)
    yield _Column(1, len(sample), title)
    lowerBound = upperBound

def _smallestDelta(sortedValues):
  smallestDelta = float("inf")
  for i in range(len(sortedValues) - 1):
    smallestDelta = min(smallestDelta, sortedValues[i+1] - sortedValues[i])
  return smallestDelta

def _canFillIn(values, maxColumns):
  representedValues = sorted(values.keys())
  smallestDelta = _smallestDelta(representedValues)
  for i in range(1, len(representedValues)):
    delta = representedValues[i] - representedValues[0]
    if abs(delta % smallestDelta) > 1e5 or (delta / smallestDelta) > maxColumns:
      return False
  return True

def _discreetColumns(values):
  representedValues = sorted(values.keys())
  smallestDelta = _smallestDelta(representedValues)
  numColumns = int(round((representedValues[-1] - representedValues[0]) / smallestDelta))
  width = int(histogramWidth / numColumns)
  smallest = representedValues[0]
  for i in range(numColumns):
    value = smallest + i * smallestDelta
    validKeys = list(filter(lambda x: abs(value - x) < smallestDelta / 2, representedValues))
    title = "%.2E" % value
    if len(validKeys) == 0:
      yield _Column(width, 0, title)
    elif len(validKeys) == 1:
      yield _Column(width, values[validKeys[0]], title)
    else:
      raise "Huh"

def _columns(collection, maxColumns):
  i = 0
  seenValues = dict()
  smallest = float("inf")
  largest = -float("inf")
  while i < len(collection):
    if len(seenValues) <= maxColumns:
      seenValues[collection[i]] = seenValues.get(collection[i], 0) + 1
    smallest = min(smallest, collection[i])
    largest = max(largest, collection[i])
    i += 1

  if len(seenValues) > maxColumns:
    return _continuousColumns(smallest, largest, collection)
  return _discreetColumns(seenValues)

def printHistogram(data, title):
  if hasattr(data, '__call__'):
    data = _sampleGen(data)
  title = "Histogram of " + title
  title = title[:histogramWidth]
  headlineSpace = int((histogramWidth - len(title) + 10) / 2)
  print(" " * headlineSpace + title)

  columns = list(_columns(data, histogramWidth))
  columnHeights = list(map(lambda x: x.height, columns))
  lowest = min(columnHeights)
  highest = max(columnHeights)
  delta = (highest - lowest) / histogramHeight
  for row in range(histogramHeight):
    lineContents = ""
    curHeight = highest - delta * (row + row / histogramHeight)
    if row == histogramHeight - 1:
      lineContents += "%.2E %s" % (lowest, BOX_VERT)
      curHeight = lowest
    elif row % rowLabelSpacing == 0:
      lineContents += "%.2E %s" % (curHeight, BOX_VERT)
    else:
      lineContents += " " * 9 + BOX_VERT

    for column in columns:
      for character in range(column.width):
        lineContents += BLOCK if column.height >= curHeight else " "
    print(lineContents)

  titlesLine = ""
  axisLine = ""
  characterDebt = 0
  finalTitleLen = len(columns[-1].title) + 1
  for column in columns:
    firstHalf = math.floor(column.width / 2)
    secondHalf = int(column.width - firstHalf) - 1

    characterDebt -= firstHalf
    axisLine += BOX_HORIZ * firstHalf

    titleLen = len(column.title)
    padding = 0 if (characterDebt + titleLen >= 0) else (-titleLen - characterDebt)
    fullLen = padding + titleLen + minTitleSpacing
    if characterDebt <= 0 and (len(titlesLine) + fullLen < histogramWidth - finalTitleLen or column == columns[-1]):
      titlesLine += " " * padding + column.title + " " * minTitleSpacing
      axisLine += BOX_TITLE_TICK
      characterDebt += fullLen - 1
    else :
      characterDebt -= 1
      axisLine += BOX_HORIZ

    characterDebt -= secondHalf
    axisLine += BOX_HORIZ * secondHalf

  titlesLine = " " * 10 + titlesLine
  axisLine = " " * 9 + BOX_ORIGIN + axisLine
  print(axisLine)
  print(titlesLine)

  stdStatement = "Standard Deviation: %.2E" % standardDeviation(data)
  averageStatement = "Average: %.2E" % average(data)
  padding = int((histogramWidth + 10 - len(stdStatement) - len(averageStatement)) / 3)
  print(" " * padding + averageStatement + " " * padding + stdStatement)

import random
def testSample():
  return random.randint(1, 10)

def bellCurve():
  return random.normalvariate(0, 1)

def dice():
  acc = 0
  for i in range(100):
    acc += random.randint(1, 6)
  return acc

def test():
  print("Average (1-10): %.2f" % average(testSample))
  print("Standard Deviation (1-10): %.2f" % standardDeviation(testSample))
  sampleCount = 1
  print("Standard Deviation (single sample): %.2f" % standardDeviation(testSample))
  sampleCount = 10000
  printHistogram(testSample, "1-10")
  print("")
  printHistogram(bellCurve, "Bell Curve")
  print("")
  printHistogram(dice, "100d6")

if __name__ == '__main__':
  test()
