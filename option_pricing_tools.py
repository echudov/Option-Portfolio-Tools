import math
from scipy.stats import norm
import decimal


def black_scholes(strike: float, t: float, r: float, volatility: float, spot_price: float, option_type: str = 'call') -> float:
    d1 = (math.log(spot_price / strike) + (r + 0.5 * volatility ** 2) * t) / (volatility * (math.sqrt(t)))
    d2 = d1 - volatility * math.sqrt(t)
    cum = norm.cdf
    if option_type == 'call':
        return cum(d1) * spot_price - cum(d2) * strike * math.e ** (-r * t)
    else:
        return cum(-d2) * strike * math.e ** (-r * t) - cum(-d1) * spot_price


# not implemented
def binomial(strike, t, r, volatility, spot_price, option_type='call'):
    return 0

# should try to implement this and the above just for shits and giggles
# def monte_carlo(params)
