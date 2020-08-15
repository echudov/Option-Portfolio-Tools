import numpy as np
from numpy import random
import option_pricing_tools as opt
import probability_tools as pt


class Security:
    def __init__(self, ticker):
        self.ticker = ticker

    def value(self, price, time, **kwargs):
        raise Exception("Not Implemented")

    def prob_weighted_val(self, P, time, **kwargs):
        return pt.integrate_probability(P, lambda p: p)

    def delta(self, price, time, accuracy=0.01):
        return (self.value(price + 0.5 * accuracy, time) - self.value(price - 0.5 * accuracy, time)) / accuracy


class Option(Security):
    def __init__(self, ticker, option_type, strike, expiry):
        Security.__init__(self, ticker)
        self.option_type = option_type
        self.strike = strike
        self.expiry = expiry

    # currently, since only black-scholes is implemented, that's all I use to value the option :/
    def value(self, price, time, **kwargs):
        r = kwargs.get("r")
        sigma = kwargs.get("sigma")
        model = kwargs.get("model")
        if time is None:
            time = (self.expiry - np.datetime64('nat')).astype(int)
        else:
            time = (self.expiry - time).astype(int)
        if model == 'black':
            return opt.black_scholes(self.strike, time, r, sigma, price, option_type=self.option_type)

    # find the expected value across a given probability distribution
    # This is incredibly expensive, and the root of most of the execution time, but there isn't much I can do
    # Since there is no way to algebraically evaluate this for an arbitrary probability distribution
    # Especially when the distribution is discreet/non approximatable by a basic function
    def prob_weighted_val(self, P, time, **kwargs):
        r = kwargs.get("r")
        sigma = kwargs.get("sigma")
        model = kwargs.get("model")
        if time is None:
            time = (self.expiry - np.datetime64('nat')).astype(int)
        else:
            time = (self.expiry - time)
        if model == 'black':
            return pt.integrate_probability(P, lambda p: opt.black_scholes(self.strike, time, r, sigma, p,
                                                                           option_type=self.option_type))


class Equity(Security):
    def __init__(self, ticker):
        Security.__init__(self, ticker)

    def value(self, price, time, **kwargs):
        return price

    def prob_weighted_val(self, P, time, **kwargs):
        return pt.integrate_probability(P, lambda p: p)

    def delta(self, price, time, accuracy=0.01):
        return accuracy


class Portfolio:
    def __init__(self, securities, types, r):
        self.r = r
        self.securities = securities
        self.types = types

    @classmethod
    def from_securities(cls, securities, r):
        assert all(isinstance(s, Security) for s in securities)
        secs = []
        types = []
        for s in securities:
            if isinstance(s, Option):
                secs.append((s, random.uniform(low=-1, high=1)))
                types.append(s.option_type)
            else:
                secs.append((s, random.uniform(low=0, high=1)))
                types.append(s.ticker)
        return cls(securities=secs, types=types, r=r)

    @classmethod
    def from_serialization(cls, serialization, types, r, ticker):
        securities = []
        pos = 0
        for sec_type in types:
            if sec_type == 'call' or sec_type == 'put':
                sec = Option(ticker, sec_type, serialization[pos + 1], serialization[pos + 2])
                securities.append((sec, serialization[pos]))
                pos += 3
            else:
                sec = Equity(ticker)
                securities.append((sec, serialization[pos]))
                pos += 1
        return cls(securities=securities, types=types, r=r)

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

    def serialize(self, date_relative_to):
        options = []
        securities = []
        types = []
        for s, w in self.securities:
            if isinstance(s, Option):
                options.append(w)
                options.append(s.strike)
                options.append((s.expiry - date_relative_to).astype(int))
                types.append(s.option_type)
            else:
                securities.append(w)
                types.append('equity')
        return options + securities, types
