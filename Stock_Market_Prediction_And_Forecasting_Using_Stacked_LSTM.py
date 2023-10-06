#!/usr/bin/env python
# coding: utf-8

# #Data set:  
# //raw.githubusercontent.com/mwitiderrick/stockprice/master/NSE-TATAGLOBAL.csv
# 

# In[ ]:


#Import necessary Libraries
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import tensorflow as tf
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense
from tensorflow.python.keras.layers import LSTM
get_ipython().run_line_magic('matplotlib', 'inline')


# In[ ]:


#checking my tensorflow versio 
tf.__version_ 


# In[ ]:


#Import the data and remove rows containing NAN values
df = pd.read_csv('https://raw.githubusercontent.com/mwitiderrick/stockprice/master/NSE-TATAGLOBAL.csv')
df=df. iloc[::-1]
df.head()



# In[ ]:


df.tail()


# In[ ]:


#Data Preprocessing
df.isnull().sum()


# In[ ]:


df.shape


# In[ ]:


df_high=df.reset_index()['High']
plt.plot(df_high)


# In[ ]:


#Since LSTM are sensitive to the scale of the data, so we apply MinMax Scaler to transform our values between 0 and 1

scaler = MinMaxScaler(feature_range = (0,1))
df_high = scaler.fit_transform(np.array(df_high).reshape(-1,1))


# In[ ]:


df_high.shape


# In[ ]:


df_high


# In[ ]:


#Split the data into train and test split
training_size = int(len(df_high) * 0.75)
test_size = len(df_high) - training_size
train_data, test_data = df_high[0:training_size,:], df_high[training_size:len(df_high),:1]


# In[ ]:


training_size,test_size


# In[ ]:


def create_dataset(dataset, time_step = 1):
    dataX, dataY = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i+time_step), 0]
        dataX.append(a)
        dataY.append(dataset[i+time_step, 0])
    return np.array(dataX), np.array(dataY)

    
time_step = 100
x_train, y_train = create_dataset(train_data, time_step)
x_test, y_test = create_dataset(test_data, time_step)


# In[ ]:


#Reshape the input to be [samples, time steps, features] which is the requirement of LSTM
x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 1)
x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], 1)


print(x_train.shape), print(y_train.shape)


# In[ ]:


print(x_test.shape), print(y_test.shape)


# In[ ]:


#Create the LSTM Model
model = Sequential()
model.add(LSTM(50, return_sequences = True, input_shape = (100,1)))
model.add(LSTM(50, return_sequences = True))
model.add(LSTM(50))
model.add(Dense(1))
model.compile(loss = 'mean_squared_error', optimizer = 'adam')


model.summary()


# In[ ]:


model.fit(x_train, y_train, validation_data = (x_test, y_test), epochs = 100, batch_size = 64, verbose = 1)


# In[ ]:


#Lets predict and check performance metrics
train_predict = model.predict(x_train)
test_predict = model.predict(x_test)


# In[ ]:


#Transform back to original form
train_predict = scaler.inverse_transform(train_predict)
test_predict = scaler.inverse_transform(test_predict)


# In[ ]:


#Calculate RMSE performance metrics
math.sqrt(mean_squared_error(y_train, train_predict))


# In[ ]:


#Test Data RMSE
math.sqrt(mean_squared_error(y_test, test_predict))


# In[ ]:


#Plotting

#Shift train prediction for plotting
look_back = 100
trainPredictPlot = np.empty_like(df_high)
trainPredictPlot[:,:] = np.nan
trainPredictPlot[look_back:len(train_predict) + look_back, :] = train_predict

#Shift test prediction for plotting
testPredictPlot = np.empty_like(df_high)
testPredictPlot[:,:] = np.nan
testPredictPlot[len(train_predict) + (look_back * 2)+1:len(df_high) - 1, :] = test_predict

#Plot baseline and predictions
plt.plot(scaler.inverse_transform(df_high))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.show()

print("Green indicates the Predicted Data")
print("Blue indicates the Complete Data")
print("Orange indicates the Train Data")


# In[ ]:


#Predict the next 28 days Stock Price
len(test_data), x_test.shape


# In[ ]:


x_input = test_data[409:].reshape(1,-1)
x_input.shape


# In[ ]:


temp_input = list(x_input)
temp_input = temp_input[0].tolist()

lst_output=[]
n_steps=100
nextNumberOfDays = 28
i=0

while(i<nextNumberOfDays):
    
    if(len(temp_input)>100):
        x_input=np.array(temp_input[1:])
        print("{} day input {}".format(i,x_input))
        x_input=x_input.reshape(1,-1)
        x_input = x_input.reshape((1, n_steps, 1))
        yhat = model.predict(x_input, verbose=0)
        print("{} day output {}".format(i,yhat))
        temp_input.extend(yhat[0].tolist())
        temp_input=temp_input[1:]
        lst_output.extend(yhat.tolist())
        i=i+1
    else:
        x_input = x_input.reshape((1, n_steps,1))
        yhat = model.predict(x_input, verbose=0)
        print(yhat[0])
        temp_input.extend(yhat[0].tolist())
        print(len(temp_input))
        lst_output.extend(yhat.tolist())
        i=i+1
    

print(lst_output)


# In[ ]:


day_new = np.arange(1,101)
day_pred = np.arange(101,129)


# In[ ]:


day_new.shape


# In[ ]:


day_pred.shape


# In[ ]:


df3 = df_high.tolist()
df3.extend(lst_output)

len(df_high)


# In[ ]:


plt.plot(day_new, scaler.inverse_transform(df_high[1935:]))
plt.plot(day_pred, scaler.inverse_transform(lst_output))


# In[ ]:


df3=df_high.tolist()
df3.extend(lst_output)
plt.plot(df3[2000:])


# In[ ]:


df3=scaler.inverse_transform(df3).tolist()


# In[ ]:


plt.plot(df3)

