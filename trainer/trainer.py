import pickle
import tensorflow as tf
import time
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, Activation, Flatten, InputLayer
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.keras.utils import to_categorical
from tensorflow.python.keras.callbacks import TensorBoard


class Trainer:

    def __init__(self):
        self.BATCH_SIZE = 16
        self.EPOCHS = 10
        self.VALIDATION_SPLIT = 0.3

        self.model = None
        # specify learning rate for optimizer
        self.optimizer = Adam(lr=1e-3)
        # to start tensorboard run: tensorboard --logdir=logs/, in working directory
        self.tensorboard = None

        pickle_in = open("../X.pickle", "rb")
        self.X = pickle.load(pickle_in)

        pickle_in = open("../y.pickle", "rb")
        self.y = pickle.load(pickle_in)
        # one hot encode the labels
        self.y = to_categorical(self.y)

        # first we normalize the data
        self._normalize_data()

    def set_batch_size(self, batch_size):
        self.BATCH_SIZE = batch_size

    def set_epochs(self, epochs):
        self.EPOCHS = epochs

    def set_validation_split(self, validation_split):
        self.VALIDATION_SPLIT = validation_split

    def _normalize_data(self):
        self.X = self.X / 255

    def create_model_deep(self):
        # give the model a name for tensorboard
        NAME = 'CNN-number-detection-deepnet'
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))

        print('[INFO] creating model: ', NAME)

        # create model
        self.model = Sequential()

        # add model layers
        # 1. Layer
        self.model.add(InputLayer(input_shape=[28, 28, 3])) # 3 because it is rgb, if gray: 1
        self.model.add(Conv2D(filters=32, kernel_size=3, strides=1, padding='same'))
        self.model.add(Activation(activation='relu'))
        self.model.add(MaxPooling2D(pool_size=3, padding='same'))

        # 2. Layer
        self.model.add(Conv2D(filters=50, kernel_size=3, strides=1, padding='same'))
        self.model.add(Activation(activation='relu'))
        self.model.add(MaxPooling2D(pool_size=3, padding='same'))

        # 3. Layer
        self.model.add(Conv2D(filters=80, kernel_size=3, strides=1, padding='same'))
        self.model.add(Activation(activation='relu'))
        self.model.add(MaxPooling2D(pool_size=3, padding='same'))

        self.model.add(Dropout(rate=0.25))
        self.model.add(Flatten())
        self.model.add(Dense(512, activation='relu'))
        self.model.add(Dropout(rate=0.5))
        self.model.add(Dense(11, activation='softmax'))

        self.model.compile(loss='categorical_crossentropy',
                      optimizer=self.optimizer,
                      metrics=['accuracy'])

        # display summary of the created model
        self.model.summary()

    def create_model_light(self):
        # give the model a name for tensorboard
        NAME = 'CNN-number-detection-lightnet'
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))

        print('[INFO] creating model: ', NAME)

        # create model
        self.model = Sequential()

        # add model layers
        self.model.add(Conv2D(64, kernel_size=3, input_shape=(28, 28, 3)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))

        self.model.add(Conv2D(64, kernel_size=3))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))

        self.model.add(Flatten())
        self.model.add(Dense(64))
        self.model.add(Activation('relu'))

        self.model.add(Dense(11))
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy',
                           optimizer=self.optimizer,
                           metrics=['accuracy'])

        # display summary of the created model
        self.model.summary()

    def create_various_models(self):
        dense_layers = [0, 1, 2]
        layer_sizes = [32, 64, 128]
        conv_layers = [1, 2, 3]

        for dense_layer in dense_layers:
            for layer_size in layer_sizes:
                for conv_layer in conv_layers:
                    NAME = "{}-conv-{}-nodes-{}-dense-{}".format(conv_layer, layer_size, dense_layer, int(time.time()))
                    print('[INFO] creating model: ', NAME)

                    # create model
                    model = Sequential()

                    # add model layers
                    model.add(Conv2D(layer_size, kernel_size=3, input_shape=(28, 28, 3)))
                    model.add(Activation('relu'))
                    model.add(MaxPooling2D(pool_size=(2, 2)))

                    for l in range(conv_layer - 1):
                        model.add(Conv2D(layer_size, kernel_size=3))
                        model.add(Activation('relu'))
                        model.add(MaxPooling2D(pool_size=(2, 2)))

                    model.add(Flatten())

                    for _ in range(dense_layer):
                        model.add(Dense(layer_size))
                        model.add(Activation('relu'))

                    model.add(Dense(11))
                    model.add(Activation('softmax'))

                    tensorboard = TensorBoard(log_dir="logs/{}".format(NAME))

                    model.compile(loss='categorical_crossentropy',
                                  optimizer=self.optimizer,
                                  metrics=['accuracy'],)

                    model.fit(self.X, self.y,
                              batch_size=self.BATCH_SIZE,
                              epochs=self.EPOCHS,
                              validation_split=self.VALIDATION_SPLIT,
                              callbacks=[tensorboard])

    def fit_model(self):
        print('[INFO] training model')

        self.model.fit(self.X, self.y,
                       batch_size=self.BATCH_SIZE,
                       epochs=self.EPOCHS,
                       validation_split=self.VALIDATION_SPLIT,
                       callbacks=[self.tensorboard])

    def save_model(self):
        print('[INFO] saving model')

        model_path = "../number_detection_model.h5"
        tf.keras.models.save_model(
            self.model,
            model_path,
            overwrite=True,
            include_optimizer=True)

        print('[INFO] successfully saved model to: ', model_path)