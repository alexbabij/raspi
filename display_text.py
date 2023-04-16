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
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

#The screen will continue to display the last image sent to it, until it recieves something new

def dispText(textIn,textLoc,fontColor=[0,0,0,255],FONTSIZE=15,BORDER=5,width=width,height=height):
    startTime = time.time()
    # First define some constants to allow easy resizing of shapes.
    #BORDER = 20
    #FONTSIZE = 20

    image = Image.new("RGB", (width, height))

    # Get drawing object to draw on image.
    draw = ImageDraw.Draw(image)

    # Draw a green filled box as the background
    draw.rectangle((0, 0, width, height), fill=(255,255,255))
    #disp.image(image)

    # Draw a smaller inner purple rectangle
    # draw.rectangle(
    #     (0, 0, width - BORDER - 1, height - BORDER - 1), fill=(170, 0, 136)
    # )

    # Load a TTF Font
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", FONTSIZE)

    # Draw Some Text
    #text = "Hello Worldaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"
    # 0,0 = top left corner of display
    #fontColor = [0,0,0]

    #For some reason, the R and B in the RGBA values are swapped, but only for fill in draw.text, I have no idea why
    if textLoc == "center":
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (width // 2 - font_width // 2, height // 2 - font_height // 2),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc == "northwest":
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (BORDER,BORDER),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc == "southeast":
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (width-(BORDER+font_width),height-(BORDER+font_height)),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc == "northeast":
        (font_width, font_height) = font.getsize_multiline(textIn)
        draw.text(
            (BORDER,height-(BORDER+font_height)),
            textIn,
            font=font,
            fill=(fontColor[2], fontColor[1], fontColor[0], fontColor[3]),
        )
    elif textLoc == "southwest":
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
    disp.image(image)
    print("Elapsed time:",str(time.time()-startTime))
