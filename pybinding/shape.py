import numpy as np
import matplotlib.pyplot as plt

from . import _cpp
from . import pltutils
from .utils import with_defaults

__all__ = ['Polygon', 'primitive', 'rectangle', 'regular_polygon', 'circle',
           'translational_symmetry']


class Polygon(_cpp.Polygon):
    """Shape defined by a list of vertices

    Parameters
    ----------
    vertices : list of array_like
        Polygon vertices. Must be defined in clockwise or counterclockwise order.
    """

    def __init__(self, vertices):
        super().__init__()
        self.vertices = vertices

    @property
    def vertices(self):
        return list(zip(self.x, self.y))

    @vertices.setter
    def vertices(self, vertices):
        x, y = zip(*vertices)
        if len(x) < 3:
            raise ValueError("A polygon must have at least 3 sides")

        self.x = np.array(x, dtype=np.float32)
        self.y = np.array(y, dtype=np.float32)

    def plot(self, **kwargs):
        plt.plot(np.append(self.x, self.x[0]), np.append(self.y, self.y[0]),
                 **with_defaults(kwargs, color='black'))
        plt.axis('scaled')
        pltutils.despine(trim=True)
        pltutils.add_margin()


class Circle(_cpp.Circle):
    def plot(self, **kwargs):
        plt.gca().add_artist(plt.Circle(tuple(self.center), self.r, fill=False,
                                        **with_defaults(kwargs, color='black')))
        plt.axis('scaled')
        pltutils.despine(trim=True)
        pltutils.add_margin()


def primitive(v1=None, v2=None, v3=None, nanometers=False):
    """Shape of the lattice's primitive unit cell.

    Parameters
    ----------
    v1, v2, v3 : int or float
        Number of unit vector lengths in the respective primitive vector directions.

    nanometers : bool
        If set to True, take length in nanometers instead of number of unit vector lengths.
    """

    lengths = tuple((v or 0) for v in (v1, v2, v3))
    return _cpp.Primitive(lengths, nanometers)


def rectangle(x, y=None):
    y = y if y else x
    x0 = x / 2
    y0 = y / 2
    return Polygon([[x0, y0], [x0, -y0], [-x0, -y0], [-x0, y0]])


def regular_polygon(num_sides, radius, angle=0):
    from math import pi, sin, cos
    angles = [angle + 2 * n * pi / num_sides for n in range(num_sides)]
    return Polygon([(radius * sin(a), radius * cos(a)) for a in angles])


def circle(radius, center=(0, 0, 0)):
    return Circle(radius, center)


def translational_symmetry(a1=True, a2=True, a3=True):
    """Simple translational symmetry

    Parameters
    ----------
    a1, a2, a3 : bool or float
        Control translation in the 'a1, a2, a3' lattice vector directions.
        Possible values:
            False - No translational symmetry in this direction.
            True - Translation length is automatically set to the unit cell length.
            <number> - Manually set the translation length in nanometers.
    """
    def to_cpp_params(value):
        if value is False:
            return -1  # disabled
        elif value is True:
            return 0  # automatic length
        else:
            return value  # manual length

    lengths = tuple(to_cpp_params(a) for a in (a1, a2, a3))
    return _cpp.Translational(lengths)
