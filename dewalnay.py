#!/usr/bin/python

from random import random, randint
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw, ImageColor, ImageOps
from math import sin, cos, pi
from argparse import ArgumentParser


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
    parser = ArgumentParser(
        description="Generate a wallpaper using Delaunay triangulation", add_help=False)
    parser.add_argument("--help", action="help", help="show this help message and exit")

    parser.add_argument("-w", "--width",       type=int,   metavar="W", default=1920,
                        help="image width in pixels (default: 1920)")
    parser.add_argument("-h", "--height",      type=int,   metavar="H", default=1080,
                        help="image height in pixels (default: 1080)")
    parser.add_argument("-n", "--num-pts",     type=int,   metavar="N", default=50,
                        help="number of interior points (default: 50)")
    parser.add_argument("-l", "--left-color",  type=str,   metavar="#RRGGBB", default="#000000",
                        help="hexcode for left color (default: #000000)")
    parser.add_argument("-r", "--right-color", type=str,   metavar="#RRGGBB", default="#ffffff",
                        help="hexcode for right color (default: #ffffff)")
    parser.add_argument("-a", "--angle",       type=int,   default=0,
                        help="angle to rotate gradient CCW in degrees (default: 0)")

    parser.add_argument("--min-value",         type=int,                default=15,
                        help="minimum greyscale value (default: 15)")

    parser.add_argument("--max-value",         type=int,                default=240,
                        help="maximum greyscale value (default: 240)")

    parser.add_argument("--fuzz",              type=int,              default=32,
                        help="radius of interval of possible greyscale values (default: 32)")
    parser.add_argument("--border-pts",        type=int,   metavar="N", default=5,
                        help="number of points added to each border line (default: 5)")
    parser.add_argument("--max-force",         type=int,                default=3,
                        help="max magnitude of net Coulomb force on a point (default: 3)")
    parser.add_argument("--epsilon",           type=float,              default=100000,
                        help="Coulomb proportionality constant (default: 100000)")

    parser.add_argument("outfile",             type=str,                default="out.png", nargs="?",
                        help="the image to be written (default: 'out.png')")

    args = parser.parse_args()

    IMAGE_SIZE = (args.width, args.height)

    NUM_PTS = args.num_pts

    LEFT_COLOR = ImageColor.getrgb(args.left_color)
    RIGHT_COLOR = ImageColor.getrgb(args.right_color)

    ANGLE = args.angle / 180 * pi

    MIN_VALUE = args.min_value
    MAX_VALUE = args.max_value

    SHADING_FUZZ = args.fuzz / 255
    BORDER_PASSES = args.border_pts
    MAX_FORCE = args.max_force
    EPSILON = args.epsilon

    # Generate points list.
    points = [[random() * IMAGE_SIZE[0], random() * IMAGE_SIZE[1]]
              for _ in range(NUM_PTS)]

    # Apply repulsive forces to points until no net force exceeds MAX_FORCE
    # in magnitude.
    forces = []
    while forces and max(forces,
                         key=lambda f: sum(c * c for c in f)) < MAX_FORCE**2:
        for i, pti in enumerate(points):
            forces = [coulomb_force(pti, ptj, epsilon=EPSILON) for ptj in points]
            net_force = [sum(col) for col in zip(*forces)]

            # Update positions, clipping to window size.
            pti = [max(0, min(cm, ci + cf))
                   for ci, cf, cm in zip(pti, net_force, IMAGE_SIZE)]

    # Add the corners. This ensures the triangulation will take up the
    # entire image.
    points.extend([(0, 0), (IMAGE_SIZE[0], 0), (0, IMAGE_SIZE[1]), IMAGE_SIZE])

    # Now randomly generate more points on the border to avoid oversaturating
    # the corners.
    for _ in range(BORDER_PASSES):
        points.extend([(randint(0, IMAGE_SIZE[0]), 0),
                       (randint(0, IMAGE_SIZE[0]), IMAGE_SIZE[1]),
                       (0, randint(0, IMAGE_SIZE[1])),
                       (IMAGE_SIZE[0], randint(0, IMAGE_SIZE[1]))])

    # Initial image is grayscale for simplicity, is colorized later.
    image = Image.new('L', IMAGE_SIZE, 0)
    dr = ImageDraw.Draw(image)

    dt = Delaunay(points)
    for tri in dt.simplices:
        # tri is a list of indices
        # PIL needs tuples because PIL is _special_
        pts = tuple(tuple(int(x) for x in points[i]) for i in tri)

        # Shade by centroid x-pos.
        centroid = tuple(sum(col) // len(col) for col in zip(*pts))
        value_pct = (centroid[0] / IMAGE_SIZE[0] * cos(ANGLE) +
                     centroid[1] / IMAGE_SIZE[1] * sin(ANGLE))

        # Fuzz the value uniformly from [-fuzz, fuzz]
        value_pct += 2 * SHADING_FUZZ * random() - SHADING_FUZZ

        # Clip to [0, 1]
        value_pct = max(0, min(1, value_pct))

        # Interpolate to [MIN_VALUE, MAX_VALUE]
        value = MIN_VALUE + (MAX_VALUE - MIN_VALUE) * value_pct

        dr.polygon(pts, fill=(int(value),))

    del dr

    image = ImageOps.colorize(image, LEFT_COLOR, RIGHT_COLOR)

    image.save(args.outfile, "PNG")


if __name__ == "__main__":
    __main__()
