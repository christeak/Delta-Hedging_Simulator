import numpy as np
from scipy.stats import norm
from bs_functions import call_price, d1, d2


def simulate_gbm_path(S0, mu, sigma, T, N, rng):
    """
    Simulate one Geometric Brownian Motion path: dS_t = mu*S_t*dt + sigma*S_t*dW_t.
    Returns an array of N+1 points (t = 0, dt, 2dt, ..., T), so that the last
    point corresponds exactly to maturity (tau = 0).
    """
    dt = T / N
    S = np.zeros(N + 1)
    S[0] = S0
    for t in range(1, N + 1):
        dW = rng.normal(0, np.sqrt(dt))
        S[t] = S[t - 1] * np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * dW)
    return S


def simulate_delta_hedge(S_path, K, T, r, sigma_hedge, transaction_cost=0.0,
                          cash0=0.0, shares0=0.0):
    """
    Replicate a short European call by dynamically delta-hedging along a given
    price path. sigma_hedge is the volatility used to compute Delta at each
    step (can differ from the volatility that actually generated S_path, to
    study misspecification).

    Unlike a naive discretization, the loop runs through i = 0..N so the
    final step corresponds to tau = 0: the hedge is unwound exactly at
    maturity against the option's real payoff.
    """
    N = len(S_path) - 1
    dt = T / N

    # Delta and option value depend only on (S_t, tau), not on the hedge
    # state, so they can be computed once, vectorized over the whole path
    # (this is far faster than calling scipy.stats.norm.cdf N times in a
    # Python loop). Only the final point (tau = 0) needs the scalar
    # exercise-boundary formulas.
    tau_array = T - np.arange(N) * dt          # strictly positive, length N
    S_array = S_path[:N]
    d1_arr = d1(S_array, K, tau_array, r, sigma_hedge)
    d2_arr = d2(S_array, K, tau_array, r, sigma_hedge)
    delta_head = norm.cdf(d1_arr)
    option_head = S_array * norm.cdf(d1_arr) - K * np.exp(-r * tau_array) * norm.cdf(d2_arr)

    final_delta = 1.0 if S_path[N] > K else 0.0
    final_option = max(S_path[N] - K, 0.0)

    delta_series = np.append(delta_head, final_delta)
    option_value = np.append(option_head, final_option)

    cash = cash0
    shares = shares0
    cash += call_price(S_path[0], K, T, r, sigma_hedge)  # premium received (short call)

    portfolio_value = np.zeros(N + 1)
    for i in range(N + 1):
        S_t = S_path[i]
        current_delta = delta_series[i]

        delta_shares = current_delta - shares
        cash -= delta_shares * S_t * (1 + transaction_cost * np.sign(delta_shares))
        shares = current_delta

        if i < N:
            cash *= np.exp(r * dt)

        portfolio_value[i] = cash + shares * S_t

    hedging_error = portfolio_value - option_value

    return {
        "S": S_path,
        "portfolio_value": portfolio_value,
        "option_value": option_value,
        "hedging_error": hedging_error,
        "delta": delta_series,
        "final_pnl": hedging_error[-1],
    }
