import pandas as pd
import statsmodels.api as sm

dayofyear =   [  1,    2,    3,    4,    5,    6,    7,    8,    9,   10,   11,   12,   13,   14,   15,   16,   17,   18,   19,   20,   21  ]
demand =      [100.1, 99.0, 99.2, 97.3, 97.9, 96.0, 94.2, 95.0, 92.0, 93.1, 91.9, 91.2, 88.0, 89.0, 89.1, 88.5, 88.4, 87.2, 87.1, 85.2, 85.3]
temperature = [ 12.3, 12.8, 12.5, 13.0, 13.2, 15.0, 15.5, 15.4, 16.4, 15.9, 17.8, 17.9, 17.7, 18.1, 17.9, 18.2, 18.7, 18.5, 18.9, 19.2, 19.5]

dependent = pd.DataFrame(data={'DayOfYear': dayofyear})
independent = pd.DataFrame(data={'Demand': demand, 'Temperature': temperature})

X = independent
y = dependent
model = sm.OLS(y, X).fit()
predictions = model.predict(X)
print(predictions)
summary = model.summary()
print(summary)