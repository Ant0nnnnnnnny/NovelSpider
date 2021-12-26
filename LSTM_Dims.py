import pandas as pd
import tensorflow as tf
from keras.layers import LSTM
from keras.layers import Dropout
from keras.models import Sequential
from pandas.core.frame import DataFrame
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Dense
import numpy as np
from keras.models import load_model
import matplotlib.pyplot as plt
from sklearn import preprocessing

class LSTMModel:

    # 输入的数据
    __row_data = None
    # 输入数据的维度
    __input_dim = 1
    # 输出数据的维度
    __output_dim = 1
    # 转化之后的参数数据
    __reframed_data = None

    # 模型
    __model = None
    # 输入的步长
    __time_steps = 1
    # 训练集
    __train_X, __train_Y = [], []
    # 测试集
    __test_X, __test_Y = [], []
    # 归一化变量
    __scaler_fit = None

    def __init__(self, data,output_dim = 1) -> None:
        '''
        初始化LSTM神经网络
        --------
        在本神经网络中，第一列的默认为需要预测的数据。

         data:  DataFrame格式的数据
         output_dim:  输出数据的维度
        例子
        --------

            一维:
                >>> data = pd.read_csv('row_data.csv')
                >>> my_lstm = lstm_model(data['price'],1)
                >>> lstm.build(time_steps=3,units=50)
                >>> lstm.train(epochs=150,batch_size=40,verbose=2,loss_print=True,save=False)
                其中，price即为要预测的数据.
            多维:
                >>> data = pd.read_csv('row_data.csv')
                >>> my_lstm = lstm_model(data[['price','max','min','percent']])
                >>> lstm.build(time_steps=3,units=200)
                >>> lstm.train(epochs=150,batch_size=72,verbose=2,loss_print=True,save=False)
                在上述程序中，会使用price, max, min, percent来预测price的值
        '''
        self.__row_data = data
        self.__input_dim = data.shape[1]
        self.__output_dim = output_dim

    def __series_to_supervised(self):

        n_vars = 1 if type(self.__row_data) is list else self.__row_data.shape[1]
        df = pd.DataFrame(self.__row_data)
        cols, names = list(), list()
        # 输入步长(t-n, ... t-1)
        for i in range(self.__time_steps-1, 0, -1):
            cols.append(df.shift(i))
            names += [('var%d(t-%d)' % (j+1, i)) for j in range(n_vars)]
        cols.append(df.shift(-1))
        names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
        for i in range(0, self.__output_dim):
            cols.append(df.shift(-i))
            if i == 0:
                names += [('var%d(t)' % (j+1)) for j in range(n_vars)]
            else:
                names += [('var%d(t+%d)' % (j+1, i)) for j in range(n_vars)]
        # 聚合
        agg = pd.concat(cols, axis=1)
        agg.columns = names
        # 去除空值
        agg.dropna(inplace=True)
        print(agg)
        return agg

    def __transmit(self):
        self.__train_X = []
        self.__train_Y = []
        self.__test_X = []
        self.__test_Y = []
        
        percent = round(self.__reframed_data.shape[0]*0.8)
        train_set = self.__reframed_data.values[:percent, :]
        test_set = self.__reframed_data.values[percent:, :]

        for j in range(train_set.shape[0]):
            temp = []
            for i in range(0, train_set.shape[1]-self.__output_dim, self.__input_dim):
                temp.append((train_set[j][i:i+self.__input_dim]))
            self.__train_X.append(temp)

        self.__train_Y = self.__reframed_data.values[:percent,
                                                 :][:, -self.__input_dim]

        for j in range(test_set.shape[0]):
            temp = []
            for i in range(0, test_set.shape[1]-self.__output_dim, self.__input_dim):
                temp.append((test_set[j][i:i+self.__input_dim]))
            self.__test_X.append(temp)

        self.__test_Y = self.__reframed_data.values[percent:,
                                                :][:, -self.__input_dim]
        self.__train_X = np.array(self.__train_X)     
        self.__test_X = np.array(self.__test_X)  


    def __scaler(self):
        values = self.__row_data.values
        encoder = preprocessing.LabelEncoder()
        values[:, len(self.__row_data.columns) -
               1] = encoder.fit_transform(values[:, len(self.__row_data.columns)-1])
        values = values.astype('float32')
        self.__scaler_fit = MinMaxScaler(feature_range=(0, 1))
        self.__row_data = self.__scaler_fit.fit_transform(values)

    def build(self,time_steps = 1, units=10, loss='mae', optimizer='adam',dropout_pram = 0.7):

        self.__time_steps = time_steps
        self.__scaler()
        self.__reframed_data = self.__series_to_supervised()

        self.__transmit()
        self.__model = Sequential()
        self.__model.add(tf.compat.v1.keras.layers.CuDNNLSTM(units, input_shape=(self.__train_X.shape[1], self.__train_X.shape[2])))
        self.__model.add(Dropout(dropout_pram))
        self.__model.add(Dense(self.__output_dim))
        self.__model.compile(loss=loss, optimizer=optimizer)

    def train(self,epochs = 100,batch_size = 20,verbose = 2,loss_print = True,save = True,path = 'model/model.h5'):
        '''
        训练模型.
        epochs: 训练迭代次数
        batch_size: 最小批次梯度下降数量
        verbose: 日志打印模式
        loss_print: 是否绘制train_loss与test_loss
        save: 是否保存模型至本地
        path: 保存路径
        '''
        print(self.__train_X)
        history = self.__model.fit(self.__train_X, self.__train_Y, epochs=epochs, batch_size=batch_size, validation_data=(self.__test_X, self.__test_Y), verbose=verbose, shuffle=False)
        if loss_print:
            plt.plot(history.history['loss'], label='train')
            plt.plot(history.history['val_loss'], label='test')
            plt.legend()
            plt.show()
        if save:
            self.__model.save(path)
    def predict(self,data,future_time = 1) -> DataFrame:
        
        scaler = MinMaxScaler(feature_range=(0, 1))
        x_scaler = MinMaxScaler(feature_range=(0,1))
        x_scaler.fit_transform(np.array(data.iloc[:,0]).reshape(-1,1))
        data = scaler.fit_transform(data)
        predict_results = None
        input_data = []
        for j in range(0,data.shape[0]-self.__time_steps):
            input_data.append(data[j:j+self.__time_steps][:].tolist())
        input_data = np.array(input_data)
        input_data = input_data.reshape(input_data.shape[0], self.__time_steps, self.__input_dim)
        print(np.array([input_data]))
        temp = self.__model.predict(np.array([input_data[-1]])).reshape(-1, 1)
        predict_results = x_scaler.inverse_transform(temp)
        if future_time!=1:
            if self.__output_dim!= self.__input_dim:
                print('输入维度与输出维度不一致情况下, 只能进行单步预测. ')
            else:
                for i in range(0,future_time-1):
                    data = np.append(data, temp)
                    input_data = []
                    for j in range(0,data.shape[0]-self.__time_steps):
                        input_data.append(data[j:j+self.__time_steps][:].tolist())
                    input_data = np.array(input_data)
                    input_data = input_data.reshape(input_data.shape[0], self.__time_steps, self.__input_dim)
                    temp = self.__model.predict(np.array([input_data[-1]])).reshape(-1, 1)
                    predict_results = np.append(predict_results, x_scaler.inverse_transform(temp))
        return predict_results
           
    def load_from_storage(self,path):

        self.__model = load_model(path)

