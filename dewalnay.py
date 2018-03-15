#!/usr/bin/python

from random import random, randint
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw, ImageColor, ImageOps
from math import sin, cos, pi


def coulomb_force(i, j, epsilon=100000):
    """Compute the vector force between points i and j, as per Coulomb's law.
    Keyword arguments:
    epsilon -- the proportionality constant (default 100,000)
    """
    ij = [ci - cj for ci, cj in zip(i, j)]
    ij_norm = sum(c * c for c in ij)**0.5
    if ij_norm > 0:
        return [epsilon * c / (ij_norm**3) for c in ij]
    else:
        return [0, 0]


def __main__():
    image_size = (1920, 1080)

    # color_left = ImageColor.getrgb("#c8a2c8")
    color_left = ImageColor.getrgb("#d97f25")
    color_right = ImageColor.getrgb("#8c0035")

    angle = pi / 6
    NUM_PTS = 50
    VALUE_MIN = 15
    VALUE_MAX = 240
    SHADING_FUZZ = 0.125
    BORDER_PASSES = 5
    MAX_FORCE = 3

    # Generate points list.
    points = [[random() * image_size[0], random() * image_size[1]]
              for _ in range(NUM_PTS)]

    # Apply repulsive forces to points until no net force exceeds MAX_FORCE
    # in magnitude.
    forces = []
    while forces and max(forces,
                         key=lambda f: sum(c * c for c in f)) < MAX_FORCE**2:
        for i, pti in enumerate(points):
            forces = [coulomb_force(pti, ptj) for ptj in points]
            net_force = [sum(col) for col in zip(*forces)]

            # Update positions, clipping to window size.
            pti = [max(0, min(cm, ci + cf))
                   for ci, cf, cm in zip(pti, net_force, image_size)]

    # Add the corners. This ensures the triangulation will take up the
    # entire image.
    points.extend([(0, 0), (image_size[0], 0), (0, image_size[1]), image_size])

    # Now randomly generate more points on the border to avoid oversaturating
    # the corners.
    for _ in range(BORDER_PASSES):
        points.extend([(randint(0, image_size[0]), 0),
                       (randint(0, image_size[0]), image_size[1]),
                       (0, randint(0, image_size[1])),
                       (image_size[0], randint(0, image_size[1]))])

    # Initial image is grayscale for simplicity, is colorized later.
    image = Image.new('L', image_size, 0)
    dr = ImageDraw.Draw(image)

    dt = Delaunay(points)
    for tri in dt.simplices:
        # tri is a list of indices
        # PIL needs tuples because PIL is _special_
        pts = tuple(tuple(int(x) for x in points[i]) for i in tri)

        # Shade by centroid x-pos.
        centroid = tuple(sum(col) // len(col) for col in zip(*pts))
        value_pct = (centroid[0] / image_size[0] * cos(angle) +
                     centroid[1] / image_size[1] * sin(angle))

        # Fuzz the value uniformly from [-fuzz, fuzz]
        value_pct += 2 * SHADING_FUZZ * random() - SHADING_FUZZ

        # Clip to [0, 1]
        value_pct = max(0, min(1, value_pct))

        # Interpolate to [VALUE_MIN, VALUE_MAX]
        value = VALUE_MIN + (VALUE_MAX - VALUE_MIN) * value_pct

        dr.polygon(pts, fill=(int(value),))

    del dr

    image = ImageOps.colorize(image, color_left, color_right)

    image.save("dewalnay.png", "PNG")


if __name__ == "__main__":
    __main__()
