import numpy as np
import pandas as pd
import dirichlet
import matplotlib.pyplot as plt



bodyshop = pd.read_csv("data/autoshop_ratings.csv", header=0)
bodyshop['total'] = bodyshop.iloc[:, 1:5].sum(axis=1)
bodyshop = bodyshop.loc[bodyshop['total'] > 0]
bodyshop['metric'] = (bodyshop['five'] * 5 + bodyshop['four'] * 4 \
                    + bodyshop['three'] * 3 + bodyshop['two'] * 2 \
                    + bodyshop['one']) / bodyshop['total']

bodyshop = bodyshop.sort_values(by='total', ascending=False)

K = 5
ITERATION = 50
a0 = np.array([100, 299, 100])
D0 = np.random.dirichlet(a0, 1000)
dirichlet.mle(D0)