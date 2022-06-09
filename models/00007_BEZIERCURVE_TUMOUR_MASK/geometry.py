import logging
import os
import warnings
from pathlib import Path

import imageio as io
import numpy as np
from scipy.special import binom
from skimage import draw, morphology


def get_nodular_points(n=10, scale=0.8):
    """Create n random points that follow a circular pattern with random offset"""

    points = np.empty((n, 2))
    for i, a in enumerate(np.linspace(0, 2 * np.pi, n)):
        points[i, 0] = np.cos(a) + np.random.randn() * 0.1
        points[i, 1] = np.sin(a) + np.random.randn() * 0.1
    return points * scale


def get_stellate_points(n=10, scale=0.8):
    """Create n random points that follow a circular pattern with random offset"""

    points = np.empty((n, 2))
    sign = 1
    for i, a in enumerate(np.linspace(0, 2 * np.pi, n)):
        #         sign *= -1
        points[i, 0] = np.cos(a) + sign * np.random.randn() * 0.5
        points[i, 1] = np.sin(a) + sign * np.random.randn() * 0.5
    return points * scale


def get_random_points(n=5, scale=0.8, mindst=None, rec=0):
    """create n random points in the unit square, which are *mindst*
    apart, then scale them."""

    mindst = mindst or 0.7 / n
    a = np.random.rand(n, 2)
    d = np.sqrt(np.sum(np.diff(ccw_sort(a), axis=0), axis=1) ** 2)
    if np.all(d >= mindst) or rec >= 200:
        return a * scale
    else:
        return get_random_points(n=n, scale=scale, mindst=mindst, rec=rec + 1)


params = {
    "oval": {
        "rad": [0.3, 0.51],
        "edgy": 0.01,
        "n": [3, 4],
        "scale": [140, 150],  # [50, 70],
        "func": get_random_points,
    },
    "lobulated": {
        "rad": [0.3, 0.61],
        "edgy": 0.01,
        "n": [5, 7],
        "scale": [140, 150],  # [50, 70],
        "func": get_random_points,
    },
    "nodular": {
        "rad": [0.25, 0.61],
        "edgy": 0.01,
        "n": [30, 51],
        "scale": [36, 72],  # [20, 36],
        "func": get_nodular_points,
    },
    "stellate": {
        "rad": [0.0, 0.26],
        "edgy": 10.0,
        "n": [20, 31],
        "scale": [30, 45],  # [20, 25],
        "func": get_stellate_points,
    },
    "irregular": {
        "rad": [0.0, 0.31],
        "edgy": 0.01,
        "n": [60, 81],
        "scale": [30, 45],  # [20, 25],
        "func": get_stellate_points,
    },
}

"""
https://stackoverflow.com/questions/50731785/create-random-shape-contour-using-matplotlib/50751932#50751932
"""
bernstein = lambda n, k, t: binom(n, k) * t**k * (1.0 - t) ** (n - k)


def bezier(points, num=200):
    N = len(points)
    t = np.linspace(0, 1, num=num)
    curve = np.zeros((num, 2))
    for i in range(N):
        curve += np.outer(bernstein(N - 1, i, t), points[i])
    return curve


class Segment:
    """Class for the different segments of the curve based on points and angles"""

    def __init__(self, p1, p2, angle1, angle2, **kw):
        self.p1 = p1
        self.p2 = p2
        self.angle1 = angle1
        self.angle2 = angle2
        self.numpoints = kw.get("numpoints", 100)
        r = kw.get("r", 0.3)
        d = np.sqrt(np.sum((self.p2 - self.p1) ** 2))
        self.r = r * d
        self.p = np.zeros((4, 2))
        self.p[0, :] = self.p1[:]
        self.p[3, :] = self.p2[:]
        self.calc_intermediate_points(self.r)

    def calc_intermediate_points(self, r):
        self.p[1, :] = self.p1 + np.array(
            [self.r * np.cos(self.angle1), self.r * np.sin(self.angle1)]
        )
        self.p[2, :] = self.p2 + np.array(
            [self.r * np.cos(self.angle2 + np.pi), self.r * np.sin(self.angle2 + np.pi)]
        )
        self.curve = bezier(self.p, self.numpoints)


def get_curve(points, **kw):
    """get and return the curve based on input points"""

    segments = []
    for i in range(len(points) - 1):
        seg = Segment(
            points[i, :2], points[i + 1, :2], points[i, 2], points[i + 1, 2], **kw
        )
        segments.append(seg)
    curve = np.concatenate([s.curve for s in segments])
    return segments, curve


def ccw_sort(p):
    d = p - np.mean(p, axis=0)
    s = np.arctan2(d[:, 0], d[:, 1])
    return p[np.argsort(s), :]


def get_bezier_curve(a, rad=0.2, edgy=0):
    """given an array of points *a*, create a curve through
    those points.
    *rad* is a number between 0 and 1 to steer the distance of
          control points.
    *edgy* is a parameter which controls how "edgy" the curve is,
           edgy=0 is smoothest."""

    p = np.arctan(edgy) / np.pi + 0.5
    a = ccw_sort(a)
    a = np.append(a, np.atleast_2d(a[0, :]), axis=0)
    d = np.diff(a, axis=0)
    ang = np.arctan2(d[:, 1], d[:, 0])
    f = lambda ang: (ang >= 0) * ang + (ang < 0) * (ang + 2 * np.pi)
    ang = f(ang)
    ang1 = ang
    ang2 = np.roll(ang, 1)
    ang = p * ang1 + (1 - p) * ang2 + (np.abs(ang2 - ang1) > np.pi) * np.pi
    ang = np.append(ang, [ang[0]])
    a = np.append(a, np.atleast_2d(ang).T, axis=1)
    s, c = get_curve(a, r=rad, method="var")
    x, y = c.T
    return x, y, a


def sample_params(params, shape):
    """Define the sample geometric parameters"""

    n = np.random.randint(*params[shape]["n"])
    rad = np.random.uniform(*params[shape]["rad"])
    edgy = params[shape]["edgy"]
    scale = np.random.uniform(*params[shape]["scale"])
    func = params[shape]["func"]
    return n, rad, edgy, scale, func


def get_fg_shape(params, h, w, shape, xshift = 0, yshift = 0):
    """Get the shape based on point matrices"""

    n, rad, edgy, scale, point_generator = sample_params(params, shape)
    pad = 10
    a = point_generator(n=n, scale=scale)
    x, y, _ = get_bezier_curve(a, rad=rad, edgy=edgy)
    x -= x.mean()
    y -= y.mean()
    dx = x.max() - x.min()
    dy = y.max() - y.min()
    # moving the points where shapes intersect (x and y) around via xshift and yshift
    # xshift = np.random.randint(-(h-dx)//2+pad, (h-dx)//2-pad)
    # yshift = np.random.randint(-(w-dy)//3+pad, (w-dx)//2-pad)
    x += h / 2 + xshift
    y += w / 2 + yshift
    xx, yy = draw.polygon(x, y, shape=(h,w))

    # Some points in the polygon might lie outside the height or width of the final image.
    # As a fallback, we iteratively increase image size until the mask fits onto the image.
    # Lastly, the image is scaled back to its original height h and width w.
    # This way we have a consistent returned image size, while the tradeoff is that.
    # large masks will occupy a vast amount of space in the image.
    # Masks are the same size (optimized for 256x256) indifferent of the image height h and width w.
    img = None
    multiplier = 1
    while img is None:
        try:
            img = np.zeros((h*multiplier, w*multiplier), dtype=np.uint8)
            img[xx, yy] = 1
            img = img[:h, :w]
        except:
            pass
        multiplier = multiplier + 1
    return img


def get_random_image(h=128, w=128, shapes=None):
    """Get the random mask based on height width and shapes"""

    if shapes is None:
        shapes = ["oval", "lobulated", "nodular", "stellate", "irregular"]
    shape = np.random.randint(len(shapes))
    img = get_fg_shape(params, h, w, shapes[shape])
    img = morphology.closing(img)
    return img
