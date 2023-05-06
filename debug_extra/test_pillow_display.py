#! /usr/bin/python

import time
from PIL import Image, ImageDraw, ImageFont


diwidth = 160  # we swap height/width to rotate it to landscape!
diheight = 128

#The screen will continue to display the last image sent to it, until it recieves something new
#according to this: https://arduino.stackexchange.com/questions/74624/slow-refresh-rate-of-1-8-tft-display
#The max frame rate is theoretically around 24 fps
#from my testing we can get like 29 fps at max speed

# class piDisplay:
#     def __init__(self):
#         self.input = ""



def gForceMeter(accVector,width=diwidth,height=diheight,circles=[120,80,40],axes=True,linewidth=2,backColor='#fcd8ac'):
    #circles = [] list of diameter of each circle to be drawn
    fillColor = '#ffffff'
    outlineColor = '#000000'
    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, height), fill=backColor)
    # Draw a green filled box as the background

    #disp.image(image)
  
    #its pretty self explanatory what these do just by the names
    for diam in circles:
        draw.ellipse([(width/2-diam/2,height/2-diam/2),(width/2+diam/2,height/2+diam/2)],width = linewidth, outline = outlineColor)

    if axes:
        draw.line([(width/2,0),(width/2,height)],width = linewidth, fill = outlineColor)
        draw.line([(0,height/2),(width,height/2)],width = linewidth, fill = outlineColor)
    
    # Display image.
    
    image.show()
    print('displayed image') #DEBUG


def dispBackground(backColor=[0,0,255],width=diwidth,height=diheight):
    startTime = time.time()
    # First define some constants to allow easy resizing of shapes.
    #BORDER = 20
    #FONTSIZE = 20

    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a green filled box as the background
    draw.rectangle((0, 0, width, height), fill=(backColor[2],backColor[1],backColor[0]))
    #disp.image(image)
  
    
    # Display image.
    
    print("Elapsed time:",str(time.time()-startTime))
 

dispBackground()
gForceMeter(1)