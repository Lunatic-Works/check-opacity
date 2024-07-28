#!/usr/bin/env python3

import os
import sys
from math import pi

import imageio.v3 as imageio
import numpy as np


def oklab_to_srgb(c):
    c @= np.asarray(
        [
            [1, +0.3963377774, +0.2158037573],
            [1, -0.1055613458, -0.0638541728],
            [1, -0.0894841775, -1.2914855480],
        ]
    ).T
    c **= 3
    c @= np.asarray(
        [
            [+4.0767416621, -3.3077115913, +0.2309699292],
            [-1.2684380046, +2.6097574011, -0.3413193965],
            [-0.0041960863, -0.7034186147, +1.7076147010],
        ]
    ).T
    c = np.where(
        c > 0.0031308, 1.055 * np.maximum(c, 0) ** (1 / 2.4) - 0.055, 12.92 * c
    )
    return c


def main(in_filename):
    print("in_filename", in_filename)

    img = imageio.imread(in_filename)
    if img.ndim != 3 or img.shape[2] != 4:
        print("Alpha channel not found")
        return
    img = img[:, :, 3]

    out = np.empty(img.shape + (3,), dtype=np.float64)
    out[:, :, 0] = 0.5

    min_alpha = img.min()
    max_alpha = img.max()
    print("min_alpha", min_alpha, "max_alpha", max_alpha)
    theta = img / max_alpha * 5 / 3 * pi
    out[:, :, 1] = np.cos(theta)
    out[:, :, 2] = np.sin(theta)

    out[img == 0] = 0
    out[img == max_alpha] = 0

    img = oklab_to_srgb(out)

    img = np.clip(img, 0, 1)
    img = np.rint(255 * img).astype(np.uint8)

    basename, extname = os.path.splitext(in_filename)
    out_filename = f"{basename}_opacity.png"
    print("out_filename", out_filename)
    imageio.imwrite(out_filename, img)


if __name__ == "__main__":
    for in_filename in sys.argv[1:]:
        main(in_filename)
    input("Finished")
