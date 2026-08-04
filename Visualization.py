import numpy as np
import matplotlib.pyplot as plt

from simulation import simulate_gbm_path, simulate_delta_hedge
from experiments import (
    monte_carlo_hedging_pnl,
    rebalancing_frequency_study,
    volatility_misspecification_study,
)

# ------------------------------
# Parameters
# ------------------------------
S0 = float(input("Enter the price of the initial underlying S0 : "))
K = float(input("Enter the strike K : "))
T = float(input("Enter the maturity T : "))
r = float(input("Enter the interest rate r : "))
mu = float(input("Enter the real-world drift mu (use the same value as r to simulate under the risk-neutral measure) : "))
sigma = float(input("Enter the true volatility sigma : "))
N = int(input("Enter the number of rebalancing steps N : "))
transaction_cost = float(input("Enter the transaction cost, as a %% of trade value : ")) / 100

rng = np.random.default_rng(42)

# ------------------------------
# 1. Single path: underlying, Delta, hedging error
# ------------------------------
S_path = simulate_gbm_path(S0, mu, sigma, T, N, rng)
result = simulate_delta_hedge(S_path, K, T, r, sigma, transaction_cost)

fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
axes[0].plot(result["S"], label="Underlying price S")
axes[0].axhline(K, color="red", linestyle="--", label="Strike")
axes[0].set_ylabel("Price")
axes[0].set_title("Delta-Hedging Simulation of a Short Call (Black-Scholes)")
axes[0].legend()

axes[1].plot(result["delta"], label="Delta", color="green")
axes[1].set_ylabel("Delta")
axes[1].legend()

axes[2].plot(result["portfolio_value"], label="Hedged portfolio value")
axes[2].plot(result["option_value"], label="Option value", linestyle="--")
axes[2].plot(result["hedging_error"], label="Hedging error (P&L)", color="red", linestyle=":")
axes[2].set_xlabel("Rebalancing step")
axes[2].set_ylabel("Value")
axes[2].legend()

plt.tight_layout()
plt.show()

# ------------------------------
# 2. Monte Carlo P&L distribution
# ------------------------------
n_paths = 2000
pnls = monte_carlo_hedging_pnl(n_paths, S0, K, T, r, mu, sigma, sigma, N, transaction_cost)

plt.figure(figsize=(10, 5))
plt.hist(pnls, bins=50, edgecolor="black")
plt.axvline(0, color="black", linewidth=0.8)
plt.xlabel("Final hedging P&L")
plt.ylabel("Frequency")
plt.title(f"Distribution of hedging P&L over {n_paths} paths (N={N} rebalancings)")
plt.grid(True)
plt.show()
print(f"Mean P&L: {pnls.mean():.4f} | Std P&L: {pnls.std():.4f}")

# ------------------------------
# 3. Rebalancing frequency study
# ------------------------------
N_list = [1, 4, 12, 52, 252]
freq_results = rebalancing_frequency_study(n_paths, S0, K, T, r, mu, sigma, N_list, transaction_cost)

plt.figure(figsize=(10, 5))
plt.plot(N_list, [freq_results[n]["std"] for n in N_list], marker="o")
plt.xscale("log")
plt.xlabel("Number of rebalancing dates (log scale)")
plt.ylabel("Std. dev. of hedging P&L")
plt.title("Hedging error vs. rebalancing frequency")
plt.grid(True)
plt.show()

# ------------------------------
# 4. Volatility misspecification study
# ------------------------------
sigma_hedge_list = [round(sigma * f, 4) for f in [0.5, 0.75, 1.0, 1.25, 1.5]]
vol_results = volatility_misspecification_study(n_paths, S0, K, T, r, mu, sigma, sigma_hedge_list, N, transaction_cost)

plt.figure(figsize=(10, 5))
plt.plot(sigma_hedge_list, [vol_results[s]["mean"] for s in sigma_hedge_list], marker="o", label="Mean P&L")
plt.axvline(sigma, color="red", linestyle="--", label="True volatility")
plt.xlabel("Hedging volatility assumption")
plt.ylabel("Mean hedging P&L")
plt.title("Impact of volatility misspecification on hedging P&L")
plt.legend()
plt.grid(True)
plt.show()
