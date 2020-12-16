#!/usr/bin/env python3

import argparse
import os

from PIL import Image


def steg(img_to_hide, carrier_img):
    """
    Steg image to hide into carrier image
    :param img_to_hide: image to hide
    :param carrier_img: carrier image
    :return: stegged image
    """
    width, height = img_to_hide.size
    rgb_data = []

    for y in range(height):
        for x in range(width):
            # Get MSB from image to hide
            r_hide, g_hide, b_hide = img_to_hide.load()[x, y]
            r_hide = r_hide >> 6
            g_hide = g_hide >> 6
            b_hide = b_hide >> 6

            # Remove LSB from carrier image
            r_hide_in, g_hide_in, b_hide_in = carrier_img.load()[x, y]
            r_hide_in = r_hide_in & 0b11111100
            g_hide_in = g_hide_in & 0b11111100
            b_hide_in = b_hide_in & 0b11111100

            # OR MSB from image to hide into the LSB of carrier
            rgb_data.append((r_hide | r_hide_in,
                             g_hide | g_hide_in,
                             b_hide | b_hide_in))
    stegged = Image.new("RGB", img_to_hide.size)
    stegged.putdata(rgb_data)
    return stegged


def unsteg(img):
    """
    Unsteg image from LSB of stegged image
    :param img: stegged image
    :return: unstegged image
    """
    width, height = img.size
    encoded_image = img.load()
    rgb_data = []

    for y in range(height):
        for x in range(width):
            # Get LSB from encoded image and move to MSB
            r_encoded, g_encoded, b_encoded = encoded_image[x, y]
            r_encoded = (r_encoded & 0b0000011) << 6
            g_encoded = (g_encoded & 0b0000011) << 6
            b_encoded = (b_encoded & 0b0000011) << 6
            rgb_data.append((r_encoded, g_encoded, b_encoded))
    unstegged = Image.new("RGB", img.size)
    unstegged.putdata(rgb_data)
    return unstegged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hide image in another image")
    parser.add_argument("-s", "--steg", help="carrier image to steg")
    parser.add_argument("-i", "--input-file", help="image to hide")
    parser.add_argument("-o", "--output-file", help="output image", required=True)
    parser.add_argument("-u", "--unsteg", help="unsteg image")
    argparse_namespace = parser.parse_args()

    if argparse_namespace.steg and argparse_namespace.unsteg:
        parser.exit(-1, "ERROR: Can't steg and unsteg simultaneously")
    if argparse_namespace.steg:
        if not argparse_namespace.input_file:
            parser.exit(-1, "ERROR: Please set input file to hide in image")
        else:
            if not os.path.isfile(argparse_namespace.steg):
                parser.exit(-1, "ERROR: file '{}' does not exist".format(argparse_namespace.steg))
            if not os.path.isfile(argparse_namespace.input_file):
                parser.exit(-1, "ERROR: file '{}' does not exist".format(argparse_namespace.input_file))
            img_to_hide = Image.open(argparse_namespace.input_file)
            carrier_img = Image.open(argparse_namespace.steg)
            hide_w, hide_h = img_to_hide.size
            carrier_w, carrier_h = carrier_img.size
            if hide_w > carrier_w or hide_h > carrier_h:
                print("ERROR: Image to hide must be smaller than carrier image")
                exit(-1)
            steg(img_to_hide, carrier_img).save(argparse_namespace.output_file)
    if argparse_namespace.unsteg:
        if not os.path.isfile(argparse_namespace.unsteg):
            parser.exit(-1, "ERROR: file '{}' does not exist".format(argparse_namespace.unsteg))
        img = Image.open(argparse_namespace.unsteg)
        unsteg(img).save(argparse_namespace.output_file)
