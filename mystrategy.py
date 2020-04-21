# from random import random

# N options: n in {0, .., N-1}
# K trials: k in {0, .., K-1}

# dummy strategy
#  * spread first 10*N tests uniformly over options
#  * then always select option with max score (ignore tie)

VERSION = '0.1.1'

class Strategy:
  # setup any variables your strategy needs
  # N: number of options
  # trial: number of trials
  def __init__(self, N, trials):
    self.N = N
    self.state = [0]*N
    self.trials = trials


  # use your state information to select an option
  # k: current trial # (0-index)
  def select(self, k):
    if k < 10 * self.N:
      # explore
      return int(k/10)
    else:
      # exploit
      return(self.state.index(max(self.state)))


  # record the reward for trial k
  # idx is your selected option (so you dont need to track within select)
  def record(self, reward, idx, k):
    self.state[idx] += reward
