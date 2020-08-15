import numpy as np
import pandas as pd
import yahoo_finance_pandas
import yfinance as yf
import datetime
from scipy import optimize as optim
from numpy import random
from scipy.stats import norm
import math
import matplotlib.pyplot as plt
from multiprocessing import pool
import optimization
import Security
import probability_tools as pt
import optimization as opt

EXCHANGE_FEE = 0.75

if __name__ == '__main__':
    ticker = 'AMD'
    op1 = Security.Option(ticker, 'call', 69, np.datetime64('2020-08-31'))
    op2 = Security.Option(ticker, 'put', 60, np.datetime64('2020-08-22'))
    amd = Security.Equity(ticker)

    P = pt.ProbabilityDistribution(lambda x: pt.basic_normal_pdf(x, center=73, std=4), (57, 89))

    portfolio = Security.Portfolio.from_securities([op1, op2, amd], r=0.1)

    opt.optimize(portfolio, P, 62, np.datetime64('2020-08-12'), np.datetime64('2020-08-20'), ticker)
