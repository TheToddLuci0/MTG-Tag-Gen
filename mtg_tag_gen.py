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

# List of set_type values from Scryfall
# https://scryfall.com/docs/api/sets
SET_TYPES = ["core", "expansion", "masters", "alchemy", "arsenal", "from_the_vault",
             "spellbook", "premium_deck", "duel_deck", "draft_inovation", "treasure_chest", "commander",
             "planechase", "archenemy", "vanguard", "funny", "starter", "box", "promo", "token", "memorabilia"]


parser = argparse.ArgumentParser(description='Generate MTG card divider labels')
parser.add_argument('-v', '--verbose', action="store_true")
parser.add_argument('-e', '--exclude-type', action="append", help="Do not generate labels for the given type")
parser.add_argument('-t', '--type', default=[], action="append", help="ONLY generate labels for these types")
# Tuning args
parser.add_argument("--height", default=(3/8) * inch, type=int, help="How tall to make the tags")
parser.add_argument("--width", default=(2 + (5/8)) * inch, type=int, help="How wide to make the tags")
parser.add_argument("--image-offset", default=5, type=int, help="Spacing between text and icon")
parser.add_argument("--font-size", default=8.5, type=float, help="How big to make the letters")
parser.add_argument("--max-chars", default=39, type=int, help="Maximum length of the string that will fit on the labels")
parser.add_argument("--font", default="Times-Roman")
args = parser.parse_args()
# Constants for BCW traiding card dividers
# TODO Dynamically calculate max rows/cols based on args (ie page size / width + padding?)
MAX_ROWS = 24
MAX_COLS = 3
TARGET_HEIGHT = args.height - 5

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
    if args.exclude_type and i['set_type'] in args.exclude_type:
        if args.verbose:
            print("Skipping '{}', type '{}'".format(i['name'], i['set_type']))
        continue
    if args.type and i['set_type'] not in args.set_type:
        if args.verbose:
            print("Skipping '{}', type '{}'".format(i['name'], i['set_type']))
        continue
    if args.verbose:
        print(i['name'])
    # Figure out the text
    to = c.beginText()
    to.setFont(args.font, args.font_size)
    n = i["name"]
    replacer = 0
    while len(n) > args.max_chars:
        # We're too long!
        try:
            n = n.replace(REPLACERS[replacer]['key'],
                          REPLACERS[replacer]['value'])
            replacer += 1
        except Exception as e:
            print("No replacers fix '{}'! Please add one!".format(n))
            print("Max length:\t{}".format(args.max-chars))
            print("Actual length:\t{}".format(len(n)))
            c.save()
            sys.exit(99)

    to.textOut(n)
    c.drawText(to)
    # Put the icon in
    r = s.get(i['icon_svg_uri'])
    image = svg2rlg(BytesIO(r.content))
    image.renderScale = (TARGET_HEIGHT / image.height)
    renderPDF.draw(image, c, to.getX() + args.image_offset, 0)
    # Move to the next location
    if col == (MAX_COLS - 1) and row == (MAX_ROWS - 1):
        if args.verbose:
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
        c.translate((col * args.width) + .1*inch, 0)
    else:
        row += 1
        c.translate(0, (args.height + .1*inch))

c.save()
