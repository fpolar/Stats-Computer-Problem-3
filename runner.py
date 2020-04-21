import argparse
import numpy as np
from collections import defaultdict
import json
# strategy import
from mystrategy import Strategy

VERSION = '0.1.2'

DEFAULT_OPTION_COUNT = 3
ROUND_PRECISION = 3

p = argparse.ArgumentParser('Run sampling game strategy')
# if sum(probs)>0 use the fixed value
#   note: override 'random' probabilities
# you can add arbitrary dimensions to increase the number of options, i.e. len(probs)=N
p.add_argument('--probability', dest='probs', action='store', type=float, nargs='+', default=[0]*DEFAULT_OPTION_COUNT, help='a space separated list float() parseable numbers')
p.add_argument('--trials', dest='trials', type=int, action='store', default=100, help='number of trials')
# file, load arguments probability and trial
p.add_argument('--batch', dest='batch', type=argparse.FileType('r'), action='store', help='')
args = p.parse_args()

if sum(args.probs) > 0 and args.batch:
  raise Exception('cannot define both probs and batch options at the same time')

# NOTE: some things not checked
#   train > 0
#   probs[] <= 1

class Game:
  def __init__(self, probs):
    # cleaner
    self.__probs = np.round(probs, ROUND_PRECISION)

    # extend for non-uniform rewards
    self.__rewards = [1]*len(self.__probs)

    self.__score = 0
    self.__trials = 0


  def test(self, idx):
    # force to int and check if valid index
    idx = int(idx)
    if (idx < 0) or (idx >= len(self.__probs)):
      raise Exception('test index must be between 0 and %d -- input was: %d' % (len(self.__probs), idx))

    reward = self.__rewards[idx] if (np.random.random() < self.__probs[idx]) else 0
    self.__score += reward
    return reward


    # note: expected value of max score
  def scoreMax(self):
    return self.__trials * max(self.__probs)


  def scoreExp(self):
    return self.__trials * sum(self.__probs) / len(self.__probs)


    # efficiency metric
  def efficiency(self):
    scoreMax = self.scoreMax()
    scoreExp = self.scoreExp()
    scoreStrategy = self.__score

    # note, if scoreMax = scoreExp, leads to divide by zero
    return 0 if scoreMax == scoreExp else (scoreStrategy - scoreExp) / (scoreMax - scoreExp)


  def run(self, strategy, trials):
    N = len(self.__probs)

    for k in range(0, trials):
      self.__trials += 1
      idx = strategy.select(k)
      reward = self.test(idx)
      strategy.record(reward, idx, k)

    return {
      'efficiency': self.efficiency(),
      'expscore':   self.scoreExp(),
      'maxscore':   self.scoreMax(),
      'probs':      self.__probs,
      'score':      self.__score,
      'trials':     self.__trials,
    }


results = []


def report(res):
  print('Probabilities:\t%s' % (res['probs']))
  print('N=%d, perfect: %.1f, expected: %.1f' % (res['trials'], res['maxscore'], res['expscore']))
  print('')
  print('* Strategy:\t%d points' % (res['score']))
  print('* Efficiency:\t%.3f' % (res['efficiency']))


# single run
def runOne(probs, trials):
  if (sum(probs) == 0):
    probs = np.random.random([len(probs)])
  else:
    # no peaking
    np.random.shuffle(probs)

  s = Strategy(len(probs), trials)
  q = Game(probs)
  res = q.run(s, trials)
  return res

def runN(probs, trials, N):
  tally = defaultdict(int)

  for _ in range(1,N):
    res = runOne(probs, trials)
    
    for key in ['efficiency', 'score']:
      tally[key] += res[key]

  for key in tally.keys():
    tally[key] /= N

  return tally  
  

if args.batch:
  args.batch = json.load(args.batch)

  # batch run
  for ss in args.batch:
    for trials in ss['trials']:
      tag = '%s:%d' % (ss['tag'], trials)
      res = runN(ss['probs'], trials, ss['N'])
      results.append((tag, res))

  avgEfficiency = np.mean([res['efficiency'] for (tar, res) in results])
  scores = {'Success':'1', 'Avg Efficiency': '%.2f' % (100 * avgEfficiency)}
  scoreboard = ['%.2f' % (100 * avgEfficiency)] + ['%.2f' % (100 * res['efficiency']) for (tar, res) in results]
  out = {'scores': scores, 'scoreboard': scoreboard}
  print(json.dumps(out))
else:
  res = runOne(args.probs, args.trials)
  report(res)
