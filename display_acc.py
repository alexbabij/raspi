#! /usr/bin/python
import digitalio
import board
import time
from PIL import Image, ImageDraw, ImageFont

from adafruit_rgb_display import st7735  # pylint: disable=unused-import

# Configuration for CS and DC pins (these are PiTFT defaults):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
bl_pin = digitalio.DigitalInOut(board.D23)

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()


disp = st7735.ST7735S(spi, rotation=0, cs=cs_pin, bl=bl_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE, width=160,height=128,x_offset=0,y_offset=0) 
#Yes I changed to the actually correct display which fixes the issue of the rgb color values being swapped because the bits in the register are set differently
#no I will not be going back to fix the old one
# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    diheight = disp.width  # we swap height/width to rotate it to landscape!
    diwidth = disp.height
else:
    diwidth = disp.width  # we swap height/width to rotate it to landscape!
    diheight = disp.height

#The screen will continue to display the last image sent to it, until it recieves something new
#according to this: https://arduino.stackexchange.com/questions/74624/slow-refresh-rate-of-1-8-tft-display
#The max frame rate is theoretically around 24 fps
#from my testing we can get like 29 fps at max speed


def gForceMeter(accVector,width=diwidth,height=diheight,circles=[120],axes=True,linewidth=2,backColor='#5d1fa3',border=4,justification='center'):
    #circles = [] list of diameter of each circle to be drawn
    fillColor = '#ffffff'
    outlineColor = '#000000'
    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, width, height), fill=backColor)
    
    #basically we are shifting a 128x128 box left, right, or center
    relwidth = height
    if justification == 'center':
        shift = 16
    elif justification == 'left':
        shift = 0
    elif justification == 'right':
        shift = 32
    else:
        shift = 16
        
    #its pretty self explanatory what these do just by the names
    for diam in circles:
        draw.ellipse([(height/2-diam/2+shift,height/2-diam/2),(relwidth/2+diam/2+shift,height/2+diam/2)],width = linewidth, outline = outlineColor)

    if axes:
        draw.line([(relwidth/2+shift, border+shift),(relwidth/2+shift, height-border+shift)], width = linewidth, fill = outlineColor)
        draw.line([(shift+border, height/2+shift),(relwidth-border+shift, height/2+shift)], width = linewidth, fill = outlineColor)
    
    # Display image.
    disp.image(image)
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
    disp.image(image)
    print("Elapsed time:",str(time.time()-startTime))
 

dispBackground()
gForceMeter(1,circles=[120,80,40,10],justification ='right')