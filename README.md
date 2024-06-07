# dewalnay.py

## Installation
`poetry install` should do it. You may need to install SciPy dependencies
(LAPACK, BLAS) separately.

## Synopsis

    dewalnay.py -w 1920 -h 1080 -l '#c8a2c8' -r '#8c0035' -a 30 dewalnay.png
![Generated image](examples/dewalnay.png)


## Command-line options

    usage: dewalnay.py [--help] [-w W] [-h H] [-n N] [-l #RRGGBB] [-r #RRGGBB]
                       [-a ANGLE] [--min-value MIN_VALUE] [--max-value MAX_VALUE]
                       [--fuzz FUZZ] [--border-pts N] [--max-force MAX_FORCE]
                       [--epsilon EPSILON]
                       [outfile]

    Generate a wallpaper using Delaunay triangulation

    positional arguments:
      outfile               the image to be written (default: 'out.png')

    optional arguments:
      --help                show this help message and exit
      -w W, --width W       image width in pixels (default: 1920)
      -h H, --height H      image height in pixels (default: 1080)
      -n N, --num-pts N     number of interior points (default: 50)
      -l #RRGGBB, --left-color #RRGGBB
                            hexcode for left color (default: #000000)
      -r #RRGGBB, --right-color #RRGGBB
                            hexcode for right color (default: #ffffff)
      -a ANGLE, --angle ANGLE
                            angle to rotate gradient CCW in degrees (default: 0)
      --min-value MIN_VALUE
                            minimum greyscale value (default: 15)
      --max-value MAX_VALUE
                            maximum greyscale value (default: 240)
      --fuzz FUZZ           radius of interval of possible greyscale values
                            (default: 32)
      --border-pts N        number of points added to each border line (default:
                            5)
      --max-force MAX_FORCE
                            max magnitude of net Coulomb force on a point
                            (default: 3)
      --epsilon EPSILON     Coulomb proportionality constant (default: 100000)
