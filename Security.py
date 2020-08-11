import numpy as np
from numpy import random
import option_pricing_tools as opt
import probability_tools as pt


class Security:
    def __init__(self, ticker):
        self.ticker = ticker

    def value(self, price, time, P, **kwargs):
        raise Exception("Not Implemented")

    def delta(self, price, time, accuracy=0.01):
        return (self.value(price + 0.5 * accuracy, time) - self.value(price - 0.5 * accuracy, time)) / accuracy


class Option(Security):
    def __init__(self, ticker, option_type, strike, expiry):
        Security.__init__(self, ticker)
        self.option_type = option_type
        self.strike = strike
        self.expiry = expiry

    def value(self, price, time, P, **kwargs):
        r = kwargs.get("r")
        sigma = kwargs.get("sigma")
        model = kwargs.get("model")
        if time is None:
            time = (self.expiry - np.datetime64('nat')).astype(int)
        else:
            time = (self.expiry - time).astype(int)
        if model == 'black':
            return opt.black_scholes(self.strike, time, r, sigma, price, option_type=self.option_type)

    def prob_weighted_val(self, P, time, **kwargs):
        r = kwargs.get("r")
        sigma = kwargs.get("sigma")
        model = kwargs.get("model")
        if time is None:
            time = (self.expiry - np.datetime64('nat')).astype(int)
        else:
            time = (self.expiry - time).astype(int)
        if model == 'black':
            return pt.integrate_probability(P, lambda p: opt.black_scholes(self.strike, time, r, sigma, p,
                                                                           option_type=self.option_type))


class Equity(Security):
    def __init__(self, ticker, current_price):
        Security.__init__(self, ticker)
        self.current_price = current_price

    def value(self, price, time, **kwargs):
        return price

    def delta(self, price, time, accuracy=0.01):
        return accuracy


class Portfolio:
    def __init__(self, securities, r):
        assert all(isinstance(s, Security) for s in securities)
        self.r = r
        self.securities = []
        self.types = []
        for s in securities:
            if isinstance(s, Option):
                securities.append((s, random.uniform(low=-1, high=1)))
                self.types.append(s.option_type)
            else:
                securities.append((s, random.uniform(low=0, high=1)))
                self.types.append(s.ticker)

    def value(self, P, time, implied_volatility):
        val = 0
        for security, weight in self.securities:
            val += weight * security.prob_weighted_val(P, time=time, r=self.r, sigma=implied_volatility,
                                                       model='black')
        return val

    def print_portfolio(self):
        for security, weight in self.securities:
            if isinstance(security, Option):
                print("Type: " + str(security.option_type) + "; Strike: " + str(security.strike) + "; Expiry: " + str(
                    security.expiry) + "; Weight" + str(weight))
            else:
                print(
                    "Type: " + security.ticker + "; Price: " + str(security.current_price) + "; Weight: " + str(weight))

        print("-------------------------------------------------------------------------------------------")

    @property
    def serialize(self):
        options = []
        securities = []
        for s, w in self.securities:
            if isinstance(s, Option):
                options.append(w)
                options.append(s.strike)
                options.append(s.expiry)
            else:
                securities.append(w)
                securities.append(s.ticker)
        return options + securities