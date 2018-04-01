"""
Single input LSTM to predict closing prices.
"""
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# load and clean the dataframe
f = r'data/EUR_USD_M15_history.csv'
filename = f[5:-4]
df = pd.read_csv(f)
df.drop(["Unnamed: 0", "Open", "High", "Low", "Volume"], axis=1, inplace=True)
series = df.values.astype("float")

def singleInputModel(dataset, layers, filename):
    # normalize the dataset
    scaler = MinMaxScaler(feature_range=(0,1))
    dataset = scaler.fit_transform(dataset)

    # convert an arry of values into a dataset matrix
    # X = closing price at time (t)
    # y = closign prices at future time (t+1)
    def create_matrix(dataset):
        X, y = list(), list()
        for t in range(len(dataset)-1):
            X.append(dataset[t])
            y.append(dataset[t+1])
        return np.asarray(X), np.asarray(y)

    # split the data
    X, y = create_matrix(dataset)
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8)
    # reshape inputs (X_train/test) to [samples, timesteps, n_features]
    X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
    X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(layers, input_shape=(1,1,)))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X_train, y_train, epochs=5, batch_size=1, verbose=2)
    #model.save('singleInputModel.hdf5')
    #model = load_model('/singleInputModel')

    # make predictions
    predict_train = model.predict(X_train)
    predict_test = model.predict(X_test)

    # de-normalize data for human consumption
    predict_train = scaler.inverse_transform(predict_train)
    predict_test = scaler.inverse_transform(predict_test)
    y_train = scaler.inverse_transform(y_train)
    y_test = scaler.inverse_transform(y_test)

    # calculate root mean squared error
    trainScore = math.sqrt(mean_squared_error(y_train[:,0], predict_train[:,0]))
    #print("Training score: %.2f RMSE" % trainScore)
    testScore = math.sqrt(mean_squared_error(y_test[:,0], predict_test[:,0]))
    print("Test score: %.2f RMSE" % testScore)

    plt.plot(predict_test, label="predicted values")
    plt.plot(y_test, label="actual values")
    plt.legend()
    plt.savefig('examples/lstm1-%s' % filename)
    plt.show()

model = singleInputModel(series, 4, filename)
