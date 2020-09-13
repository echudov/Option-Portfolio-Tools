import math
from scipy.stats import norm
import numpy as np
import decimal


def black_scholes(strike: float, t: float, r: float, volatility: float, spot_price: float, option_type: str = 'call') -> float:
    d1 = (math.log(spot_price / strike) + (r + 0.5 * volatility ** 2) * t) / (volatility * (math.sqrt(t)))
    d2 = d1 - volatility * math.sqrt(t)
    cum = norm.cdf
    if option_type == 'call':
        return cum(d1) * spot_price - cum(d2) * strike * math.e ** (-r * t)
    else:
        return cum(-d2) * strike * math.e ** (-r * t) - cum(-d1) * spot_price


# implemented but not tested yet
def binomial(strike, T, r, volatility, spot_price, N=6, option_type='call'):
    values = np.zeros((N+1, (2 * N) + 1)) # option values at iteration (n, element)
    prices = np.zeros((N+1, (2 * N) + 1)) # equity prices to evaluate the option at

    dt = T / N
    u = math.exp(volatility * math.sqrt(dt))
    d = 1 / u
    p = (math.exp(r * dt) - d)/(u - d)
    q = 1 - p
    for i in range(N + 1):
        for j in range(i + 1):
            prices[j, i] = spot_price * (u ** (i - j)) * (d ** j)

    if option_type == 'call':
        values[:, N] = np.maximum(np.zeros(N + 1), (prices[:, N] - strike))
    else:
        values[:, N] = np.maximum(np.zeros(N + 1), (strike - prices[:, N]))
    for i in reversed(range(N - 1)):
        for j in range(0, i + 1):
            values[j, i] = 1 / (1 + r) * (p * values[j, i + 1] + q * values[j + 1, i + 1])

    return values[0, 0]

# should try to implement this and the above just for shits and giggles
# def monte_carlo(params)
