# Adapted from https://github.com/augiev/Shaper-Dominos

import svgwrite
from svgwrite import mm
import random
from cairosvg import svg2png
import math

# All dimensions in mm
DOMINO_WIDTH = 43.18
DOMINO_HEIGHT = 12.7
DOMINO_CORNER_RADIUS = 2.54
DOT_DIAMETER = 2.54
DOT_SPACING = 5.08

# These dot positions (left column and right column) always have dots
FIXED_DOT_POSITIONS = [0, 7, 8, 15]


def calculate_columns(length, padding, column_spacing):
    """Helper to calculate how many columns fit within a given label length."""
    return math.floor((length - 2 * padding) / (DOMINO_WIDTH + column_spacing))


def generate_all_valid_patterns():
    """Generate all valid dot patterns, as strings representing 16 bit binary numbers.

    Valid patterns are made up of dots and blanks in an 8x2 pattern which are
        - made up of exactly 10 dots, where 4 dots always make up the left-most and right-most column
        - not rotationally symmetric with themselves (top row is not the same as the reverse of the bottom row)
        - not rotationally symmetric with another domino

    Each pattern is represented as a 16-bit number, with the top row being the most significant bits,
    and the lower row being the least significant bits.
    """
    valid_patterns = set()

    for i in range(2 ** 16):
        pattern = f"{i:>016b}"

        if any(pattern[fixed_dot] != "1" for fixed_dot in FIXED_DOT_POSITIONS):
            # Fixed dot positions aren't set
            continue

        if pattern.count("1") != 10:
            # Wrong number of 1 bits
            continue

        if pattern == pattern[::-1]:
            # Bottom row is mirror image of top row
            continue

        if pattern[::-1] in valid_patterns:
            # Rotationally symmetric pattern already exists
            continue

        valid_patterns.add(pattern)

    return list(valid_patterns)


def generate_dominos(rows, columns):
    """Generate a random set of dominos for a given number of rows and columns.

    Yields the dominos in a grid format
    [
        [domino, domino], # column 1
        [domino, domino], # column 2
    ]
    """
    all_valid_patterns = generate_all_valid_patterns()
    number_of_dominos = rows * columns

    # Get a random set of dominos - explode if too many are requested
    try:
        dominos = random.sample(all_valid_patterns, number_of_dominos)
    except ValueError:
        raise RuntimeError(
            f"Tried to generate {number_of_dominos} dominos, but only {len(all_valid_patterns)} dominos exist!"
        )

    for column in range(columns):
        yield dominos[column * rows : (column + 1) * rows]


def draw_domino(
    domino, drawing, column_index, row_index, padding, row_spacing, column_spacing
):
    """Draw a single domino into an svg object."""
    x = padding + column_index * (DOMINO_WIDTH + column_spacing)
    y = padding + row_index * (DOMINO_HEIGHT + row_spacing)

    # Draw the rounded rectangle
    drawing.add(
        drawing.rect(
            (x * mm, y * mm),
            (DOMINO_WIDTH * mm, DOMINO_HEIGHT * mm),
            rx=DOMINO_CORNER_RADIUS * mm,
            ry=DOMINO_CORNER_RADIUS * mm,
            fill="black",
        )
    )

    # Add the dots
    for dot_index, dot in enumerate(domino):
        if dot != "1":
            continue
        x_offset = DOT_DIAMETER * 1.5
        y_offset = DOT_DIAMETER * 1.5
        if dot_index > 7:
            y_offset += DOT_SPACING

        drawing.add(
            drawing.circle(
                (
                    (x + x_offset + (DOT_SPACING) * (dot_index % 8)) * mm,
                    (y + y_offset) * mm,
                ),
                r=(DOT_DIAMETER / 2) * mm,
                fill="white",
            )
        )


def draw_dominos(
    rows, columns, output_filename, padding=5, row_spacing=5, column_spacing=5
):
    """Draw a grid of dominos as an SVG drawing object."""
    dominos = generate_dominos(rows, columns)

    width = 2 * padding + columns * DOMINO_WIDTH + (columns - 1) * column_spacing
    height = 2 * padding + rows * DOMINO_HEIGHT + (rows - 1) * row_spacing

    drawing = svgwrite.Drawing(
        output_filename,
        profile="tiny",
        height=height * mm,
        width=width * mm,
        size=(width * mm, height * mm),
    )

    for column_index, column in enumerate(dominos):
        for row_index, domino in enumerate(column):
            draw_domino(
                domino,
                drawing,
                column_index,
                row_index,
                padding,
                row_spacing,
                column_spacing,
            )

    return drawing


def generate_domino_png(
    rows,
    columns,
    filename,
    padding=5,
    row_spacing=DOT_SPACING,
    column_spacing=DOT_SPACING,
):
    """Draw a grid of dominos and save the output as a PNG."""
    drawing = draw_dominos(
        rows,
        columns,
        filename,
        row_spacing=row_spacing,
        column_spacing=row_spacing,
        padding=padding,
    )
    svg2png(
        bytestring=drawing.tostring(),
        write_to=filename,
        background_color="white",
        dpi=300,
    )
