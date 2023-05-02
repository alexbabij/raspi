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

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 24000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()


disp = st7735.ST7735R(spi, rotation=90, invert=False, cs=cs_pin, dc=dc_pin, rst=reset_pin, baudrate=BAUDRATE)
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

# class piDisplay:
#     def __init__(self):
#         self.input = ""



def dispText(textIn,textLoc,fontColor=[255,255,255,255],FONTSIZE=15,BORDER=5,width=diwidth,height=diheight,backColor=[0,0,0],
             refreshRate=False,updateScreen=True,imgIn=False):
    #updateScreen = True : sends the new image to the screen, if False, returns image that would be sent to screen
    #backColor = False : skips drawing the background
    #imgIn = ... :can use this in combination with updateScreen = False and drawBackground = False to stack/combine multiple images together
    #then display the combined image. Basically this lets us draw text of different size at different places on the screen by
    #calling this function multiple times. This should work because we import this entire file which includes importing PIL
    
    #fontColor = [R,G,B,opacity (0-255)]
    startTime = time.time()
    # First define some constants to allow easy resizing of shapes.
    #BORDER = 20
    #FONTSIZE = 20
    if imgIn == False:
        image = Image.new("RGB", (width, height))
    else:
        image = imgIn

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    if backColor != False:
        draw.rectangle((0, 0, width, height), fill=(backColor[2],backColor[1],backColor[0]))

    
    fstrt = time.time()
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
    #debugString+= "time to load font: "+str(time.time()-fstrt)+"\n" #DEBUG
    # Draw Some Text
    #text = "Hello Worldaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
    # 0,0 = top left corner of display
    #fontColor = [0,0,0]
    dfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    if refreshRate != False:
        refreshString = refreshRate+" fps"

        (dfont_width, dfont_height) = dfont.getsize_multiline(refreshString)
        draw.text(
            (width-(dfont_width),height-(dfont_height)),
            refreshString,
            font=dfont,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),)


    #debugString = "time to process output: "+str(time.time()-startTime)+"\n"#DEBUG
    # Load a TTF Font
    
    #For some reason, the R and B in the RGBA values are swapped, I have no idea why
    if textLoc == "center":
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (width // 2 - font_width // 2, height // 2 - font_height // 2),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc in ["northwest", "nw"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (BORDER,BORDER),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc in ["southeast", "se"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (width-(BORDER+font_width),height-(BORDER+font_height)),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc in ["southwest", "sw"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (BORDER,height-(BORDER+font_height)),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc in ["northeast", "ne"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (width-(BORDER+font_width),BORDER),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )    
    else: #Put text in center as default
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (width // 2 - font_width // 2, height // 2 - font_height // 2),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    # Display image.
    if updateScreen:
        disp.image(image)
    else:
        return image
#     debugString += "Elapsed time: "+str(time.time()-startTime)+"\n"#DEBUG
#     if 0:
#         print(debugString)
#  #DEBUG

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
 