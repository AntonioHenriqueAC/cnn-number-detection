import pickle
import time
import constants
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Dense, Dropout, Activation, Flatten
from tensorflow.python.keras.layers import Conv2D, MaxPooling2D
from tensorflow.python.keras.optimizers import Adam
from tensorflow.python.framework.graph_util import convert_variables_to_constants
from tensorflow.python.keras.callbacks import TensorBoard


class Trainer:

    def __init__(self):
        self.model = None
        # specify learning rate for optimizer
        self.optimizer = Adam(lr=1e-3)
        # to start tensorboard run: tensorboard --logdir=logs/, in working directory
        self.tensorboard = None

        pickle_in = open("../X.pickle", "rb")
        X = pickle.load(pickle_in)
        # scale the raw pixel intensities to the range [0, 1]
        X = X / 255

        pickle_in = open("../y.pickle", "rb")
        y = pickle.load(pickle_in)

        # train test split
        (self.trainX, self.testX, self.trainY, self.testY) = train_test_split(X, y,
                                                          test_size=constants.VALIDATION_SPLIT,
                                                          random_state=42)
        self.lb = LabelBinarizer()
        self.trainY = self.lb.fit_transform(self.trainY)
        self.testY = self.lb.transform(self.testY)

    def create_gnet_model_deep(self, name_postfix):
        # give the model a name for tensorboard
        model_name = 'CNN-number-detection-deepnet-{}'.format(name_postfix)
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(model_name))

        print('[INFO] creating model: ', model_name)

        # create model
        self.model = Sequential()

        # add model layers
        # 1. Layer
        self.model.add(Conv2D(filters=16, kernel_size=3, strides=1, padding='same',
                              input_shape=(constants.IMG_SIZE, constants.IMG_SIZE, constants.DIMENSION)))
        self.model.add(Activation(activation='relu'))
        self.model.add(MaxPooling2D(pool_size=3, padding='same'))

        # 2. Layer
        self.model.add(Conv2D(filters=32, kernel_size=3, strides=1, padding='same'))
        self.model.add(Activation(activation='relu'))
        self.model.add(MaxPooling2D(pool_size=3, padding='same'))

        # 3. Layer
        self.model.add(Conv2D(filters=64, kernel_size=3, strides=1, padding='same'))
        self.model.add(Activation(activation='relu'))
        self.model.add(MaxPooling2D(pool_size=3, padding='same'))

        self.model.add(Dropout(rate=0.25))
        self.model.add(Flatten())
        self.model.add(Dense(128, activation='relu'))

        self.model.add(Dropout(rate=0.5))
        self.model.add(Dense(len(constants.CATEGORIES), activation='softmax'))

        self.model.compile(loss='categorical_crossentropy',
                      optimizer=self.optimizer,
                      metrics=['accuracy'])

        # display summary of the created model
        self.model.summary()

    def create_gnet_model_light(self, name_postfix):
        # give the model a name for tensorboard
        model_name = 'CNN-number-detection-lightnet-{}'.format(name_postfix)
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(model_name))

        print('[INFO] creating model: ', model_name)

        # create model
        self.model = Sequential()

        # add model layers
        self.model.add(Conv2D(16, kernel_size=3, input_shape=(constants.IMG_SIZE, constants.IMG_SIZE, constants.DIMENSION)))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))

        self.model.add(Conv2D(32, kernel_size=3))
        self.model.add(Activation('relu'))
        self.model.add(MaxPooling2D(pool_size=(2, 2)))

        self.model.add(Dropout(rate=0.5))
        self.model.add(Flatten())

        self.model.add(Dense(len(constants.CATEGORIES)))
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy',
                           optimizer=self.optimizer,
                           metrics=['accuracy'])

        # display summary of the created model
        self.model.summary()

    def create_gnet_model_light_v2(self):
        # give the model a name for tensorboard
        model_name = 'CNN-number-detection-lightnet-v2'
        self.tensorboard = TensorBoard(log_dir="logs/{}".format(model_name))

        print('[INFO] creating model: ', model_name)

        # create model
        self.model = Sequential()

        # add model layers
        self.model.add(Conv2D(16, kernel_size=3,
                              strides=(2, 2),
                              input_shape=(constants.IMG_SIZE, constants.IMG_SIZE, constants.DIMENSION)))
        self.model.add(Activation('relu'))

        self.model.add(Conv2D(32, kernel_size=3, strides=(2, 2)))
        self.model.add(Activation('relu'))

        self.model.add(Dropout(rate=0.5))
        self.model.add(Flatten())

        self.model.add(Dense(len(constants.CATEGORIES)))
        self.model.add(Activation('softmax'))

        self.model.compile(loss='categorical_crossentropy',
                           optimizer=self.optimizer,
                           metrics=['accuracy'])

        # display summary of the created model
        self.model.summary()

    def create_various_models(self):
        dense_layers = [0, 1, 2]
        layer_sizes = [16, 32, 64]
        conv_layers = [1, 2, 3]

        for dense_layer in dense_layers:
            for layer_size in layer_sizes:
                for conv_layer in conv_layers:
                    model_name = "{}-conv-{}-nodes-{}-dense-{}".format(conv_layer, layer_size, dense_layer, int(time.time()))
                    print('[INFO] creating model: ', model_name)

                    # create model
                    model = Sequential()

                    # add model layers
                    model.add(Conv2D(layer_size,
                                     kernel_size=3,
                                     input_shape=(constants.IMG_SIZE, constants.IMG_SIZE, constants.DIMENSION)))
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

                    model.add(Dense(len(constants.CATEGORIES)))
                    model.add(Activation('softmax'))

                    tensorboard = TensorBoard(log_dir="logs/{}".format(model_name))

                    model.compile(loss='categorical_crossentropy',
                                  optimizer=self.optimizer,
                                  metrics=['accuracy'],)

                    model.fit(self.trainX, self.trainY,
                              validation_data=(self.testX, self.testY),
                              batch_size=constants.BATCH_SIZE,
                              epochs=constants.EPOCHS,
                              callbacks=[tensorboard])

    def fit_model(self):
        print('[INFO] training model')
        self.model.fit(self.trainX, self.trainY,
                       validation_data=(self.testX, self.testY),
                       batch_size=constants.BATCH_SIZE,
                       epochs=constants.EPOCHS,
                       callbacks=[self.tensorboard])

        print("[INFO] evaluating network")
        predictions = self.model.predict(self.testX, batch_size=32)
        print(classification_report(self.testY.argmax(axis=1),
                                    predictions.argmax(axis=1), target_names=self.lb.classes_))

    def save_model(self):
        print('[INFO] saving model')
        model_path = "{}.h5".format(constants.MODEL_DIR)
        self.model.save(model_path)
        print('[INFO] successfully saved model to: ', model_path)

    def convert_model_tensorflow(self):
        print('[INFO] saving model for tensorflow')
        model_output_path = '{}.pb'.format(constants.MODEL_DIR)
        output_path_array = model_output_path.split('/')
        output_path = ''
        output_name = ''

        for index, path in enumerate(output_path_array):
            if index != len(output_path_array) - 1:
                output_path = '{}{}/'.format(output_path, path)
            else:
                output_name = path

        keras.backend.set_learning_phase(0)
        model_input_path = "{}.h5".format(constants.MODEL_DIR)
        model = keras.models.load_model(model_input_path)

        frozen_graph = self.__convert_keras_to_tensorflow(keras.backend.get_session(),
                                                          output_names=[out.op.name for out in model.outputs])
        tf.train.write_graph(keras.backend.get_session().graph_def, output_path, "graph.pbtxt", as_text=True)
        tf.train.write_graph(frozen_graph, output_path, output_name, as_text=False)
        print('[INFO] successfully saved model to: ', model_output_path)

    def __convert_keras_to_tensorflow(self, session, keep_var_names=None, output_names=None, clear_devices=True):
        graph = session.graph
        with graph.as_default():
            freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
            output_names = output_names or []
            output_names += [v.op.name for v in tf.global_variables()]
            input_graph_def = graph.as_graph_def()
            if clear_devices:
                for node in input_graph_def.node:
                    node.device = ""
            frozen_graph = convert_variables_to_constants(session, input_graph_def, output_names, freeze_var_names)
            return frozen_graph
