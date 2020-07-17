import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from web.CollaborativeFiltering import CF

# ignore divide by zero or divide by NaN
np.seterr(divide='ignore', invalid='ignore')

r_cols = ['user_id', 'movie_id', 'rating', 'unix_timestamp']

rating_base = pd.read_csv('./data//ml-100k/ub.base', sep='\t', names=r_cols, encoding='latin-1')
rating_test = pd.read_csv('./data//ml-100k/ub.test', sep='\t', names=r_cols, encoding='latin-1')

rate_train = rating_base.to_numpy()
rate_test = rating_test.to_numpy()

# indices start from 0
rate_train[:, :2] -= 1
rate_test[:, :2] -= 1

# User-User CF
rs = CF(rate_train, k=30, uuCF=1)
rs.fit()

y_test = []
y_predict = []
n_tests = rate_test.shape[0]
SE = 0  # squared error
for n in range(n_tests):
    pred = rs.pred(rate_test[n, 0], rate_test[n, 1], normalized=0)
    y_predict.append(pred)
    y_test.append(rate_test[n, 2])
    SE += (pred - rate_test[n, 2]) ** 2

RMSE = np.sqrt(SE / n_tests)
print('User-user CF, RMSE =', RMSE)

_, ax = plt.subplots()

ax.scatter(x=range(0, np.array(y_test).size), y=np.array(y_test), c='blue', label='Actual', alpha=0.3)
ax.scatter(x=range(0, np.array(y_predict).size), y=np.array(y_predict), c='red', label='Predicted', alpha=0.3)
plt.title('Actual and Predicted values in User-User CF')
xlabel = "RMSE User-User CF = %s." % RMSE
plt.xlabel(xlabel)
plt.legend()
plt.savefig('./static/web/images/RMSE-User-User-CF.png')
plt.show()

# Item-item CF
rs = CF(rate_train, k=30, uuCF=0)
rs.fit()

n_tests = rate_test.shape[0]
y_test1 = []
y_pred1 = []
SE = 0  # squared error
for n in range(n_tests):
    pred = rs.pred(rate_test[n, 0], rate_test[n, 1], normalized=0)
    y_pred1.append(pred)
    y_test1.append(rate_test[n, 2])
    SE += (pred - rate_test[n, 2]) ** 2

RMSEI = np.sqrt(SE / n_tests)
print('Item-item CF, RMSE =', RMSEI)

_, ax = plt.subplots()

ax.scatter(x=range(0, np.array(y_test1).size), y=np.array(y_test1), c='blue', label='Actual', alpha=0.3)
ax.scatter(x=range(0, np.array(y_pred1).size), y=np.array(y_pred1), c='red', label='Predicted', alpha=0.3)
plt.title('Actual and Predicted values in Item-Item CF')
xlabel = "RMSE Item-Item CF = %s." % RMSEI
plt.xlabel(xlabel)
plt.legend()
plt.savefig('./static/web/images/RMSE-Item-Item-CF.png')
plt.show()
