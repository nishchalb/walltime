# walltime

Walltime is a system that chooses a wallpaper on your system that best matches the current time of day.

## Dependencies

Walltime has a few dependencies. Before using it, the following python packages should also be installed:

1. Numpy

2. OpenCV2

3. Peewee

4. Scipy

5. Matplotlib

## Installation

Once the dependencies are installed, clone the repository. At this point, you can choose to either use walltime as a normal script, or you can make it work globally by adding the cloned repository to your PATH, or by moving walltime to somewhere in your path.

## Usage
`
usage: walltime [-h] [-u UPDATE] [-b] [-s]

Select the most appropriate of your wallpapers based on the current time of
day

optional arguments:
  -h, --help            show this help message and exit
  -u UPDATE, --update UPDATE
                        Update the database of images with the given
                        directory. A directory must be given. This will not
                        change the wallpaper
  -b, --best            Whether to use the best image or not. If this flag is
                        used, the best image will be selected. Otherwise, a
                        reasonable one will be used
  -s, --show            Display an image of the color for the current time
`
