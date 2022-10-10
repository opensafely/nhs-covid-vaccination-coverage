import collections
import os

from IPython.display import Image
from IPython.core.display import SVG


ImageFormat = collections.namedtuple("ImageFormat", ["extension", "formatter"])
DEFAULT_IMAGE_FORMAT = "png"


def pick_image_format():
    fmt = os.environ.get("IMAGE_FORMAT", DEFAULT_IMAGE_FORMAT)

    if fmt == "svg":
        return ImageFormat("svg", SVG)
    if fmt == "png":
        return ImageFormat("png", Image)
    raise ValueError(f"Unknown IMAGE_FORMAT '{fmt}', you must specify one of 'svg' or 'png'")
