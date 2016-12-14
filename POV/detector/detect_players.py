import sys
import cv2
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import matplotlib.pyplot as plt

import models

# Bigger value more feet detection with more false alarams
FEET_DETECTION_TOLERANCE = 3000

class DetectPlayers:
    def __init__(self, linesPosition, linesWidth, player1Color, player2Color, tolerance, lineBelongs, playersCount,
                 distanceBetweenDummys):
        self.linesPosition = linesPosition
        self.linesWidth = linesWidth
        self.player1Color = player1Color
        self.player2Color = player2Color
        self.tolerance = tolerance
        self.lineBelongs = lineBelongs
        self.playersCount = playersCount
        self.distanceBetweenDummys = distanceBetweenDummys
        self.dummyHeight = 40
        self.stripWidth = 75
        self.stripHeight = 10

    def detect(self, image):
        # return []  # TODO comment when needed!
        height, width, channels = image.shape
        return self.processLines(image, height)

    def processLines(self, image, height):
        dummys = []
        lineIndex = 0
        for linePos, belongs, playersCount in zip(self.linesPosition, self.lineBelongs, self.playersCount):
            sourceSegment = image[0:height, linePos - int(self.linesWidth / 2):linePos + int(self.linesWidth / 2)].copy()

            currentPlayerColor = self.player1Color if belongs == 1 else self.player2Color
            dummyIndexes = self.segmentLines(sourceSegment.copy(), 
                                             currentPlayerColor, 
                                             playersCount,
                                             True if lineIndex % 3 == 0 else False)
            dummyIndexes.sort()

            dummyStrips = []
            for index in dummyIndexes:
                cv2.rectangle(image, (linePos - self.stripWidth, index - self.stripHeight), (linePos + self.stripWidth, index + self.stripHeight), (255, 0, 0))

                if index - self.stripHeight < 0:
                    strip = image[0: self.stripHeight, linePos - self.stripWidth:linePos + self.stripWidth].copy()
                elif index + self.stripHeight >= height:
                    strip = image[height - self.stripHeight -1: height -1, linePos - self.stripWidth:linePos + self.stripWidth].copy()
                else:
                    strip = image[index - self.stripHeight: index + self.stripHeight, linePos - self.stripWidth:linePos + self.stripWidth].copy()


                dummyStrips.append(strip)
                cv2.circle(image, (linePos, index), 5, (255, 0, 0), 10)
            #cv2.imshow("test", image)
            #cv2.waitKey()

            #(width, center) = self.computeDummyWidth(dummyStrips, currentPlayerColor)
            (width, center) = self.computeDummyWidth(dummyStrips, currentPlayerColor)
            playerIndex = 1
            for index in dummyIndexes:
                dummys.append(models.Dummy((linePos, index), playerIndex, lineIndex, (linePos + center, index), belongs))
                cv2.rectangle(image, (linePos + center - int(width / 2), index - int(self.dummyHeight / 2)), (linePos + center + int(width / 2), index + int(self.dummyHeight / 2)), (255, 0, 0))
                playerIndex += 1


            lineIndex += 1

        return dummys

    def computeDummyWidth(self, strips, playerColor):
        colorValues = []
        i = 0
        for strip in strips:
            gray = cv2.cvtColor(strip,cv2.COLOR_RGB2GRAY)
            ret,gray = cv2.threshold(gray,142,255,0, cv2.THRESH_MASK)
            strips[i] = gray
            #cv2.imshow("wtf", gray)
            #cv2.waitKey()
            #strips[i] = cv2.cvtColor(strip, cv2.COLOR_RGB2HSV)
            i += 1

        playerColor = 255                         

        for i in range(self.stripWidth * 2):
            colorDiff = 0
            for j in range(self.stripHeight):
                for strip in strips:
                    colorDiff += abs(strip[j, i] - 255)
            colorValues.append(int(colorDiff))

        colorValues = gaussian_filter(colorValues, sigma=1)

        #colorValues = colorValues / np.max(colorValues)

        #plt.plot(range(0, len(colorValues)), colorValues)
        #plt.show()

        index = self.stripWidth
        i = 0
        for x in colorValues:
            # Magic constnat?  Yes, change it if detection of feet doesn't
            # work, but be carefoul it can damage your computer
            if x < FEET_DETECTION_TOLERANCE and abs(i - self.stripWidth) > abs(index - self.stripWidth):
                index = i
            i += 1

        return (self.linesWidth, index - self.stripWidth)

    def computeDummyWidth2(self, strips, playerColor):
        methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

        templates = []
        templates.append(cv2.imread('C:\\Users\\adamj\\Desktop\\templates\\red.PNG',0))
        templates.append(cv2.imread('C:\\Users\\adamj\\Desktop\\templates\\red1.PNG',0))
        templates.append(cv2.imread('C:\\Users\\adamj\\Desktop\\templates\\red3.PNG',0))
        templates.append(cv2.imread('C:\\Users\\adamj\\Desktop\\templates\\red4.PNG',0))
        templates.append(cv2.imread('C:\\Users\\adamj\\Desktop\\templates\\red5.PNG',0))

        kernel = np.ones((3,3),np.uint8)
        strip = cv2.cvtColor(strips[2],cv2.COLOR_RGB2GRAY)
        strip = cv2.Sobel(strip, cv2.CV_8U,1,0)
        #strip = cv2.morphologyEx(strip, cv2.MORPH_OPEN, kernel)
        #strip = strips[2]
        #cv2.imshow("test2", strip)
        #cv2.waitKey()
        index = 0
        max = 0
        max_index = -1
        for template in templates:
            w, h = template.shape[::-1]


            #template = cv2.cvtColor(template,cv2.COLOR_RGB2GRAY)
            template = cv2.Sobel(template, cv2.CV_8U,1,0)
            #template = cv2.morphologyEx(template, cv2.MORPH_OPEN, kernel)

            #cv2.imshow("test", template)
            #cv2.imshow("test2", strip)
            #cv2.waitKey()
            img = strip.copy()
            method = cv2.TM_CCORR_NORMED
            res = cv2.matchTemplate(img, template, method)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc

            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(img,top_left, bottom_right, 255, 2)
            plt.subplot(121),plt.imshow(res,cmap = 'gray')
            plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
            plt.subplot(122),plt.imshow(img,cmap = 'gray')
            plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
            #plt.suptitle(meth)
            #plt.show()

            if max_val > max:
                max = max_val
                max_index = index
            #print("Max: " + str(max_val))
            #print("Min: " + str(min_val))
            index += 1
        print("max index: " + str(max_index))
        if max_index == 0:
            return (self.linesWidth, 0)
        elif max_index == 1:
            return (self.linesWidth, self.stripWidth - 10)
        elif max_index == 2:
            return (self.linesWidth, -self.stripWidth + 10)
        elif max_index == 3:
            return (self.linesWidth, -self.stripWidth + 30)
        elif max_index == 4:
            return (self.linesWidth, self.stripWidth - 30)

        return None




    def segmentLines(self, image, color, playersCount, computeLastMiddlePlayer):
        rows = self.compueMeanSquareForEachRow(cv2.cvtColor(image, cv2.COLOR_RGB2HSV), color)

        rows = gaussian_filter(rows, sigma=11, mode='nearest')

        frameHeight = len(rows)
        #plt.plot(range(0, frameHeight), rows)
        #plt.show()

        rowIndexes = []

        distanceBetweenDummys = self.distanceBetweenDummys
        if computeLastMiddlePlayer:
            playersCount -= 1
            distanceBetweenDummys = distanceBetweenDummys * 2

        firstIndex = self.findNMinims(rows, playersCount, distanceBetweenDummys)
        for playerIndex in range(playersCount):
            index = firstIndex + playerIndex * distanceBetweenDummys
            rowIndexes.append(index)

        # try hill climbing for even better results
        i = 0
        for rowIndex in rowIndexes:
            rowIndexes[i] = self.hillClimbing(rowIndex, rows)
            i += 1

        if computeLastMiddlePlayer and len(rowIndexes) == 2:
            # if we got atleast 2 players and they are on the sides we can get
            # middle one
            # If distance between these 2 players is greater then distance
            # between dummys and magic constant so we can find middle one
            index = int((rowIndexes[0] + rowIndexes[1]) / 2)
            rowIndexes.append(index)

        return rowIndexes

    def hillClimbing(self, startingIndex, rows):
        currentIndex = startingIndex
        maxIndex = len(rows)
        while True:
            L = self.neighbors(currentIndex, maxIndex)
            nextEval = np.inf
            nextIndex = None
            for x in L: 
                if rows[x] < nextEval:
                    nextIndex = x
                    nextEval = rows[x]
            if nextEval >= rows[currentIndex]:
                #Return current node since no better neighbors exist
                return currentIndex
            currentIndex = nextIndex

    def neighbors(self, index, maxIndex):
        if index == 0:
            return [index + 1]
        elif index == maxIndex:
            return [index - 1]
        return [index + 1, index - 1]

    def findNMinims(self, rows, playersCount, distanceBetweenDummys):
        rowsCount = len(rows)
        lastMaxIndex = (playersCount - 1) * distanceBetweenDummys

        minIndex = -1
        minValue = sys.maxsize
        while lastMaxIndex < rowsCount:
            sum = 0
            for i in range(playersCount):
                sum += rows[lastMaxIndex - i * distanceBetweenDummys]
            if sum < minValue:
                minIndex = lastMaxIndex - (playersCount - 1) * distanceBetweenDummys
                minValue = sum
            lastMaxIndex += 1

        return minIndex

    def normalize(self, index, frameHeight):
        if index < 0:
            return 0
        if index >= frameHeight:
            return frameHeight
        return index

    def compueMeanSquareForEachRow(self, image, color):
        height, width, channels = image.shape

        rows = []
        for i in range(height):
            rowSum = 0
            for j in range(width):
                distance = abs(image[i, j] - color)
                value = (distance[0] + distance[1]) ** 2
                rowSum += value

            rowSum = rowSum / width
            rowSum = rowSum ** (1 / 2.0)

            rows.append(int(rowSum))

        return rows
