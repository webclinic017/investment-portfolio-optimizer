[![Prospector](https://github.com/worldemar/investment-portfolio-optimizer/actions/workflows/linter.yml/badge.svg)](https://github.com/worldemar/investment-portfolio-optimizer/actions/workflows/linter.yml)
[![Code QL](https://github.com/worldemar/investment-portfolio-optimizer/actions/workflows/codeql.yml/badge.svg)](https://github.com/worldemar/investment-portfolio-optimizer/actions/workflows/codeql.yml)

### Investment portfolio optimizer

This simple script will simulate rebalancing portfolios with given set of assets and display statistics.

### How to use

- Install requirements via `python3 -m pip install -r requirements.txt`

- Save market data into [asset_returns.csv](asset_returns.csv) file. Each row is one rebalancing period, each column is revenue from corresponding asset. Look at example file for details.
- Open [asset_colors.py](asset_colors.py) and edit asset colors to your taste.
- Run `optimizer.py` with parameters:
  - `--precision=10` - Precision is specified in percent. Asset allocation will be stepped according to this value.
  - `--hull=3` - Use ConvexHull algorithm to select only edge-case portfolios. This considerably speeds up plotting.
     In most cases these portfolios are most interesting anyway. This settings is 0 by default.
     Note that in this case ALL portfolios will be drawn on SVG. Your browser might not be able to display it.

Results of edge case portfolios will be displayed in terminal.

Check SVG graphs in `result` folder for all portfolios performances.

### What does it actually do?

Script will generate all possible investment portfolios with every asset allocated from 0 to 100% stepping according to `--precision` parameter.

Then every portfolio is simulated through market history, rebalancing at every step. Rebalancing assumes selling all assets with new prices and buying them back according to portfolio's asset allocation. For example:

| Asset1  | Asset2  | Asset1 (20%)           | Asset2 (80%)           | Portfolio value            |
| ------- | ------- | ---------------------- | ---------------------- | -------------------------- |
| (start) | (start) | 0.2                    | 0.8                    | 1                          |
| -10%    |  25%    | 0.2 - 10% = 0.18       | 0.8 + 25% = 1          | 0.18 + 1 = 1.18            |
|         |         | 1.18 * 20% = 0.236     | 1.18 * 80% = 0.944     | 1.18 = 0.236 + 0.944       |
|  15%    |  -5%    | 0.236 + 15% = 0.2714   | 0.944 - 5% = 0.8968    | 0.2714 + 0.8968 = 1.1682   |
|         |         | 1.1682 * 20% = 0.23364 | 1.1682 * 80% = 0.93456 | 1.1682 = 0.23364 + 0.93456 |

If `--hull` is specified and is not zero, script will use ConvexHull algorithm to select only edge-case portfolios for
each plot. Edge cases are calculated separately for each plot.

### Demo SVGs
(You need to download them to enable interactivity)

<img src="./image-demos/cagr_variance.svg" width="50%"><img src="./image-demos/cagr_stdev.svg" width="50%">
<img src="./image-demos/gain_sharpe.svg" width="50%"><img src="./image-demos/sharpe_variance.svg" width="50%">

DONE :: 888037 portfolios tested in 15.29s
times: prepare = 2.98s, simulate = 12.30s
--- Graph ready: CAGR % - Variance --- 5.16s
--- Graph ready: Sharpe - Variance --- 1.08s
--- Graph ready: CAGR % - Stdev --- 5.09s
--- Graph ready: Sharpe - Stdev --- 3.90s
--- Graph ready: CAGR % - Sharpe --- 0.85s
DONE :: in 172.43s

processes=16
DONE :: 888037 portfolios tested in 11.50s, rate: 77k/s
--- Graph ready: CAGR % - Variance --- 1.85s
--- Graph ready: Sharpe - Variance --- 1.06s
--- Graph ready: CAGR % - Stdev --- 1.55s
--- Graph ready: Sharpe - Stdev --- 1.21s
--- Graph ready: CAGR % - Sharpe --- 0.85s
DONE :: in 60.26s, rate = 14k/s