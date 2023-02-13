import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm

##########
brushThickness = 15
eraserThickness = 50

folderPath = "header"
myList = os.listdir(folderPath)  #creates a list of all items names in header folder

overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)  #list of all images in folder header

header = overlayList[0]
drawColor = (182, 42, 128)


cap = cv2.VideoCapture(0)  #to set up webcam
cap.set(3,1280)
cap.set(4,720)

detector = htm.handDetector(detectionCon=0.85)
xp, yp = 0,0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)


while True:

    # 1. importing image
    success, img = cap.read()
    img = cv2.flip(img, 1)    #flips image

    # 2. find hand landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList)!=0:

        #print(lmList)

        #tip of index and middle finger
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3. check which fingers are up

        fingers = detector.fingersUp()
        #print(fingers)

        # 4. if selection mode (2 fingers are up) 

        if fingers[1] and fingers[2]:
            xp, yp = 0, 0 #whenevr start drawing again or there is a selection, set it back to zero or else line will begin from where it last ended
            print("Selection Mode")
            #checking for click
            if y1 < 125:
                if 538<x1<690:
                    header = overlayList[0]
                    drawColor =  (182, 42, 128)
                elif 720<x1<860:
                    header = overlayList[1]
                    drawColor =  (94, 23, 235)
                elif 880<x1<1020:
                    header = overlayList[2]
                    drawColor =  (0, 128, 55)
                elif 1050<x1<1200:
                    header = overlayList[3]
                    drawColor =  (0, 0, 0)
            cv2.rectangle(img, (x1, y1-15), (x2, y2+15), drawColor, cv2.FILLED)


        # 5. if draw mode (index finger is up)

        if fingers[1] and fingers[2]==False:
            cv2.circle(img, (x1,y1), 15, drawColor, cv2.FILLED)
            print("Drawing Mode")
            if xp==0 and yp==0:  #if this line isnt there, the line initially will join from posn 0,0 to current position
                xp, yp = x1, y1  #initially, it is set to current position

            if drawColor ==(0,0,0):
                cv2.line(img, (xp, yp), (x1, y1), drawColor, eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, eraserThickness)  #increase thickness of eraser
            else:
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness) #this draws on the img being captured hence removes the drawing after every iteration
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)  #draw a line joining previous posn of finger and current posn
                    #upper line is used to draw the image and save it on a blank canvas so that it isnt removed after each iteration
            xp, yp = x1, y1  #it is iterated to previous position everytime current position changes

        #bsasically how the eraser works is, the canva is a blank black screen, hence using black color for eraser will make it look like the colored part is erased

    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)  
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)    #converts all the drawn region into black
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR) #convert to image inverse #conerting it bad to be able to add in colored image, gray and color cant be added
    img = cv2.bitwise_and(img, imgInv)   #adding the image inverse and the image, black region wherever u draw
    img = cv2.bitwise_or(img, imgCanvas)  #so add colored part of canva image with or operation on actual screen to give final image

    # setting header image
    img[0:125, 0:1280] = header
    #img = cv2.addWeighted(img, 0.5, imgCanvas, 0.5, 0)  #morphs the two screen images onto img  with each having opacity 0.5
    cv2.imshow('Image', img)
    cv2.imshow('Canvas', imgCanvas)
    cv2.waitKey(1)
    