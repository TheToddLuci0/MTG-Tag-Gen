# Generate labels for your MTG card dividers

Targets the [BCW dividers](https://www.amazon.com/BCW-Brand-Trading-Divider-Cards/dp/B09JWZTTYD/) I use. Should be adjustable to your needs

Uses the [SkryFall API](https://scryfall.com/docs/api)

## Useage
Calling with no arguments will generate labes for my dividers of choice, for all set types. Pretty much everything is tunable to your needs, it will just require some experimentation to find the right settings for your divider of choice.

```
usage: mtg_tag_gen.py [-h] [-v] [-e EXCLUDE_TYPE] [-t TYPE] [-j JUST] [-o OUTFILE] [--children] [--height HEIGHT] [--width WIDTH] [--image-offset IMAGE_OFFSET] [--font-size FONT_SIZE] [--max-chars MAX_CHARS] [--font FONT]

Generate MTG card divider labels

options:
  -h, --help            show this help message and exit
  -v, --verbose
  -e EXCLUDE_TYPE, --exclude-type EXCLUDE_TYPE
                        Do not generate labels for the given type (see https://scryfall.com/docs/api/sets)
  -t TYPE, --type TYPE  ONLY generate labels for these types (see https://scryfall.com/docs/api/sets)
  -j JUST, --just JUST  Generate labels for JUST the sets passed (eg m21)
  -o OUTFILE, --outfile OUTFILE
                        Output filename
  --children            Generate labels for sub sets (tokens, promos, ect)
  --height HEIGHT       How tall to make the tags
  --width WIDTH         How wide to make the tags
  --image-offset IMAGE_OFFSET
                        Spacing between text and icon
  --font-size FONT_SIZE
                        How big to make the letters
  --max-chars MAX_CHARS
                        Maximum length of the string that will fit on the labels
  --font FONT
  ```
## Example
The file [example.pdf](./example.pdf) was generated with the following command

```shell
python mtg_tag_gen.py -o example.pdf 
```

## TODO
- [x] Params
- [ ] CI/CD
- [ ] Probably a half dozen other things
- [x] Docs