import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

#Initial parameters
S0 = float(input("Enter the price of the initial underlying S0 : "))       # Initial price of the asset
K = float(input("Enter the strike K : "))       # Option strike
T = float(input("Enter the maturity T : "))      # Maturity (1 year)
r = float(input("Enter the interest rate r : "))        # Risk-free rate
sigma = float(input("Enter the volatility sigma : "))   # Volatility
N = int(input("Enter the number of days N : "))         # Number of rebalancings
dt = T / N     # Timestep
transaction_cost = float(input("Enter the percentage of the price for transaction cost (%): "))/100  # Transaction cost

# ------------------------------
#Black-Scholes functions
# ------------------------------
def d1(S, K, T, r, sigma):
    return (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))

def d2(S, K, T, r, sigma):
    return (np.log(S/K) + (r - 0.5*sigma**2)*T) / (sigma*np.sqrt(T))

def call_price(S, K, T, r, sigma):
    if T <= 0:
        return max(S - K, 0)
    return S * norm.cdf(d1(S,K,T,r,sigma)) - K * np.exp(-r*T) * norm.cdf(d2(S,K,T,r,sigma))

def delta_call(S, K, T, r, sigma):
    if T <= 0:
        return 0 if S < K else 1
    return norm.cdf(d1(S, K, T, r, sigma))

# ------------------------------
# Asset Price simulation
# ------------------------------
np.random.seed(42)  
S = np.zeros(N)
S[0] = S0
for t in range(1, N):
    dW = np.random.normal(0, np.sqrt(dt))
    S[t] = S[t-1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * dW)

# ------------------------------
# Delta Hedging Simulation
# ------------------------------
cash = float(input("Enter the initial cash (normally 0): "))                  # Initial cash
shares = float(input("Enter the initial number of hold shares (normally 0) : "))               # Number of hold shares
portfolio_value = []     # Hedged portfolio value
objective_value = []

# Initialization : Selling of the option
option_initial = call_price(S[0], K, T, r, sigma)
cash += option_initial    # We gain the money

for t in range(N):
    current_S = S[t]
    tau = T - t * dt      # Remaining time     
    # Computation of the delta and the value of the option
    current_delta = delta_call(current_S, K, tau, r, sigma)
    option_value = call_price(current_S, K, tau, r, sigma)
    # Rebalancing : Hold shares
    delta_shares = current_delta - shares
    cash -= delta_shares * current_S*(1 + transaction_cost * np.sign(delta_shares))
    cash *= np.exp(r * dt)
    shares = current_delta

    # Total Portfolio Value
    portfolio_value.append(cash + shares * current_S)
    objective_value.append(cash + shares * current_S - option_value)
# ------------------------------
# Visualisation
# ------------------------------
plt.figure(figsize=(12, 6))
plt.plot(S, label="Price of the asset (S)")
plt.plot(portfolio_value, label="Value of the hedged portefolio")
plt.plot(objective_value, color='red', linestyle=':', label="(Hedged portfolio - option) value (neutral objective for initial cash and shares = 0)")
plt.title("Delta Hedging of a Call option (Black-Scholes)")
plt.xlabel("Time (days)")
plt.ylabel("Value")
plt.legend()
plt.grid(True)
plt.show()
