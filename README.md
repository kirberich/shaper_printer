# Raspberry pi domino printer

This is a small helper to generate dominos for a shaper origin and print them using a Brother QL printer - most of the actual domino creation logic is heavily informed by https://github.com/augiev/Shaper-Dominos. This is not meant to be a replacement for shaper tape, but just a little experiment.

This code is untested and will likely make your origin explode and burn down your workshop, and it won't be my fault!

Use actual shaper tape for anything serious!

## Setup

* Clone the repo
* Create a python3 virtualenv, (`python3 -m venv .env`)
* Activate the virtualenv (`source .env/bin/activate`)
* Install the requirements (`pip install -r requirements.txt`)

## Usage

You'll need your printer identifier and model - check the docs of brother_ql.

Run `./print <label_length> <printer_identifier> <printer_model> [--dry-run]`
For me, `./print 50 usb://0x04f9:0x20c0 QL-650TD` prints a label with one column of 4 dominos.

Dry run will generate the image file but won't actually print.
