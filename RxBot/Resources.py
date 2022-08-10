from Settings import *
from Initialize import *
import pyautogui
import mss
import mss.tools
#import pytesseract
from PIL import Image, ImageOps
import cv2
import numpy
from xlutils.copy import copy
import xlrd
import re
import pygsheets
#pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
#pyautogui.FAILSAFE = False  # Might cause nuclear apocalypse

res = settings["RESOLUTION MODIFIER"] / 100

scrollToLineUpBottomDistance = -240
scrollToMoveUpOneBarDistance = -54
timesToScrollUp = 8
portraitOffset = -40

def cvToPil(cvImg):
    cvImg = cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB)
    pilImg = Image.fromarray(cvImg)
    del cvImg
    return pilImg


def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))
    def contrast(c):
        return 128 + factor * (c - 128)
    return img.point(contrast)


class resources:
    def __init__(self):
        self.width, self.height = pyautogui.size()
        self.userText = None
        self.IdText = None
        self.buyInText = None
        self.profitText = None
        self.cachedIdImage = None
        self.handsText = None
        self.lastLeaderboardHandCounts = []
        self.currentLeaderboardHandCounts = []
        self.wipeNextScan = False
        self.oldTempCache = []

    def holdKey(self, key, duration):
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)

    def findImageOnScreen(self, imgName, confidence):
        imageLocation = pyautogui.locateOnScreen("Resources/%s" % imgName, confidence=confidence)
        if not imageLocation:
            return False
        #print("Image found at " + str(imageLocation))
        return imageLocation

    def moveMouseToLocation(self, imageLocation):
        x, y = pyautogui.center(imageLocation)
        pyautogui.moveTo(x, y, 0.3)

    # def imgToText(self, img):
    #     text = pytesseract.image_to_string(img, config='--psm 10 --oem 3').replace("-", "")
    #     #print("OCR TEXT: \n" + text + "\n")
    #     return text.strip()

    def screenshotRegion(self, top, left, width, height, invert, filter):
        if settings["ALTERNATIVE SCREENSHOT"]:
            with mss.mss() as sct:
                # The screen part to capture
                region = {'top': top, 'left': left, 'width': width, 'height': height}

                # Grab the data
                sctimg = sct.grab(region)
                img = Image.frombytes("RGB", sctimg.size, sctimg.bgra, "raw", "BGRX")
        else:
            img = pyautogui.screenshot(region=(left, top, width, height))
        newImg = img

        # Upscale
        if filter:
            imgSize = img.size
            img = img.resize((imgSize[0] * 2, imgSize[1] * 2), resample=Image.BOX)

            newImg = img



        if invert:
            img = ImageOps.invert(img)

        if filter == "Normal":
            img = change_contrast(img, 142)

            cvImg = numpy.array(img)
            cvImg = cvImg[:, :, ::-1].copy()

            gray = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)
            revisedCvImg = cv2.fastNlMeansDenoising(gray, cvImg, 67.0, 7, 21)
            (thresh, blackAndWhiteImage) = cv2.threshold(revisedCvImg, (143 + settings["IMAGE OFFSET"]), 255, cv2.THRESH_BINARY)
            newImg = cvToPil(blackAndWhiteImage)

        if filter == "Hands":
            img = change_contrast(img, 142)

            cvImg = numpy.array(img)
            cvImg = cvImg[:, :, ::-1].copy()

            gray = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)
            revisedCvImg = cv2.fastNlMeansDenoising(gray, cvImg, 67.0, 7, 21)
            (thresh, blackAndWhiteImage) = cv2.threshold(revisedCvImg, (143 + settings["HANDS OFFSET"]), 255, cv2.THRESH_BINARY)
            newImg = cvToPil(blackAndWhiteImage)

        if filter == "ID":
            img = change_contrast(img, 40)

            cvImg = numpy.array(img)
            cvImg = cvImg[:, :, ::-1].copy()

            gray = cv2.cvtColor(cvImg, cv2.COLOR_BGR2GRAY)
            (thresh, blackAndWhiteImage) = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
            revisedCvImg = cv2.fastNlMeansDenoising(gray, blackAndWhiteImage, 35.0, 7, 5)
            (thresh, blackAndWhiteImage) = cv2.threshold(revisedCvImg, (220 + settings["ID IMAGE OFFSET"]), 255, cv2.THRESH_BINARY)
            newImg = cvToPil(blackAndWhiteImage)

        #newImg.show()



        # thresh = 170
        # fn = lambda x: 255 if x > thresh else 0
        # img = img.convert('L').point(fn, mode='1')


        if settings["DEBUG SHOW IMAGE"]:
            newImg.show()
            print("Showed image, waiting for it to be closed or moved.")
            time.sleep(1)

        #newImg.show()
        return newImg


    def scrollDown(self):
        pyautogui.moveTo(int(resources.width / 2), int(resources.height / 2), 0.3)
        pyautogui.drag(0, int(scrollToMoveUpOneBarDistance * res), 0.8, button="left")
        time.sleep(1.8)


    def scrollUp(self):
        pyautogui.moveTo(int(resources.width / 2), int(resources.height / 2), 0.3)
        pyautogui.drag(0, 400, 0.8, button="left")
        time.sleep(1)


    # def leaderboardOCRLookup(self, userImage, IdImage, buyinImage, profitImage, handsImage):
    #     self.userText = self.imgToText(userImage).strip()  # pretty much useless but grabbing anyway
    #
    #     self.IdText = self.imgToText(IdImage).strip()
    #
    #     self.buyInText = self.imgToText(buyinImage).strip()
    #     self.buyInText = ''.join(filter(str.isdigit, self.buyInText))
    #
    #     self.handsText = self.imgToText(handsImage).strip()
    #     self.handsText = ''.join(filter(str.isdigit, self.handsText))
    #
    #     self.profitText = self.imgToText(profitImage).strip()
    #     firstDigit = self.profitText[0]
    #     profitText = ''.join(filter(str.isdigit, self.profitText))
    #     if firstDigit != "+":
    #         firstDigit = "-"
    #     profitText = firstDigit + profitText


def resetStartAgain():
    if resources.findImageOnScreen("gem.png", 0.8):
        resources.moveMouseToLocation(resources.findImageOnScreen("gem.png", 0.8))
        pyautogui.click()
    elif resources.findImageOnScreen("darkGem.png", 0.8):
        resources.moveMouseToLocation(resources.findImageOnScreen("darkGem.png", 0.8))
        pyautogui.click()

    else:
        print("No game window detected")
        return
    pyautogui.keyDown("ctrl")
    pyautogui.keyDown("down")
    time.sleep(1)
    pyautogui.keyUp("ctrl")
    pyautogui.keyUp("down")
    time.sleep(0.5)
    pyautogui.keyDown("w")
    pyautogui.keyDown("a")
    time.sleep(0.5)
    pyautogui.keyUp("w")
    pyautogui.keyUp("a")


def startRequest():
    # Make sure the game didn't time out
    if resources.findImageOnScreen("reloadgame.png", 0.8):
        print("Game timed out, reloading")
        resources.moveMouseToLocation(resources.findImageOnScreen("reloadgame.png", 0.8))
        pyautogui.click()
        time.sleep(10)
        resetStartAgain()


    # Search for resources
    if resources.findImageOnScreen("gold.png", 0.7):
        print("Found gold, clicking!")
        resources.moveMouseToLocation(resources.findImageOnScreen("gold.png", 0.7))
        pyautogui.click()


    if resources.findImageOnScreen("elixir.png", 0.7):
        print("Found elixir, clicking!")
        resources.moveMouseToLocation(resources.findImageOnScreen("elixir.png", 0.7))
        pyautogui.click()


    # Check if the army is full
    if resources.findImageOnScreen("fightMenu.png", 0.7):
        resources.moveMouseToLocation(resources.findImageOnScreen("fightMenu.png", 0.7))
        pyautogui.click()
        time.sleep(0.3)
        resources.moveMouseToLocation(resources.findImageOnScreen("trainTroops.png", 0.7))
        pyautogui.click()
        time.sleep(0.3)

        if resources.findImageOnScreen("barbarian.png", 0.75):
            print("Training troops...")
            resources.moveMouseToLocation(resources.findImageOnScreen("barbarian.png", 0.75))
            pyautogui.move(0, 80)
            pyautogui.mouseDown()
            while resources.findImageOnScreen("barbarian.png", 0.75):
                time.sleep(0.2)
            pyautogui.mouseUp()
            print("Done")
        else:
            resetStartAgain()
            print("Nothing to do right now, waiting a minute then trying again...")
            time.sleep(60)
            return False

    else:
        resetStartAgain()




resources = resources()