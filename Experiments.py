import numpy as np
from simulation import simulate_gbm_path, simulate_delta_hedge


def monte_carlo_hedging_pnl(n_paths, S0, K, T, r, mu, sigma_true, sigma_hedge,
                             N, transaction_cost=0.0, seed=42):
    """Run n_paths independent simulations and return the array of final hedging P&Ls."""
    rng = np.random.default_rng(seed)
    pnls = np.zeros(n_paths)
    for i in range(n_paths):
        S_path = simulate_gbm_path(S0, mu, sigma_true, T, N, rng)
        result = simulate_delta_hedge(S_path, K, T, r, sigma_hedge, transaction_cost)
        pnls[i] = result["final_pnl"]
    return pnls


def rebalancing_frequency_study(n_paths, S0, K, T, r, mu, sigma, N_list,
                                 transaction_cost=0.0, seed=42):
    """
    Std. dev. of hedging P&L as a function of the number of rebalancing dates.
    Illustrates that hedging error shrinks as N grows (continuous-time limit).
    """
    results = {}
    for N in N_list:
        pnls = monte_carlo_hedging_pnl(n_paths, S0, K, T, r, mu, sigma, sigma,
                                        N, transaction_cost, seed)
        results[N] = {"mean": pnls.mean(), "std": pnls.std()}
    return results


def volatility_misspecification_study(n_paths, S0, K, T, r, mu, sigma_true,
                                       sigma_hedge_list, N, transaction_cost=0.0, seed=42):
    """
    Hedging P&L when the hedger's assumed volatility (sigma_hedge) differs
    from the volatility that actually drives the underlying (sigma_true).
    """
    results = {}
    for sigma_hedge in sigma_hedge_list:
        pnls = monte_carlo_hedging_pnl(n_paths, S0, K, T, r, mu, sigma_true, sigma_hedge,
                                        N, transaction_cost, seed)
        results[sigma_hedge] = {"mean": pnls.mean(), "std": pnls.std()}
    return results
