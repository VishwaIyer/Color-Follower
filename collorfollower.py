import cv2 
import numpy as np
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(29,GPIO.OUT) #ENA
GPIO.setup(31,GPIO.OUT) #IN1
GPIO.setup(33,GPIO.OUT) #IN2
GPIO.setup(35,GPIO.OUT) #IN3
GPIO.setup(37,GPIO.OUT) #IN4
GPIO.setup(40,GPIO.OUT) #ENB

GPIO.output(29,GPIO.HIGH)
GPIO.output(40,GPIO.HIGH)

def forward():
    GPIO.output(31,GPIO.HIGH)
    GPIO.output(33,GPIO.LOW)
    GPIO.output(35,GPIO.LOW)
    GPIO.output(37,GPIO.HIGH)
def backward():
    GPIO.output(31,GPIO.LOW)
    GPIO.output(33,GPIO.HIGH)
    GPIO.output(35,GPIO.HIGH)
    GPIO.output(37,GPIO.LOW)
def right():
    GPIO.output(31,GPIO.LOW)
    GPIO.output(33,GPIO.LOW)
    GPIO.output(35,GPIO.LOW)
    GPIO.output(37,GPIO.HIGH)
def left():
    GPIO.output(31,GPIO.HIGH)
    GPIO.output(33,GPIO.LOW)
    GPIO.output(35,GPIO.LOW)
    GPIO.output(37,GPIO.LOW)
def stop():
    GPIO.output(31,GPIO.LOW)
    GPIO.output(33,GPIO.LOW)
    GPIO.output(35,GPIO.LOW)
    GPIO.output(37,GPIO.LOW)

cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    #Noise filtering
    blur_frame = cv2.GaussianBlur(frame, (5,5) , 0)
    
    #RGB to HSV color Conversion
    hsv = cv2.cvtColor(blur_frame,cv2.COLOR_BGR2HSV)
    
    #setting the upper and lower values
    lower_red = np.array([0,50,50]) 
    upper_red = np.array([10,255,255])
    
    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    #filtering the background noise using Morphological Transformations
    kernel = np.ones((5,5), np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    #find the contours in the opening mask
    _,contours,_ = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours)>0:
        areas = [cv2.contourArea(c) for c in contours] #find the areas of each contour in the opening mask
        max_index = np.argmax(areas)                    #get the max area of contours found
        cnt=contours[max_index]
        
        #bounding the max. contour with a rectgular shape
        x,y,w,h = cv2.boundingRect(cnt)                 
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        center = int(x+(w/2))
        area_mContour = w*h
    
        if (area_mContour > 15000) and (area_mContour < 20000):
            stop()
            print('stop')
            sleep(0.01)
        elif area_mContour > 20000:
            backword()
            print('backward')
        else:
            if center < 220:
                left()
                print('left')
            elif center > 440:
                right()
                print('right')
            elif center > 220 and center < 440:
                forword()
                print('straight')
            else :
                stop()
                print ('stop')
                sleep(0.01)
    else :
        stop()
        print('stop, no contours is found')
    
    
    cv2.imshow('frame', frame)
    
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break
    
cv2.destoryAllWindows()
cap.release()
