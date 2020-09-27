#Description: This program uses an artificial recurrent neural netowrk called
#Long Short Term Memory LSTM to predict stocks using past 60 days

import math
import pandas_datareader as web
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
from tensorflow import keras
import matplotlib.pyplot as plt
from backend.portfolioManagement import getPortfolio

plt.style.use('fivethirtyeight')

def calculate_LSTM(ticker):
    #collect the data
    tickers = getPortfolio(ticker)
    #create a new dataframe with only Close column
    data = tickers.filter(['Adj Close'])
    #Convert the Dataframe to a numpy array
    dataset = data.values
    #Get or compute the number of rows to train LSTM model on
    training_data_len = math.ceil( len(dataset) * .8 )

    #scale the data
    scalar = MinMaxScaler(feature_range=(0,1))
    scaled_data = scalar.fit_transform(dataset)

    print(scaled_data)

    #create the training data set
    #create the scaled training data set
    train_data = scaled_data[0:training_data_len , :]

    #Split the data into x_train and y_train
    x_train = []
    y_train = []

    for i in range(60, len(train_data)):
        x_train.append(train_data[i-60:i,0])
        y_train.append(train_data[i,0])
        if i<=61:
            print(x_train)
            print(y_train)
            print()

    #Convert the x_train and y_train to numpy array
    x_train, y_train = np.array(x_train), np.array(y_train)

    #Reshape the data
    print(x_train.shape)
    #x_train.shape produces number of rows and columns
    x_train= np.reshape(x_train,(x_train.shape[0], x_train.shape[1], 1))
    print(x_train.shape)

    #Build the LSTM Model
    #model = keras.models.load_model(new_model)
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))

    #compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    #train the model
    model.fit(x_train, y_train, batch_size=1, epochs=1)

    #create the testing data
    #create a new array containing scaled values from index 1543 to 2003
    test_data = scaled_data[training_data_len - 60: , :]

    #Create the data sets x_test and y_test
    x_test = []
    y_test =  dataset[training_data_len:, :]
    for i in range(60,len(test_data)):
        x_test.append(test_data[i-60:i, 0])

    #Convert the data to a numpy array
    x_test = np.array(x_test)

    #Reshape the data
    x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

    #Get the models predicted price values
    predictions = model.predict(x_test)
    predictions = scalar.inverse_transform(predictions)

    #predictions should contain the same dataset as y_test dataset based off x_test
    #Evaluate with RMSE (root mean squared error) which is Std dev of residual values
    rmse=np.sqrt(np.mean(((predictions- y_test)**2)))

    #plot the data
    train = data[:training_data_len]
    valid = data[training_data_len:]
    valid['Predictions'] = predictions

    return train, valid

#@app.route('/plotLSTMPrediction')
def lstm_prediction_build_plot(ticker):
    plot = tf.get_default_graph()
    train, valid = calculate_LSTM(ticker)

    # visualize the data
    plt.figure(figsize=(16, 6))
    plt.title('LSTM Model')
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Adj Close Price USD($)', fontsize=18)
    plt.plot(train['Adj Close'])
    plt.plot(valid[['Adj Close', 'Predictions']])
    plt.legend(['Train', 'Validation Set', 'Preditions'], loc='lower right')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return '<img src="data:image/png;base64,{}">'.format(plot_url)

def backtestLSTM():
    #Get the quote to predict 12-18 price
    apple_quote = web.DataReader('AAPL', data_source='yahoo', start='2012-01-01', end='2019-12-17')
    #Get the last 60 days close price
    new_df = apple_quote.filter(['Close'])
    last_60_days = new_df[-60:].values
    #scale the data to be values between 0-1
    last_60_days_scaled = scalar.transform(last_60_days)
    #add last 60 days to new numpy array
    X_test = []
    X_test.append((last_60_days_scaled))
    X_test.np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    #Get predicted scaled price
    pred_price = model.predict(X_test)
    pred_price = scalar.inverse_transform(pred_price)
    print(pred_price)
