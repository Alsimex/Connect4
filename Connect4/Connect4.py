########
# Student name: Dayton McManus
# Course: COSC 3143 - Pi & Python
# Assignment: Final Project
# Filename: Connect4.py
#
# Purpose: A playable game of Connect 4 using GPIO buttons for input
#
# Input: Three GPIO buttons for right, left, and select
#
# Output: A GUI display and an RGB LED for the player turn
#
# Assumptions: The circuit must be wired according to the schematics
#
# Limitations: Red will go first when first starting the game and the
#                   losing player will go first when playing again
#
# Operational Status: functional
#######

# import statements
import tkinter as Tk
from tkinter import messagebox
from array import *
import os
from os import path
import atexit
import time
import RPi.GPIO as GPIO
from multiprocessing import Process, Value

# pin values
redPin = 11
greenPin = 13
bluePin = 15

leftButton = 12
rightButton = 16
selButton = 18

pinOn = GPIO.HIGH
pinOff = GPIO.LOW

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(redPin,GPIO.OUT)
GPIO.setup(greenPin,GPIO.OUT)
GPIO.setup(bluePin,GPIO.OUT)
GPIO.setup(leftButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(rightButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(selButton,GPIO.IN,pull_up_down=GPIO.PUD_UP)

freq = 100

# setup PWM objects
redPWM = GPIO.PWM(redPin, freq)
greenPWM = GPIO.PWM(greenPin, freq)
bluePWM = GPIO.PWM(bluePin, freq)

# create 2d array for the board that is 7 wide and 6 tall
boardX = 7
boardY = 6
boardArray = [[0 for y in range(boardY)] for x in range(boardX)]

linesToWin = 4  # number of pieces in one line needed to win

# start of GUI
root = Tk.Tk()
root.title("Connect 4")

playerTurn = Tk.IntVar(root, 1)  # current player's turn; 1 = red, 2 = yellow
lightColor = Value('i', 1)       # color of the LED, same as playerTurn

# arrays for the GUI
boardGUI = [[None for y in range(boardY)] for x in range(boardX)]
cursorGUI = [None for x in range(boardX)]

# bindings for sprites
__location__ = path.realpath(path.join(os.getcwd(), path.dirname(__file__)))    # filepath for current directory
spriteSize = 96     # size of each sprite

titleImage = Tk.PhotoImage(file=os.path.join(__location__, "Sprites/C4-Title.png"))     # title

frameCnt = 10       # number of frames in cursor gif
cursorFrames = [Tk.PhotoImage(file=os.path.join(__location__,"Sprites/C4-Cursor.gif"),
                              format = 'gif -index %i' %(i)) for i in range(frameCnt)]  # cursor array
cursorFrame = cursorFrames[0]       # current frame in cursor gif
blankCursorImage = Tk.PhotoImage(file=os.path.join(__location__, "Sprites/C4-BlankCursor.png")) # image for space without cursor

redImage = Tk.PhotoImage(file=os.path.join(__location__, "Sprites/C4-Red.png"))         # red piece
yellowImage = Tk.PhotoImage(file=os.path.join(__location__, "Sprites/C4-Yellow.png"))   # yellow piece
emptyImage = Tk.PhotoImage(file=os.path.join(__location__, "Sprites/C4-Empty.png"))     # no piece
boardImages = [emptyImage,redImage,yellowImage]                                         # every piece

ready = 1   # whether the game is ready for input

# position of the cursor
cursorPos = Tk.IntVar()
cursorPos.set(3)

########################################
def turnAllOff():
    GPIO.output(redPin,pinOff)
    GPIO.output(greenPin,pinOff)
    GPIO.output(bluePin,pinOff)
########################################

########################################
def quitter():
    turnAllOff()
    GPIO.cleanup()
########################################

########################################
def resetBoard():
    for x in range(boardX):
        for y in range(boardY):
            if boardArray[x][y].get() > 0:
                boardArray[x][y].set(0)
            boardGUI[x][y].configure(image=boardImages[0])
########################################

########################################
def playerWin(playerTurn):
    lightColor.value = 0
    
    line = "~~~~~~~~~~~~~~~"
    replay = "Play Again?"
    if playerTurn == 1:
        winner = "Red Player Wins!"
    elif playerTurn == 2:
        winner = "Yellow Player Wins!"
    else:
        winner = "No Player Wins!"
    if messagebox.askyesno("GAME OVER",line + "\n" + winner + "\n\n" + replay):
        resetBoard()
    else:
        root.withdraw()
        exit()
########################################

########################################
def checkLine(x, y, xInc, yInc, playerTurn):
    if x >= boardX or x < 0 or y >= boardY or y < 0:
        return 0
    elif boardArray[x][y].get() == playerTurn:
        x += xInc
        y += yInc
        return checkLine(x, y, xInc, yInc, playerTurn) + 1
    return 0
########################################

########################################
def checkWin(x, y, turn):
    global linesToWin
    win = False
    lines = checkLine(x, y, 1, 0, turn) + checkLine(x, y, -1, 0, turn) - 1 # left and right
    if lines >= linesToWin:
        win = True
    lines = checkLine(x, y, 0, 1, turn) # down
    if lines >= linesToWin:
        win = True
    lines = checkLine(x, y, 1, 1, turn) + checkLine(x, y, -1, -1, turn) - 1 # downleft and upright
    if lines >= linesToWin:
        win = True
    lines = checkLine(x, y, 1, -1, turn) + checkLine(x, y, -1, 1, turn) - 1 # upleft and downright
    if lines >= linesToWin:
        win = True
    return win
########################################

########################################
def boardFull():
    full = True
    for x in range(boardX):
        if boardArray[x][0].get() == 0:
            full = False
            break
    return full
########################################

########################################
def animateCursor(ind):
    global cursorFrame 
    cursorFrame = cursorFrames[ind]
    ind += 1
    if ind == frameCnt:
        ind = 0
    cursorGUI[cursorPos.get()].configure(image=cursorFrame)
    root.after(83, animateCursor, ind)
########################################

########################################
def updateCursor(x):
    oldX = cursorPos.get()
    
    cursorGUI[oldX].configure(image=blankCursorImage)
    
    if x < 0:
        x = boardX - 1
    elif x >= boardX:
        x = 0
    cursorPos.set(x)
    
    cursorGUI[x].configure(image=cursorFrame)
########################################

########################################
def cursorLeft(x):
    updateCursor(cursorPos.get()-1)
########################################

########################################
def cursorRight(x):
    updateCursor(cursorPos.get()+1)
########################################
    
########################################
def animatePiece(x, y, endY, turn):
    global ready
    if y == 0:
        boardGUI[x][y].configure(image=boardImages[turn])
    else:
        boardGUI[x][y-1].configure(image=boardImages[0])
        boardGUI[x][y].configure(image=boardImages[turn])
    if y == endY:
        ready = 1
        return None

    y += 1
    root.after(83, animatePiece, x, y, endY, turn)
########################################

########################################
def calcTurn(x):
    global ready
    
    # check if column is full
    y = -1
    for i in range(boardY):
        if boardArray[x][i].get() == 0:
            y = i
    if y == -1:
        ready = 1
        return None

    turn = playerTurn.get()
    boardArray[x][y].set(turn)

    animatePiece(x, 0, y, turn)

    # check if the player has won
    # otherwise check if the board is full
    if checkWin(x, y, turn) == True:
        playerWin(turn)
    elif boardFull() == True :
        playerWin(0)
    
    # change which player's turn it is
    if turn == 1:
        playerTurn.set(2)
    else:
        playerTurn.set(1)
        
    lightColor.value = playerTurn.get()
########################################

########################################
def select(x):
    global ready
    if ready == 1:
        ready = 0
        calcTurn(cursorPos.get())
########################################

########################################
def click(x):
    global ready
    if ready == 1:
        ready = 0
        updateCursor(x)
        calcTurn(x)
########################################
        
# title
title = Tk.Label(root, image=titleImage, borderwidth=0, width=spriteSize*7, height=spriteSize)
title.grid(row=0,column=0,columnspan=7)

# set up the initial GUI
for x in range(boardX):
    for y in range(boardY):
        boardArray[x][y] = Tk.IntVar()
        boardGUI[x][y] = Tk.Label(root, image=boardImages[0], borderwidth=0, width=spriteSize, height=spriteSize)
        boardGUI[x][y].grid(row=y+2,column=x)
        boardGUI[x][y].bind("<Button-1>", lambda e, x=x: click(x))
    cursorGUI[x] = Tk.Label(root, image=blankCursorImage, borderwidth=0, width=spriteSize, height=spriteSize)
    cursorGUI[x].grid(row=1,column=x)
    cursorGUI[x].bind("<Button-1>", lambda e, x=x: click(x))

# animate the cursor
root.after(0, animateCursor, 0)

# create button events
GPIO.add_event_detect(leftButton, GPIO.RISING, callback=cursorLeft, bouncetime = 300)
GPIO.add_event_detect(rightButton, GPIO.RISING, callback=cursorRight, bouncetime = 300)
GPIO.add_event_detect(selButton, GPIO.RISING, callback=select, bouncetime = 500)

########################################
def lightsProcess(lightColor):
    redPWM.start(0)
    greenPWM.start(0)
    bluePWM.start(0)
    while True:
        for i in range(0,101):
            if lightColor.value == 1:    # red
                redPWM.ChangeDutyCycle((i))
                greenPWM.ChangeDutyCycle(0)
                bluePWM.ChangeDutyCycle(0)
            elif lightColor.value == 2:  # yellow
                redPWM.ChangeDutyCycle((i))
                greenPWM.ChangeDutyCycle((i))
                bluePWM.ChangeDutyCycle(0)
            else:                        # win
                redPWM.ChangeDutyCycle((i))
                greenPWM.ChangeDutyCycle(100-(i))
                bluePWM.ChangeDutyCycle(100)
            time.sleep(0.005)
        for i in range(0,101):
            if lightColor.value == 1:    # red
                redPWM.ChangeDutyCycle(100-(i))
                greenPWM.ChangeDutyCycle(0)
                bluePWM.ChangeDutyCycle(0)
            elif lightColor.value == 2:  # yellow
                redPWM.ChangeDutyCycle(100-(i))
                greenPWM.ChangeDutyCycle(100-(i))
                bluePWM.ChangeDutyCycle(0)
            else:                        # win
                redPWM.ChangeDutyCycle(100-(i))
                greenPWM.ChangeDutyCycle((i))
                bluePWM.ChangeDutyCycle(100)
            time.sleep(0.005)
########################################

########################################
def main():
    atexit.register(quitter)

    turnAllOff()
    
    lights = Process(target=lightsProcess, args=(lightColor,))
    lights.daemon = True
    lights.start()
    
    root.mainloop()
    exit()
########################################

if __name__ == "__main__":
    main()