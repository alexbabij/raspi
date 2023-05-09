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


def dispText(textIn,textLoc='center',fontColor=[255,255,255,255],FONTSIZE=15,BORDER=5,width=diwidth,height=diheight,fontBackground=False,
             backColor=False,refreshRate=False,updateScreen=True,imgIn=False,tAlign='left'):
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
        draw.rectangle((0, 0, width, height), fill=(backColor[0],backColor[1],backColor[2]))

    
    fstrt = time.time()
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)
    #debugString+= "time to load font: "+str(time.time()-fstrt)+"\n" #DEBUG
    # Draw Some Text
    #text = "Hello Worldaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
    # 0,0 = top left corner of display
    #fontColor = [0,0,0]
    # Load a TTF Font
    dfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)
    if refreshRate != False:
        refreshString = refreshRate+" fps"

        (dfont_width, dfont_height) = dfont.getsize_multiline(refreshString)
        draw.text(
            (0,height-(dfont_height)), #width-(dfont_width)
            refreshString,
            font=dfont,
            fill=(fontColor[0], fontColor[1], fontColor[2], fontColor[3]),align=tAlign)


    #debugString = "time to process output: "+str(time.time()-startTime)+"\n"#DEBUG
    

    if textLoc in ["center", "c"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        if fontBackground != False:
            draw.rectangle((width // 2 - font_width // 2, height // 2 - font_height // 2, width // 2 + font_width // 2, height // 2 + font_height // 2), 
                           fill=(fontBackground[0],fontBackground[1],fontBackground[2]))
        draw.text(
            (width // 2 - font_width // 2, height // 2 - font_height // 2),
            textIn,
            font=font,
            fill=(fontColor[0], fontColor[1], fontColor[2], fontColor[3]),align=tAlign
        )
    elif textLoc in ["northwest", "nw"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        if fontBackground != False:
            draw.rectangle((BORDER,BORDER,BORDER+font_width,BORDER+font_height), 
                           fill=(fontBackground[0],fontBackground[1],fontBackground[2]))
        draw.text(
            (BORDER,BORDER),
            textIn,
            font=font,
            fill=(fontColor[0], fontColor[1], fontColor[2], fontColor[3]),align=tAlign
        )
    elif textLoc in ["southeast", "se"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        if fontBackground != False:
            draw.rectangle((width-(BORDER+font_width),height-(BORDER+font_height),width-BORDER,height-BORDER), 
                           fill=(fontBackground[0],fontBackground[1],fontBackground[2]))
        draw.text(
            (width-(BORDER+font_width),height-(BORDER+font_height)),
            textIn,
            font=font,
            fill=(fontColor[0], fontColor[1], fontColor[2], fontColor[3]),align=tAlign
        )
    elif textLoc in ["southwest", "sw"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        if fontBackground != False:
            draw.rectangle((BORDER,height-(BORDER+font_height),BORDER+font_width,height-BORDER), 
                           fill=(fontBackground[0],fontBackground[1],fontBackground[2]))
        draw.text(
            (BORDER,height-(BORDER+font_height)),
            textIn,
            font=font,
            fill=(fontColor[0], fontColor[1], fontColor[2], fontColor[3]),align=tAlign
        )
    elif textLoc in ["northeast", "ne"]:
        (font_width, font_height) = font.getsize_multiline(textIn)
        if fontBackground != False:
            draw.rectangle((width-(BORDER+font_width),BORDER,width-BORDER,BORDER+font_height), 
                           fill=(fontBackground[0],fontBackground[1],fontBackground[2]))
        draw.text(
            (width-(BORDER+font_width),BORDER),
            textIn,
            font=font,
            fill=(fontColor[0], fontColor[1], fontColor[2], fontColor[3]),align=tAlign
        )    
    else: #Put text in center as default
        (font_width, font_height) = font.getsize_multiline(textIn)
        if fontBackground != False:
            draw.rectangle((width // 2 - font_width // 2, height // 2 - font_height // 2, width // 2 + font_width // 2, height // 2 + font_height // 2), 
                           fill=(fontBackground[0],fontBackground[1],fontBackground[2]))
        draw.text(
            (width // 2 - font_width // 2, height // 2 - font_height // 2),
            textIn,
            font=font,
            fill=(fontColor[0], fontColor[1], fontColor[2], fontColor[3]),align=tAlign
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
    
    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    #Draw rectangle with dimensions of entire screen
    draw.rectangle((0, 0, width, height), fill=(backColor[0],backColor[1],backColor[2]))
    #disp.image(image)
  
    
    # Display image.
    disp.image(image)
    print("Elapsed time:",str(time.time()-startTime))
 