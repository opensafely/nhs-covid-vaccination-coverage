import collections
import os

from IPython.display import Image
from IPython.core.display import SVG


ImageFormat = collections.namedtuple("ImageFormat", ["extension", "formatter"])


def pick_image_format():
    try:
        fmt = os.environ["IMAGE_FORMAT"]
    except KeyError:
        raise Exception("You must set the IMAGE_FORMAT environment variable to svg or png")

    if fmt == "svg":
        return ImageFormat("svg", SVG)
    if fmt == "png":
        return ImageFormat("png", Image)
