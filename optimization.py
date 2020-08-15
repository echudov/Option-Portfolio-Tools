import Security
import yahoo_finance_pandas
import scipy.optimize as optim
from numpy import random
from multiprocessing import Pool
import time

def roi(weight_strike_expiry, P, price_today, today, later, volatility, r, types, ticker):
    """
    Calculates the return on investment (profit / cost) for a specific portfolio in the weight, strike, expiry form
    :param weight_strike_expiry: list of weights, strikes, and expiries that define an options portfolio
    :param P: Probability distribution to evaluate the value against
    :param price_today: today's equity price
    :param today: float value describing the relative position for today (likely 0)
    :param later: float/integer value describing the relative position (to today) for
                    when the probability distribution holds
    :param volatility: volatility of the underlying stock (implied volatility)
    :param r: risk-free interest rate
    :param types: list describing the types of securities contained in weight_strike_expiry
    :param ticker: ticker found on exchanges
    :return: float for roi percentage
    """
    value = 0
    cost = 0
    pos = 0
    for sec_type in types:
        if sec_type == 'call' or sec_type == 'put':
            # value of option at time t
            weight = weight_strike_expiry[pos]
            strike = weight_strike_expiry[pos + 1]
            expiry = weight_strike_expiry[pos + 2]
            pos += 3
            security = Security.Option(ticker, sec_type, strike, expiry)
        else:
            weight = weight_strike_expiry[pos]
            security = Security.Equity(ticker)
            pos += 1

        # value later
        value += weight * security.prob_weighted_val(P, later, r=r, sigma=volatility, model='black')
        # price now
        cost += weight * security.value(price_today, today, r=r, sigma=volatility, model='black')

    return (value - cost) / cost


def print_wse(wt_strike_expiry, types, ticker):
    """
    Prints the portfolio in a nice looking format
    :param wt_strike_expiry: list of weights, strikes, and expiries that define an options portfolio
    :param types: list describing the types of securities contained in weight_strike_expiry
    :param ticker: ticker found on exchanges
    """
    pos = 0
    for t in types:
        if t == 'put' or t == 'call':
            print("Type: " + str(t) + "; Strike: " + str(wt_strike_expiry[pos + 1]) + "; Expiry: " + str(
                wt_strike_expiry[pos + 2]) + "; Weight: " + str(wt_strike_expiry[pos]))
            pos += 3
        else:
            print(
                "Type: " + ticker + "; Weight: " + str(wt_strike_expiry[pos]))
            pos += 1

    print("-------------------------------------------------------------------------------------------")


def avg_volatility(date, df):
    """
    Finds the average volatility from a yahoo_finance_pandas dataframe at/around the specific date
    :param date: np.datetime64 date
    :param df: yahoo_finance_pandas dataframe (calls or puts)
    :return: float representing the average volatility
    """
    return df.loc[(df['expiration'] >= date - 2) & (df['expiration'] <= date + 2)]['impliedVolatility'].mean()


def optimize(portfolio, P, current_price, today, later, ticker, puts_calls=None):
    if puts_calls is None:
        puts_calls = yahoo_finance_pandas.get_option_chains(ticker=ticker)
    puts, calls = puts_calls
    vol = (avg_volatility(later, puts) + avg_volatility(later, calls)) / 2
    params, types = portfolio.serialize(today)
    later = (later - today).astype(int)  # converting np.datetime difference to an integer of days

    bounds = []
    for sec_type in types:
        if sec_type == 'call' or sec_type == 'put':
            bounds.append((-1, 1))
            bounds.append((0.1 * current_price, 10 * current_price))
            bounds.append((later, 20 * later))
        else:
            bounds.append((0, 1))

    def value_func(wt_strike_expiry):
        print_wse(wt_strike_expiry, types, ticker)
        return 0 - roi(wt_strike_expiry, P, current_price, 0, later, vol, portfolio.r, types, ticker)

    optimal = optim.minimize(value_func, x0=params, bounds=bounds, options={'disp': True}, tol=0.001)
    optimal_params = optimal.x
    best_portfolio = Security.Portfolio.from_serialization(optimal_params, types, r=portfolio.r, ticker=ticker)
    return best_portfolio


def multiprocessed_optimization(types, P, current_price, today, later, ticker, r, processes=8, random_attempts=20):
    # creating random portfolios with given security types
    puts_calls = yahoo_finance_pandas.get_option_chains(ticker=ticker)
    portfolios = []
    time_from_later = (later - today).astype(int)
    for attempt in range(random_attempts):
        securities = []
        for security_type in types:
            strike = random.uniform(low=P.domain[0], high=P.domain[1])
