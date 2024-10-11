#!/usr/bin/env python3
"""
    Helper functions to draw figures using matplotlib.
"""

from collections.abc import Iterable
from os.path import exists, join as os_path_join
from os import makedirs
import logging
from io import StringIO
from typing import List
import config.config
from config.static_portfolios import STATIC_PORTFOLIOS
import modules.data_filter as data_filter
import modules.data_types as data_types
import multiprocessing
import multiprocessing.connection
from modules.data_filter import multilayer_convex_hull, multigon_filter, multiprocess_convex_hull
from itertools import chain
from config.asset_colors import RGB_COLOR_MAP
import importlib
import pickle
import functools
import config
import time

from modules.data_types import Portfolio


def compose_plot_data(portfolios: Iterable[data_types.Portfolio], field_x: str, field_y: str):
    return [[{
            'x': portfolio.get_stat(field_x),
            'y': portfolio.get_stat(field_y),
            'text': '\n'.join([
                portfolio.plot_tooltip_assets(),
                '—' * max(len(x) for x in portfolio.plot_tooltip_assets().split('\n')),
                portfolio.plot_tooltip_stats(),
            ]),
            'marker': portfolio.plot_marker,
            'color': portfolio.plot_color(dict(RGB_COLOR_MAP.items())),
            'size': 100 if portfolio.plot_always else 50 / portfolio.number_of_assets(),
            'linewidth': 0.5 if portfolio.plot_always else 1 / portfolio.number_of_assets(),
            }] for portfolio in portfolios
            ]

def save_data(
        assets: list[str] = [],
        source: multiprocessing.connection.Connection = None,
        coord_pair: tuple[str, str] = None,
        hull_layers: int = None,
        persistent_portfolios: list[data_types.Portfolio] = None):
    logger = logging.getLogger(__name__)
    data_stream_end_pickle = pickle.dumps(data_types.DataStreamFinished())
    total_bytes = 0
    t1 = time.time()
    with open('portfolios.dat', 'wb') as f:
        while True:
            bytes = source.recv_bytes()
            if bytes == data_stream_end_pickle:
                break
            f.write(f'{len(bytes)}'.encode('utf-8'))
            f.write(bytes)
            total_bytes += len(bytes)
            logger.info(f'Received {total_bytes} bytes, rate: {total_bytes / (time.time() - t1) // 1024 // 1024} MB/sec')


def plot_data(
        assets: list[str] = [],
        source: multiprocessing.connection.Connection = None,
        coord_pair: tuple[str, str] = None,
        hull_layers: int = None,
        persistent_portfolios: list[data_types.Portfolio] = None):
    logger = logging.getLogger(__name__)
    with multiprocessing.Pool() as pool:
        all_xy_points = []
        data_stream_end_pickle = pickle.dumps(data_types.DataStreamFinished())
        while True:
            bytes = source.recv_bytes()
            if bytes == data_stream_end_pickle:
                break
            portfolios_batch = pickle.loads(bytes)
            deserialized_portfolios = map(functools.partial(Portfolio.deserialize, assets=assets), portfolios_batch)
            portfolio_xy_points = list(map(functools.partial(data_filter.PortfolioXYPoint, coord_pair=coord_pair), deserialized_portfolios))
            all_xy_points.extend(portfolio_xy_points)
            if len(all_xy_points) > config.config.CHUNK_SIZE * multiprocessing.cpu_count():
                # logger.info(f'{coord_pair}: Compacting {len(all_xy_points)} points')
                all_xy_points = multiprocess_convex_hull(pool, all_xy_points)
                # logger.info(f'{coord_pair}: Compacted to {len(all_xy_points)} points')
        # logger.info(f'Refining {len(all_xy_points)} points')
        final_points = multiprocess_convex_hull(pool, all_xy_points)
    # logger.info(f'Refined to {len(final_points)} points')
    final_portfolios = map(lambda point: point.portfolio, final_points)
    portfolios_for_plot = list(chain(final_portfolios, persistent_portfolios))
    logger.info(f'Plotting {len(portfolios_for_plot)} portfolios')
    portfolios_for_plot.sort(key=lambda x: -x.number_of_assets())
    plot_data = compose_plot_data(portfolios_for_plot, field_x=coord_pair[1], field_y=coord_pair[0])
    draw_circles_with_tooltips(
        circle_lines=plot_data,
        xlabel=coord_pair[1],
        ylabel=coord_pair[0],
        title=f'{coord_pair[0]} vs {coord_pair[1]}',
        directory='result',
        filename=f'{coord_pair[0]} - {coord_pair[1]} - Multigon',
        asset_color_map=dict(RGB_COLOR_MAP),
    )

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-statements
def draw_circles_with_tooltips(
        circles=None,
        xlabel=None, ylabel=None, title=None,
        directory='.', filename='plot',
        asset_color_map=None, portfolio_legend=None):
    logger = logging.getLogger(__name__)

    if not exists(directory):
        makedirs(directory)

    plt = importlib.import_module('matplotlib.pyplot')
    pltlines = importlib.import_module('matplotlib.lines')

    plt.rcParams["font.family"] = "monospace"
    _, axes = plt.subplots(figsize=(9, 6))

    padding_percent = 15
    xlim_min = min(c['x'] for c in circles)
    xlim_max = max(c['x'] for c in circles)
    xlim_min_padded = xlim_min - padding_percent * (xlim_max - xlim_min) / 100
    xlim_max_padded = xlim_max + padding_percent * (xlim_max - xlim_min) / 100
    ylim_min = min(c['y'] for c in circles)
    ylim_max = max(c['y'] for c in circles)
    ylim_min_padded = ylim_min - padding_percent * (ylim_max - ylim_min) / 100
    ylim_max_padded = ylim_max + padding_percent * (ylim_max - ylim_min) / 100
    axes.set_xlim(xlim_min_padded, xlim_max_padded)
    axes.set_ylim(ylim_min_padded, ylim_max_padded)
    axes.tick_params(axis='x', which='minor', bottom=True)
    axes.tick_params(axis='y', which='minor', left=True)
    axes.set_axisbelow(True)
    plt.grid(visible=True, which='both', axis='both')
    plt.title(title, zorder=0)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    if asset_color_map:
        if portfolio_legend:
            portfolio_legend_sorted = sorted(list(portfolio_legend), key=lambda x: x.plot_title())
            handles = [
                pltlines.Line2D(
                    [0], [0],
                    marker='o',
                    label=portfolio.plot_title(),
                    linewidth=0,
                    markerfacecolor=portfolio.plot_color(asset_color_map),
                    markeredgecolor='black'
                ) for portfolio in portfolio_legend_sorted
            ]
            axes.legend(
                handles=handles,
                fontsize='6',
                facecolor='white',
                framealpha=1
            ).set_zorder(1)
        else:
            handles = [
                pltlines.Line2D(
                    [0], [0],
                    marker='o',
                    label=label,
                    linewidth=0,
                    markerfacecolor=color,
                    markeredgecolor='black'
                ) for label, color in asset_color_map.items()
            ]
            axes.legend(
                handles=handles,
                fontsize='6',
                facecolor='white',
                framealpha=1
            ).set_zorder(1)

    for index, circle in enumerate(circles):
        axes.scatter(
            x=circle['x'],
            y=circle['y'],
            s=circle['size'],
            marker=circle['marker'],
            facecolor=circle['color'],
            edgecolor='black',
            linewidth=circle['linewidth'],
            gid=f'patch_{index: 08d}',
            zorder=2
        )

    plt.savefig(os_path_join(directory, filename + '.png'), format="png", dpi=300)
    logger.info(f'Plot ready: {os_path_join(directory, filename + ".png")}')

    return

    for index, circle in enumerate(all_circles):
        axes.annotate(
            gid=f'tooltip_{index: 08d}',
            text=circle['text'],
            xy=(circle['x'], circle['y']),
            xytext=(0, 8),
            textcoords='offset pixels',
            color='black',
            horizontalalignment='center',
            verticalalignment='bottom',
            fontsize=8,
            bbox={
                'boxstyle': 'round,pad=0.5',
                'facecolor': (1.0, 1.0, 1.0, 0.9),
                'linewidth': 0.5,
                'zorder': 3,
            },
        )
    virtual_file = StringIO()
    plt.savefig(virtual_file, format="svg")

    # XML trickery for interactive tooltips

    element_tree = importlib.import_module('xml.etree.ElementTree')
    element_tree.register_namespace("", "http://www.w3.org/2000/svg")
    tree, xmlid = element_tree.XMLID(virtual_file.getvalue())
    tree.set('onload', 'init(evt)')

    for index, circle in enumerate(all_circles):
        element = xmlid[f'tooltip_{index: 08d}']
        element.set('visibility', 'hidden')

    for index, circle in enumerate(all_circles):
        element = xmlid[f'patch_{index: 08d}']
        element.set('onmouseover', f"ShowTooltip('tooltip_{index: 08d}')")
        element.set('onmouseout', f"HideTooltip('tooltip_{index: 08d}')")

    script = """
        <script type="text/ecmascript">
        <![CDATA[
        function init(evt) {
            if (window.svgDocument == null) { svgDocument = evt.target.ownerDocument; }
        }
        function ShowTooltip(cur) {
            svgDocument.getElementById(cur).setAttribute('visibility',"visible")
        }
        function HideTooltip(cur) {
            svgDocument.getElementById(cur).setAttribute('visibility',"hidden")
        }
        ]]>
        </script>
        """

    tree.insert(0, element_tree.XML(script))
    element_tree.ElementTree(tree).write(os_path_join(directory, filename + '.svg'))
    logger.info(f'Plot ready: {os_path_join(directory, filename + ".svg")}')

def report_errors_in_static_portfolios(portfolios: List[Portfolio], tickers_to_test: List[str]):
    logger = logging.getLogger(__name__)
    num_errors = 0
    for static_portfolio in STATIC_PORTFOLIOS:
        error = static_portfolio.asset_allocation_error(tickers_to_test)
        if error:
            num_errors += 1
            logger.error(f'Static portfolio {static_portfolio}\nhas invalid allocation: {error}')
    return num_errors

if __name__ == '__main__':
    from math import sin, cos
    demo_data = []
    for j in range(0, 10):
        demo_data_line = []
        for i in range(0, 100, 2):
            demo_data_line.append({
                'x': ((i + j * 100) / 1000) ** 2 * cos((i + j * 100) / 25),
                'y': (i + j * 100)**0.5 * sin((i + j * 100) / 25),
                'text': f'{i}\n{i**0.5: .0f}\n{j}',
                'color': (1.0 * (i + j * 100) / 1000, abs(cos((i + j * 100) / 25)), 1.0 - (i + j * 100) / 1000),
                'size': (i + j * 100) / 20,
            })
        demo_data.append(demo_data_line)
    COLOR_MAP = {
        'red': (1, 0, 0),
        'blue': (0, 0, 1),
        'cyan': (0, 1, 1),
        'green': (0, 1, 0),
        'yellow': (1, 1, 0)
    }
    draw_circles_with_tooltips(
        xlabel='X LABEL', ylabel='Y LABEL',
        title='Demo',
        circle_lines=demo_data,
        asset_color_map=COLOR_MAP,
        directory='result',
        filename='plot_demo'
    )
