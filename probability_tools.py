import numpy as np
import math


class ProbabilityDistribution:
    def __init__(self, P, domain, mean=None, std=None):
        self.P = P
        self.domain = domain
        if mean is None:
            self.mean = self.mean()
        else:
            self.mean = mean
        if std is None:
            std = self.standard_deviation()
        else:
            self.std = std

    def mean(self, dx=0.1):
        def mean_function(x):
            return self.P(x) * x
        return riemman_sum(mean_function, self.domain, dx=dx)

    def standard_deviation(self, dx=0.1):
        def element_variance(x):
            return ((x - self.mean) ** 2) * self.P(x)

        variance = riemman_sum(element_variance, self.domain, dx=dx)
        return math.sqrt(variance)


def riemman_sum(f, domain, dx=0.05) -> float:
    return sum(f(x_i) * dx for x_i in np.arange(domain[0], domain[1], dx))


def integrate_probability(distribution, f, dx=0.05):
    def element_weighting(x):
        return distribution.P(x) * f(x)
    return riemman_sum(element_weighting, domain=distribution.domain, dx=dx)