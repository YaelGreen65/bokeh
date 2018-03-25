#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2017, Anaconda, Inc. All rights reserved.
#
# Powered by the Bokeh Development Team.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------
''' Functions useful for dealing with hexacognal tilings.

For more information on the concepts employed here, see this informative page

    https://www.redblobgames.com/grids/hexagons/

'''

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
log = logging.getLogger(__name__)

from bokeh.util.api import general, dev ; general, dev

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports

# External imports
import numpy as np

# Bokeh imports
from .dependencies import import_optional

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

@general((1,0,0))
def hexbin(x, y, size, orientation="pointytop", aspect_scale=1):
    ''' Perform an equal-weight binning of data points into hexagonal tiles.

    For more sophiscticated use cases, e.g. weighted binning or scaling
    individual tiles proprtional to some other quantity, consider using
    HoloViews.

    Args:
        x (array[float]) :
            A NumPy array of x-coordinates for binning

        y (array[float]) :
            A NumPy array of y-coordinates for binning

        size (float) :
            The size of the hexagonal tiling.

            The size is defined as the distance from the center of a hexagon
            to the top corner for "pointytop" orientation, or from the center
            to a side corner for "flattop" orientation.

        orientation (str, optional) :
            Whether the hex tile orientation should be "pointytop" or
            "flattop". (default: "pointytop")

        aspect_scale (float, optional) :
            Apply a scaling to the aspect ratio. (default: 1)

            Useful in conjuction with ``Plot.aspect_scale`` to display visually
            regular hexagons, even with the aspect ratio of the data space is
            not 1-1. Equivalent to performing a binning in "screen space".

    Returns:
        DataFrame

        The resulting DataFrame will have columns *q* and *r* that specify
        hexagon tile locations in axial coordinates, and a column *counts* that
        provides the count for each tile.

    .. warning::
        Hex binning only functions on linear scales, i.e. not on log plots.

    '''
    pd = import_optional('pandas')

    q, r = cartesian_to_axial(x, y, size, orientation, aspect_scale=aspect_scale)

    df = pd.DataFrame(dict(r=r, q=q))
    return df.groupby(['q', 'r']).size().reset_index(name='counts')

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

@dev((1,0,0))
def cartesian_to_axial(x, y, size, orientation, aspect_scale=1):
    ''' Map Cartesion *(x,y)* points to axial *(q,r)* coordinates of enclosing
    tiles.

    This function was adapted from:

        https://www.redblobgames.com/grids/hexagons/#pixel-to-hex

    Args:
        x (array[float]) :
            A NumPy array of x-coordinates for binning

        y (array[float]) :
            A NumPy array of y-coordinates for binning

        size (float) :
            The size of the hexagonal tiling.

            The size is defined as the distance from the center of a hexagon
            to the top corner for "pointytop" orientation, or from the center
            to a side corner for "flattop" orientation.

        orientation (str) :
            Whether the hex tile orientation should be "pointytop" or
            "flattop". (default: "pointytop")

        aspect_scale (float, optional) :
            Apply a scaling to the aspect ratio. (default: 1)

            Useful in conjuction with ``Plot.aspect_scale`` to display visually
            regular hexagons, even with the aspect ratio of the data space is
            not 1-1. Equivalent to performing a binning in "screen space".

    Returns:
        (array[int], array[int])

    '''
    coords = _HEX_FLAT if orientation == 'flattop' else _HEX_POINTY
    x =  x / size * (aspect_scale if orientation == "pointytop" else 1)
    y = -y / size / (aspect_scale if orientation == "flattop" else 1)
    q = coords[0] * x + coords[1] * y
    r = coords[2] * x + coords[3] * y
    return _round_hex(q, r)

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

_HEX_FLAT = [2.0/3.0, 0.0, -1.0/3.0, np.sqrt(3.0)/3.0]
_HEX_POINTY = [np.sqrt(3.0)/3.0, -1.0/3.0, 0.0, 2.0/3.0]

def _round_hex(q, r):
    ''' Round floating point axial hex coordinates to integer *(q,r)*
    coordinates.

    This code was adapted from:

        https://www.redblobgames.com/grids/hexagons/#rounding

    Args:
        q (array[float]) :
            NumPy array of Floating point axial *q* coordinates to round

        r (array[float]) :
            NumPy array of Floating point axial *q* coordinates to round

    Returns:
        (array[int], array[int])

    '''
    x = q
    z = r
    y = -x-z

    rx = np.round(x)
    ry = np.round(y)
    rz = np.round(z)

    dx = np.abs(rx - x)
    dy = np.abs(ry - y)
    dz = np.abs(rz - z)

    cond = (dx > dy) & (dx > dz)
    q = np.where(cond              , -(ry + rz), rx)
    r = np.where(~cond & ~(dy > dz), -(rx + ry), rz)

    return q.astype(int), r.astype(int)

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
