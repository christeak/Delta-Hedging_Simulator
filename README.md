# Delta-Hedging Simulator

A quantitative finance project simulating, analyzing, and visualizing the performance of dynamic delta-hedging strategies for European options within the Black-Scholes framework.

## Table of Contents
- [Overview](#overview)
- [Underlying Asset & Model](#underlying-asset--model)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Results](#results)
- [Insights & Observations](#insights--observations)
- [Possible Extensions](#possible-extensions)
- [References](#references)

## Overview

This simulator provides an educational and practical tool to understand how dynamic hedging reduces risk, how hedging errors arise, and how they depend on key parameters such as volatility, rebalancing frequency, and market conditions. It bridges theoretical option pricing and realistic trading constraints.

**Objectives**
- Implement Black-Scholes pricing for European call and put options
- Compute option Greeks: Delta, Gamma, Vega
- Simulate the dynamic delta hedging of a short option position
- Analyze hedging errors and their P&L distribution via Monte Carlo
- Study the impact of rebalancing frequency, volatility misspecification, and transaction costs

## Underlying Asset & Model

The underlying asset price follows a Geometric Brownian Motion:

$$dS_t = \mu S_t\, dt + \sigma S_t\, dW_t$$

European options are priced using the Black-Scholes closed-form formulas. The hedged portfolio consists of a short European call and a dynamically adjusted position in the underlying: at each rebalancing date, Delta is recomputed from the current price and remaining maturity, the underlying position is adjusted accordingly, and the final hedging P&L is evaluated exactly at maturity ($\tau=0$), against the option's real payoff.

Paths can be simulated under either measure by choosing $\mu$: setting $\mu = r$ simulates under the risk-neutral measure (the natural choice when only testing the hedge mechanics against the Black-Scholes price); setting $\mu \neq r$ simulates under a real-world drift, letting you observe hedging performance when the market doesn't move exactly as the risk-neutral pricing measure assumes.

## Repository Structure

```
.
├── bs_functions.py     # Black-Scholes pricing (call/put) and Greeks: Delta, Gamma, Vega
├── simulation.py        # GBM path simulation + single-path delta-hedge simulation
├── experiments.py       # Monte Carlo P&L distribution, rebalancing frequency & vol misspecification studies
├── visualization.py     # main script: runs all experiments and produces the plots below
└── requirements.txt
```

## Installation

```bash
git clone <repo-url>
cd Delta-Hedging_Simulator
pip install -r requirements.txt
```

**requirements.txt**
```
numpy
scipy
matplotlib
```

## Usage

```bash
python visualization.py
```

The script prompts for $S_0$, $K$, $T$, $r$, $\mu$, $\sigma$, the number of rebalancing steps $N$, and a transaction cost (as a % of trade value), then produces, in order:

1. A single simulated path: underlying price, Delta over time, and hedging error over time
2. The Monte Carlo distribution of the final hedging P&L (2,000 paths)
3. Hedging error (std. dev.) as a function of rebalancing frequency
4. Mean hedging P&L as a function of volatility misspecification

Each experiment can also be called directly, e.g.:

```python
from experiments import monte_carlo_hedging_pnl

pnls = monte_carlo_hedging_pnl(
    n_paths=5000, S0=100, K=100, T=1, r=0.05, mu=0.05,
    sigma_true=0.20, sigma_hedge=0.20, N=52, transaction_cost=0.0,
)
print(pnls.mean(), pnls.std())
```

## Results

Benchmark case: $S_0=K=100$, $r=\mu=5\%$, $\sigma=20\%$, $T=1$ year, 5,000 Monte Carlo paths per experiment.

**Rebalancing frequency vs. hedging error (no transaction costs)**

| N (rebalancing dates) | Mean P&L | Std. dev. of P&L |
|---|---|---|
| 1 | 0.0291 | 5.9956 |
| 4 | -0.0444 | 3.2254 |
| 12 | -0.0102 | 1.9446 |
| 52 (weekly) | -0.0149 | 0.9378 |
| 252 (daily) | 0.0042 | 0.4401 |

**Volatility misspecification (N=52, no transaction costs)** — hedging with an assumed volatility $\sigma_{hedge}$ while the underlying actually moves with $\sigma_{true}=0.20$:

| $\sigma_{hedge}$ | Mean P&L | Std. dev. of P&L |
|---|---|---|
| 0.10 | -3.8563 | 2.2795 |
| 0.15 | -1.9748 | 1.2965 |
| 0.20 (correct) | -0.0149 | 0.9378 |
| 0.25 | 1.9717 | 1.1474 |
| 0.30 | 3.9669 | 1.5196 |

**Transaction costs (N=252, daily rebalancing)**

| Transaction cost | Mean P&L | Std. dev. of P&L |
|---|---|---|
| 0% | 0.0042 | 0.4401 |
| 0.5% of trade value | -2.8526 | 1.0753 |

## Insights & Observations

- **Delta hedging is perfect only in continuous time.** The standard deviation of the final P&L drops from 5.996 at $N=1$ to 0.440 at $N=252$: discrete rebalancing leaves residual risk that shrinks toward zero as the rebalancing frequency increases, consistent with the continuous-time replication argument underlying Black-Scholes.
- **Volatility misspecification is directional, not just noise.** Pricing and hedging with $\sigma_{hedge} < \sigma_{true}$ (under-estimating volatility) produces systematic losses on a short option position, while $\sigma_{hedge} > \sigma_{true}$ produces systematic gains: the mean P&L increases from -3.86 to +3.97 as the assumed volatility rises from 0.10 to 0.30, and is close to zero when $\sigma_{hedge} = \sigma_{true}$. This follows from the option seller being short Gamma. Each rebalancing locks in a cost of roughly $\frac{1}{2}\Gamma(\Delta S)^2$, which on average amounts to $\frac{1}{2}\Gamma S^2 \sigma_{true}^2\,dt$, while the time decay earned on the option, priced at $\sigma_{hedge}$, only compensates $\frac{1}{2}\Gamma S^2 \sigma_{hedge}^2\,dt$. The hedging P&L therefore accrues at

$$d\Pi - r\Pi\,dt = \frac{1}{2}\,\Gamma_{hedge}\,S^2\left(\sigma_{hedge}^2 - \sigma_{true}^2\right)dt,$$

whose sign is that of $\sigma_{hedge} - \sigma_{true}$. The magnitudes are consistent with the Black-Scholes premium gap $BS(\sigma_{hedge}) - BS(\sigma_{true})$ (vega ≈ 40 for an at-the-money option with $S_0 = 100$, $T = 1$). The slight asymmetry between the two values reflects the convexity of the option price in volatility. Remaining deviations from strict monotonicity come from Monte Carlo noise and discrete rebalancing.

- **Transaction costs materially erode the benefit of frequent rebalancing.** At $N=252$, adding a realistic 0.5% cost per trade turns a near break-even hedge (mean P&L ≈ 0) into a mean loss of -2.85, and even increases the P&L standard deviation — illustrating the practical trade-off between rebalancing often enough to track Delta and paying too much in trading costs to do so.

## Possible Extensions

- Bid-ask spreads modeled explicitly (rather than a flat % cost)
- Stochastic volatility models (e.g. Heston) for the underlying's true dynamics
- Local volatility or implied volatility surface calibration
- Delta-Gamma hedging with a second traded option
- Calibration and backtesting on real market data

## References

- Black, F., & Scholes, M. (1973). *The Pricing of Options and Corporate Liabilities*. Journal of Political Economy, 81(3), 637-654.
- Hull, J. C. *Options, Futures, and Other Derivatives*.
