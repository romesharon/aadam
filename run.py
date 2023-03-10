# example of plotting the adam search on a contour plot of the test function
from math import sqrt

import numpy as np
from matplotlib import pyplot
from numpy import arange, sign
from numpy import asarray, absolute
from numpy import meshgrid
from numpy.random import rand
from numpy.random import seed
from sklearn.neural_network._stochastic_optimizers import AdamOptimizer


class AAdamOptimizer(AdamOptimizer):
    def __init__(self, params):
        super().__init__(params)
        self.previous_update = [np.zeros_like(param) for param in params]
        self.previous_previous_update = [np.zeros_like(param) for param in params]
        self.ds = [np.zeros_like(param) for param in params]

    def _get_updates(self, grads):
        """Get the values used to update params with given gradients

        Parameters
        ----------
        grads : list, length = len(coefs_) + len(intercepts_)
            Containing gradients with respect to coefs_ and intercepts_ in MLP
            model. So length should be aligned with params

        Returns
        -------
        updates : list, length = len(grads)
            The values to add to params
        """
        self.t += 1
        self.ms = [self.beta_1 * m + (1 - self.beta_1) * grad
                   for m, grad in zip(self.ms, grads)]
        self.vs = [self.beta_2 * v + (1 - self.beta_2) * (grad ** 2)
                   for v, grad in zip(self.vs, grads)]
        self.learning_rate = (self.learning_rate_init *
                              np.sqrt(1 - self.beta_2 ** self.t) /
                              (1 - self.beta_1 ** self.t))
        self.ds = [
            absolute(prev - prev_prev) * sign(grad) * (1 - beta1)
            for prev, prev_prev, grad in zip(self.previous_update, self.previous_previous_update, grads)]
        updates = [-self.learning_rate * m * beta1 / (np.sqrt(v + self.epsilon)) + d
                   for m, v, d in zip(self.ms, self.vs, self.ds)]
        if np.all((self.previous_previous_update == 0)) and np.all((self.previous_update == 0)):
            self.previous_previous_update = updates
            self.previous_update = updates
        else:
            self.previous_previous_update = self.previous_update
            self.previous_update = updates
        return updates


# objective function
def objective(x, y):
    return x ** 2.0 + y ** 2.0


# derivative of objective function
def derivative(x, y):
    return asarray([x * 2.0, y * 2.0])


# gradient descent algorithm with adam
def aadam(objective, derivative, bounds, n_iter, alpha, beta1, beta2, eps=1e-8):
    solutions = list()
    # generate an initial point
    x = bounds[:, 0] + rand(len(bounds)) * (bounds[:, 1] - bounds[:, 0])
    x_before = x.copy()
    x_before_before = x.copy()
    r = bounds[:, 0] + rand(len(bounds)) * (bounds[:, 1] - bounds[:, 0])
    score = objective(x[0], x[1])
    # initialize first and second moments
    m = [0.0 for _ in range(bounds.shape[0])]
    v = [0.0 for _ in range(bounds.shape[0])]
    # run the gradient descent updates
    for t in range(n_iter):
        # calculate gradient g(t)
        g = derivative(x[0], x[1])
        # build a solution one variable at a time
        for i in range(bounds.shape[0]):
            # m(t) = beta1 * m(t-1) + (1 - beta1) * g(t)
            m[i] = beta1 * m[i] + (1.0 - beta1) * g[i]
            # v(t) = beta2 * v(t-1) + (1 - beta2) * g(t)^2
            v[i] = beta2 * v[i] + (1.0 - beta2) * g[i] ** 2
            # mhat(t) = m(t) / (1 - beta1(t))
            mhat = m[i] / (1.0 - beta1 ** (t + 1))
            # vhat(t) = v(t) / (1 - beta2(t))
            vhat = v[i] / (1.0 - beta2 ** (t + 1))
            d = absolute(x_before[i] - x_before_before[i]) * sign(g[i]) * (1 - beta1)
            print(d)
            # x(t) = x(t-1) - alpha * mhat(t) / (sqrt(vhat(t)) + ep)
            # x[i] = x[i] - alpha * mhat / (sqrt(vhat) + eps)
            x[i] = x[i] - (alpha * beta1 * mhat / (sqrt(vhat + eps)) + d)
        # evaluate candidate point
        score = objective(x[0], x[1])
        x_before_before = x_before
        x_before = x.copy()
        # keep track of solutions
        solutions.append(x.copy())
        # report progress
        print('>%d f(%s) = %.5f' % (t, x, score))
    return solutions


# seed the pseudo random number generator
seed(1)
# define range for input
bounds = asarray([[-1.0, 1.0], [-1.0, 1.0]])
# define the total iterations
n_iter = 10
# steps size
alpha = 0.02
# factor for average gradient
beta1 = 0.9
# factor for average squared gradient
beta2 = 0.999
# perform the gradient descent search with adam
solutions = aadam(objective, derivative, bounds, n_iter, alpha, beta1, beta2)
# sample input range uniformly at 0.1 increments
xaxis = arange(bounds[0, 0], bounds[0, 1], 0.1)
yaxis = arange(bounds[1, 0], bounds[1, 1], 0.1)
# create a mesh from the axis
x, y = meshgrid(xaxis, yaxis)
# compute targets
results = objective(x, y)
# create a filled contour plot with 50 levels and jet color scheme
pyplot.contourf(x, y, results, levels=50, cmap='jet')
# plot the sample as black circles
solutions = asarray(solutions)
pyplot.plot(solutions[:, 0], solutions[:, 1], '.-', color='w')
# show the plot
pyplot.show()
