import logging
import time

from PIL import Image

from brother_ql.conversion import convert
from brother_ql.raster import BrotherQLRaster
from brother_ql.backends import backend_factory
from brother_ql.reader import interpret_response
from brother_ql.devicedependent import label_type_specs

TIMEOUT = 180000  # 180 seconds
EXPECTED_HEIGHT = label_type_specs["62"]["dots_printable"][0]


class PrintingError(Exception):
    pass


def send_to_printer(instructions, printer_identifier: str, blocking: bool):
    """A Slightly modified version of brother_ql.backends.helpers, changed to allow for a longer write timeout.

    The longer timeout is necessary because printing a meter-long label takes longer than the library allows.
    """
    be = backend_factory("pyusb")
    BrotherQLBackend = be["backend_class"]

    printer = BrotherQLBackend(printer_identifier)

    # Overwrite the pyusb backend write timeout
    printer.write_timeout = TIMEOUT

    # Send instructions to the printer
    start = time.time()
    printer.write(instructions)

    if not blocking:
        return True

    while time.time() - start < TIMEOUT / 1000:
        data = printer.read()
        if not data:
            time.sleep(1)
            continue

        try:
            result = interpret_response(data)
        except ValueError:
            logging.error(
                "TIME %.3f - Couln't understand response: %s", time.time() - start, data
            )
            continue

        if result["errors"]:
            raise PrintingError(", ".join(result["errors"]))
        if result["status_type"] == "Printing completed":
            return True

    return True


def print_image(filename, printer_identifier, model, hq):
    printer = BrotherQLRaster(model)

    # Validate the image size
    with Image.open(filename) as img:
        width, height = img.size
        expected_height = EXPECTED_HEIGHT * 2 if hq else EXPECTED_HEIGHT
        if abs(height - EXPECTED_HEIGHT) > 0:
            raise RuntimeError(
                f"Image size doesn't match. Image is {height} high, printer requires {EXPECTED_HEIGHT}"
            )

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
        dpi_600=hq,
    )

    send_to_printer(
        instructions=printer.data,
        printer_identifier=printer_identifier,
        blocking=True,
    )
