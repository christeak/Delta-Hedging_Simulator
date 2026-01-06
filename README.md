# Delta-Hedging_Simulator

Project Overview

The Delta Hedging Simulator is a quantitative finance project designed to simulate, analyze, and visualize the performance of delta hedging strategies for European options within the Black–Scholes framework.

The objective of this project is to provide an educational and practical tool to understand how dynamic hedging reduces risk, how hedging errors arise, and how they depend on key parameters such as volatility, rebalancing frequency, and market conditions.

This simulator bridges theoretical option pricing and realistic trading constraints.

The objectives are to implement Black–Scholes pricing for European call and put options, compute option Greeks (Delta, Gamma, Vega), simulate the dynamic delta hedging of an option portfolio, analyze hedging errors and P&L distributions.

We also study the impact of rebalancing frequency, volatility misspecification and transaction costs.


Underlying Asset

The underlying asset price follows a Geometric Brownian Motion (GBM):

𝑑𝑆𝑡 = 𝜇𝑆𝑡 𝑑𝑡 + 𝜎𝑆𝑡 𝑑𝑊𝑡
	​
European options are priced using the Black–Scholes closed-form formulas.


The portfolio consists of a short (or long) European option, a dynamically adjusted position in the underlying asset.

At each time step, Delta is recomputed, the underlying position is rebalanced accordingly, the final hedging P&L is evaluated at maturity


Visualization :

Underlying price trajectories and Delta evolution over time

Insights & Observations

This simulator illustrates several fundamental results in quantitative finance:

Delta hedging is perfect only in continuous time : Discrete rebalancing leads to residual risk

Hedging error increases with higher volatility and lower rebalancing frequency


Possible Extensions :

- Transaction costs and bid–ask spreads
- Stochastic volatility models
- Local volatility or implied volatility surfaces
- Delta–Gamma hedging
- Real market data calibration
