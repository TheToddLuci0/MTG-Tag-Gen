from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from PIL import Image
from svglib.svglib import svg2rlg
from io import BytesIO
from reportlab.graphics import renderPDF
import argparse
import requests
import sys


# Put things to shrink names in here!
# They will be used one by one, starting at the top.
# In other words, if you prefer to only replace "Token" with "tkn" as a last resort, put it last!
REPLACERS = [
    {"key": "vs.",
     "value": "v."},
    {"key": "Token",
     "value": "Tkn"},
    {'key': 'Art Series',
     'value': 'Art'},
    {"key": "Substitute",
     "value": "Subx"},
    {"key": "Display",
     "value": "Disp."},
    {"key": "Commander",
     "value": "Cmndr"},
    {"key": "Adventure",
     "value": "Adv"},
    {"key": "Legend",
     "value": "Lgnd"},
    {"key": "Global",
     "value": "Glbl"},
    {"key": "Anthology",
     "value": "Ant."},
    {"key": "Duel Decks",
     "value": "D.D."},
]

# Constants for BCW traiding card dividers
# TODO Make these args!
HEIGHT = (3/8) * inch
WIDTH = (2 + (5/8)) * inch
MAX_ROWS = 24
MAX_COLS = 3
TARGET_HEIGHT = .2 * inch
VERBOSE = True
IMAGE_OFFSET = 5
FONT = "Times-Roman"
FONT_SIZE = 8.5
MAX_CHARS = 39

# Use a session in case ScryFall ever decides they want auth
s = requests.Session()
sets = s.get('https://api.scryfall.com/sets').json()
c = canvas.Canvas("mtg-labesl.pdf", pagesize=A4)
c.setAuthor("TheToddLuci0")

col = 0
row = 0

c.translate(.5*inch, .25*inch)
c.saveState()

for i in sets['data']:
    if VERBOSE:
        print(i['name'])
    # Figure out the text
    to = c.beginText()
    to.setFont(FONT, FONT_SIZE)
    n = i["name"]
    replacer = 0
    while len(n) > MAX_CHARS:
        # We're too long!
        try:
            n = n.replace(REPLACERS[replacer]['key'],
                          REPLACERS[replacer]['value'])
            replacer += 1
        except Exception as e:
            print("No replacers fix '{}'! Please add one!".format(n))
            print("Max length:\t{}".format(MAX_CHARS))
            print("Actual length:\t{}".format(len(n)))
            c.save()
            sys.exit(99)

    to.textOut(n)
    c.drawText(to)
    # Put the icon in
    r = s.get(i['icon_svg_uri'])
    image = svg2rlg(BytesIO(r.content))
    image.renderScale = (TARGET_HEIGHT / image.height)
    renderPDF.draw(image, c, to.getX() + IMAGE_OFFSET, 0)
    # Move to the next location
    if col == (MAX_COLS - 1) and row == (MAX_ROWS - 1):
        if VERBOSE:
            print("------------------------------------------\n\Making a new page!\n------------------------------------------")
        c.restoreState()
        c.showPage()
        c.translate(.5*inch, .25*inch)
        c.saveState()
        col = 0
        row = 0
    elif row == (MAX_ROWS - 1):
        row = 0
        col += 1
        c.restoreState()
        c.saveState()
        c.translate((col * WIDTH) + .1*inch, 0)
    else:
        row += 1
        c.translate(0, (HEIGHT + .1*inch))

c.save()
