#!/usr/bin/env python3

import random
from typing import List
import pytest
from modules.convex_hull import ConvexHullPoint, multilayer_convex_hull


class PointMock(ConvexHullPoint):
    def __new__(cls, x, y, payload):
        return super().__new__(cls, (x, y))

    def __init__(self, x, y, payload):
        self.payload = payload


def mod_list(_list: List) -> List:
    return _list[:]


def mod_shuffle(_list: List) -> List:
    new_list = _list[:]
    random.shuffle(new_list)
    return new_list


def mod_reverse(_list: List) -> List:
    new_list = _list[:]
    new_list.reverse()
    return new_list


def mod_sort(_list: List) -> List:
    new_list = _list[:]
    new_list.sort()
    return new_list


def mod_sort_reverse(_list: List) -> List:
    new_list = _list[:]
    new_list.sort(reverse=True)
    return new_list


@pytest.mark.parametrize('modifier', [
    mod_list,
    mod_shuffle,
    mod_reverse,
    mod_sort,
    mod_sort_reverse
])
@pytest.mark.parametrize(
    "points, hull_layers",
    [
        [
            [[-1, 1], [1, 1], [1, -1], [-1, -1]],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
            ]
        ],
        [
            [[-1, 1], [1, 1], [1, -1], [-1, -1]],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [],
            ]
        ],
        [
            [[-1, 1], [1, 1], [1, -1], [-1, -1]],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [], [],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5]
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[0.5, 0.5]],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5]
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[0.5, 0.5], [0.5, -0.5]],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5]
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5]],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5]
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5]],
                [],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5], [-0.5, 0.5]
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5], [0.5, 0.5]],
                [],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5], [-0.5, 0.5],
                [0.3, 0.3]
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5], [0.5, 0.5]],
                [[0.3, 0.3]],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5], [-0.5, 0.5],
                [0.3, 0.3], [-0.3, -0.3],
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5], [0.5, 0.5]],
                [[0.3, 0.3], [-0.3, -0.3]],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5], [-0.5, 0.5],
                [0.3, 0.3], [-0.3, -0.3], [0.3, -0.3],
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5], [0.5, 0.5]],
                [[-0.3, -0.3], [0.3, -0.3], [0.3, 0.3]],
            ]
        ],
        [
            [
                [-1, 1], [1, 1], [1, -1], [-1, -1],
                [0.5, 0.5], [0.5, -0.5], [-0.5, -0.5], [-0.5, 0.5],
                [0.3, 0.3], [-0.3, -0.3], [0.3, -0.3], [-0.3, 0.3],
            ],
            [
                [[-1, -1], [-1, 1], [1, -1], [1, 1]],
                [[-0.5, -0.5], [-0.5, 0.5], [0.5, -0.5], [0.5, 0.5]],
                [[-0.3, -0.3], [-0.3, 0.3], [0.3, -0.3], [0.3, 0.3]],
            ]
        ],
    ]
)
def test_multilayer_hull(points, hull_layers, modifier):
    points_shuffled = modifier(points)
    expected_points = [point for layer in hull_layers for point in layer]
    hull_points = multilayer_convex_hull(points_shuffled, layers=len(hull_layers))
    expected_points.sort()
    hull_points.sort()
    assert hull_points == expected_points
