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
     "value": "Sub"},
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
    {"key": "Cmndr Lgnds",
     "value": "C.L."},
    {"key": "Minigames",
     "value": "mGames"},
    {"key": "Foils", # Mystery Booster Retail Edition Foils
     "value": "Foil"},
    {"key": "Series", # Glbl Series Jiang Yanggu & Mu Yanling
     "value": "S."},
    {"key": "Promos", # Duels of the Planeswalkers 2015 Promos
     "value": "Pro"},
    {"key": "Sub Cards", # Innistrad: Midnight Hunt Sub Cards
     "value": "Subs"},
    {"key": "Playtest", # Mystery Booster Playtest Cards 2021
     "value": "Test"},
    {"key": "20", # Duels of the Planeswalkers 2015 Pro
     "value": ""},
    {"key": "Pure", # D.D.: Mirrodin Pure v. New Phyrexia
     "value": ""},
]

# List of set_type values from Scryfall
# https://scryfall.com/docs/api/sets
SET_TYPES = ["core", "expansion", "masters", "alchemy", "arsenal", "from_the_vault",
             "spellbook", "premium_deck", "duel_deck", "draft_inovation", "treasure_chest", "commander",
             "planechase", "archenemy", "vanguard", "funny", "starter", "box", "promo", "token", "memorabilia"]


parser = argparse.ArgumentParser(description='Generate MTG card divider labels')
parser.add_argument('-v', '--verbose', action="store_true")
parser.add_argument('-e', '--exclude-type', action="append", help="Do not generate labels for the given type (see https://scryfall.com/docs/api/sets)")
parser.add_argument('-t', '--type', action="append", help="ONLY generate labels for these types (see https://scryfall.com/docs/api/sets)")
parser.add_argument('-j', '--just', action="append", help="Generate labels for JUST the sets passed (eg m21)")
parser.add_argument('-o', '--outfile', help="Output filename")
parser.add_argument('--children', action="store_true", help="Generate labels for sub sets (tokens, promos, ect)")
# Tuning args
parser.add_argument("--height", default=(3/8) * inch, type=int, help="How tall to make the tags")
parser.add_argument("--width", default=(2 + (5/8)) * inch, type=int, help="How wide to make the tags")
parser.add_argument("--image-offset", default=5, type=float, help="Spacing between text and icon")
parser.add_argument("--font-size", default=11, type=float, help="How big to make the letters")
parser.add_argument("--max-chars", default=35, type=int, help="Maximum length of the string that will fit on the labels")
parser.add_argument("--font", default="Times-Roman")
args = parser.parse_args()
# Constants for BCW traiding card dividers
# TODO Dynamically calculate max rows/cols based on args (ie page size / width + padding?)
MAX_ROWS = 24
MAX_COLS = 3
TARGET_HEIGHT = args.height - 12.6
SPACE_X = .3*inch
SPACE_Y = .2*inch

# Use a session in case ScryFall ever decides they want auth
s = requests.Session()
if not args.just:
    sets = s.get('https://api.scryfall.com/sets').json()
else:
    sets = {"data":[]}
    for k in args.just:
        r = s.get('https://api.scryfall.com/sets/{}'.format(k))
        if r.status_code != 200:
            print("Invalid set name: {}".format(k))
            sys.exit(13)
        sets['data'].append(r.json())
c = canvas.Canvas(args.outfile, pagesize=A4)
c.setAuthor("TheToddLuci0")

col = 0
row = 0

c.translate(SPACE_X, SPACE_Y)
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
    if not args.children:
        if 'parent_set_code' in i.keys() and (not args.just or i['code'] not in args.just):
            if args.verbose:
                print("Skipping child set '{}', parent code '{}'".format(i['name'], i['parent_set_code']))
            continue
    if args.verbose:
        print(i['name'])
    # Get the image
    r = s.get(i['icon_svg_uri'])
    image = svg2rlg(BytesIO(r.content))
    # Figure out the text
    to = c.beginText(y=(TARGET_HEIGHT - args.font_size) /2 )
    to.setFont(args.font, args.font_size)
    n = i["name"].strip()
    replacer = 0
    while len(n) > args.max_chars:
        # We're too long!
        try:
            n = n.replace(REPLACERS[replacer]['key'],
                          REPLACERS[replacer]['value']).strip()
            replacer += 1
        except Exception as e:
            print("No replacers fix '{}'! Please add one!".format(n))
            print("Max length:\t{}".format(args.max_chars))
            print("Actual length:\t{}".format(len(n)))
            c.save()
            sys.exit(99)

    to.textOut(n)
    c.drawText(to)
    # Put the icon in
    image.renderScale = (TARGET_HEIGHT / image.height)
    renderPDF.draw(image, c, to.getX() + args.image_offset, 0)
    # Move to the next location
    if col == (MAX_COLS - 1) and row == (MAX_ROWS - 1):
        if args.verbose:
            print("------------------------------------------\n\Making a new page!\n------------------------------------------")
        c.restoreState()
        c.showPage()
        c.translate(SPACE_X, SPACE_Y)
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
