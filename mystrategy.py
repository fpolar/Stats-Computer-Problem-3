# from random import random

# N options: n in {0, .., N-1}
# K trials: k in {0, .., K-1}

# dummy strategy
#  * spread first 10*N tests uniformly over options
#  * then always select option with max score (ignore tie)

import numpy as np

VERSION = '0.1.1'

class Strategy:
  # setup any variables your strategy needs
  # N: number of options
  # trial: number of trials
  def __init__(self, N, trials):
    self.N = N
    self.state = [0]*N
    self.p = [0]*N
    self.trials = trials
    self.exploreThreshold = N*10
    self.epsilon = .05
    self.epsilonDecay = .1/trials
    # print(N)
    # print(trials)


  # use your state information to select an option
  # k: current trial # (0-index)
  def select(self, k):
    # print(self.state)
    if k >= self.exploreThreshold:
      #setup probabilties
      self.p = [n/self.exploreThreshold for n in self.state]
    if k < self.exploreThreshold:
      # explore
      return int(k/10)
    else:
      # exploit
      if np.random.random() < self.epsilon:
      	return np.random.randint(self.N)
      return(self.p.index(max(self.p)))
      # return(self.state.index(max(self.state)))


  # record the reward for trial k
  # idx is your selected option (so you dont need to track within select)
  def record(self, reward, idx, k):
    self.state[idx] += reward
    self.p[idx] += reward/(k+1)
    self.epsilon -= self.epsilonDecay
