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
from multiprocessing import Process, Value
#import RPi.GPIO as GPIO

# create 2d array for the board that is 7 wide and 6 tall
boardX = 7
boardY = 6
boardArray = [[0 for y in range(boardY)] for x in range(boardX)]

linesToWin = 4  # number of pieces in one line needed to win

# start of GUI
root = Tk.Tk()
root.title("Connect 4")

playerTurn = Tk.IntVar(root, 1)  # current player's turn; 1 = red, 2 = yellow
lightColor = Value('i', 1)   # color of the LED, same as playerTurn

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
def quitter():
    #turnAllOff()
    #GPIO.cleanup()
    print("program has closed")
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
def playerWin(turn):
    lightColor.value = 0

    replay = "Play Again?"
    if turn == 1:
        winner = "Red Wins!"
    elif turn == 2:
        winner = "Yellow Wins!"
    else:
        winner = "No one wins!"
    if messagebox.askyesno("GAME OVER", winner + "\n" + replay):
        resetBoard()
    else:
        root.withdraw()
        exit()
########################################

########################################
def checkLine(x, y, xInc, yInc, turn):
    if x >= boardX or x < 0 or y >= boardY or y < 0:
        return 0
    elif boardArray[x][y].get() == turn:
        x += xInc
        y += yInc
        return checkLine(x, y, xInc, yInc, turn) + 1
    return 0
########################################

########################################
def checkWin(x, y, turn):
    global linesToWin
    win = checkLine(x, y, 1, 0, turn) + checkLine(x, y, -1, 0, turn) - 1 # left and right
    if win >= linesToWin:
        return True
    win = checkLine(x, y, 0, 1, turn) # down
    if win >= linesToWin:
        return True
    win = checkLine(x, y, 1, 1, turn) + checkLine(x, y, -1, -1, turn) - 1 # downleft and upright
    if win >= linesToWin:
        return True
    win = checkLine(x, y, 1, -1, turn) + checkLine(x, y, -1, 1, turn) - 1 # upleft and downright
    if win >= linesToWin:
        return True
########################################

########################################
def boardFull():
    full = True
    for x in range(boardX):
        if boardArray[x][0].get() == 0:
            full = False
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
    
    cursorPos.set(x)
    
    cursorGUI[x].configure(image=cursorFrame)
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
    y = -1
    for i in range(boardY):
        if boardArray[x][i].get() == 0:
            y = i
    if y == -1:
        ready = 1
        return None
    
    boardArray[x][y].set(playerTurn.get())

    animatePiece(x, 0, y, playerTurn.get())

    # check if the player has won otherwise check if the board is full
    if checkWin(x, y, playerTurn.get()) == True:
        playerWin(playerTurn.get())
    elif boardFull() == True :
        playerWin(0)
    
    # change which player's turn it is
    if playerTurn.get() == 1:
        playerTurn.set(2)
    else:
        playerTurn.set(1)
    
    lightColor.value = playerTurn.get()
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

# set up board GUI
for x in range(boardX):
    for y in range(boardY):
        boardArray[x][y] = Tk.IntVar()
        boardGUI[x][y] = Tk.Label(root, image=boardImages[0], borderwidth=0, width=spriteSize, height=spriteSize)
        boardGUI[x][y].grid(row=y+2,column=x)
        boardGUI[x][y].bind("<Button-1>", lambda e, x=x: click(x))
    cursorGUI[x] = Tk.Label(root, image=blankCursorImage, borderwidth=0, width=spriteSize, height=spriteSize)
    cursorGUI[x].grid(row=1,column=x)
    cursorGUI[x].bind("<Button-1>", lambda e, x=x: click(x))

root.after(0, animateCursor, 0)

########################################
def lightsProcess(lightColor):
    while True:
        for i in range(0,101):
            #print(i)
            #print(lightColor.value)
            if lightColor.value == 1:
                print("red")
            elif lightColor.value == 2:
                print("yellow")
            else:
                print("GAME OVER")
            time.sleep(0.05)
        for i in range(0,101):
            #print(100-i)
            #print(lightColor.value)
            if lightColor.value == 1:
                print("red")
            elif lightColor.value == 2:
                print("yellow")
            else:
                print("GAME OVER")
            time.sleep(0.05)
########################################

########################################
def main():
    atexit.register(quitter)

    lights = Process(target=lightsProcess, args=(lightColor,))
    lights.daemon = True
    lights.start()

    root.mainloop()
########################################

if __name__ == "__main__":
    main()