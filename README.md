# 🐟 FishScript

**FishScript** is the world’s most unnecessary aquarium programming language.

It is a tiny esolang where programs happen inside an aquarium, variables are fish, functions are rituals, and errors are probably caused by a shark.

## Install for development

```bash
pip install -e .
```

## Open the IDE

```bash
fishscript ide
```

## Run a `.fish` file

```bash
fishscript run fishscript/examples/hello.fish
```

## FishScript example

```fish
AQUARIUM OPENS

HATCH snacks AS ["kelp", "worm"]
DROP "pizza algae" INTO snacks

SING "Random snack:"
SING CHOOSE FROM snacks

PANICFISH

AQUARIUM CLOSES
```

## Syntax guide

### Program

```fish
AQUARIUM OPENS
AQUARIUM CLOSES
```

### Comments

```fish
BUBBLE this is a comment
```

### Variables

```fish
HATCH x AS 5
x MUTATES INTO 10
x SWALLOWS 3
x NIBBLES 1
```

### Output and input

```fish
SING x
FISH x FROM VOID
```

### Random

```fish
HATCH secret AS DICEFISH 1 10
```

### Lists

```fish
HATCH snacks AS ["kelp", "worm"]
DROP "pizza algae" INTO snacks
EAT INDEX 0 FROM snacks

SING LENGTH OF snacks
SING CHOOSE FROM snacks
SING INDEX 0 FROM snacks
```

### Math

```fish
HATCH x AS SUM OF 5 AND 3
HATCH y AS PRODUCT OF x AND 10
```

Supported:

- `SUM OF a AND b`
- `DIFFERENCE OF a AND b`
- `PRODUCT OF a AND b`
- `QUOTIENT OF a AND b`
- `REMAINDER OF a AND b`

### Conditions

```fish
IF x SMELLS LIKE y
REEF
    SING "same"
SURFACE
OTHERWATER
REEF
    SING "different"
SURFACE
```

Supported:

- `SMELLS LIKE`
- `SMELLS NOT LIKE`
- `SMELLS LESS THAN`
- `SMELLS MORE THAN`
- `EXISTS IN`

### Loops

```fish
WHILE x STILL SWIMMING
REEF
    SING x
    x NIBBLES 1
SURFACE
```

### Functions / rituals

```fish
RITUAL DOUBLE WITH fishy
REEF
    fishy SWALLOWS fishy
    RELEASE fishy
SURFACE

SING DOUBLE(5)
```

## Build desktop app

Install PyInstaller:

```bash
pip install pyinstaller
```

Build the IDE:

```bash
pyinstaller --name FishScript --windowed --onefile fishscript/ide.py
```

The app will appear in `dist/`.

## Website

The `website/` folder is ready for GitHub Pages, Netlify, or Vercel.

## License

MIT
