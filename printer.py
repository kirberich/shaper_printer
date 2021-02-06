from brother_ql.backends.helpers import send
from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster


def print_image(filename, printer_identifier, model):
    printer = BrotherQLRaster(model)

    # Create the label
    convert(
        printer,
        [filename],
        "62",
        threshold=70,
        cut=True,
        dither=False,
        compress=False,
        red=False,
        rotate=90,
    )

    send(
        instructions=printer.data,
        printer_identifier=printer_identifier,
        backend_identifier="pyusb",
        blocking=True,
    )
