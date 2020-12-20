import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  
import random
import numpy as np
import tensorflow as tf
import cv2
from tensorflow.keras.callbacks import ModelCheckpoint
#from matplotlib import pyplot as plt
from tensorflow import Tensor
from tensorflow.keras.layers import Input, Conv2D, ReLU, BatchNormalization,\
                                    Add, AveragePooling2D, Flatten, Dense, Dropout
from tensorflow.keras.models import Model

def relu_bn(inputs: Tensor) -> Tensor:
    relu = ReLU()(inputs)
    bn = BatchNormalization()(relu)
    return bn

def residual_block(x: Tensor, downsample: bool, filters: int, kernel_size: int = 3) -> Tensor:
    y = Conv2D(kernel_size=kernel_size,
               strides= (1 if not downsample else 2),
               filters=filters,
               padding="same")(x)
    y = relu_bn(y)
    y = Dropout(0.3)(y)
    y = Conv2D(kernel_size=kernel_size,
               strides=1,
               filters=filters,
               padding="same")(y)

    if downsample:
        x = Conv2D(kernel_size=1,
                   strides=2,
                   filters=filters,
                   padding="same")(x)
    out = Add()([x, y])
    out = relu_bn(out)
    return out

def create_res_net():
    
    inputs = Input(shape=(80, 80, 3))
    num_filters = 64
    
    t = BatchNormalization()(inputs)
    t = Conv2D(kernel_size=3,
               strides=1,
               filters=num_filters,
               padding="same")(t)
    t = relu_bn(t)
    
    num_blocks_list = [2, 5, 5, 2]
    for i in range(len(num_blocks_list)):
        num_blocks = num_blocks_list[i]
        for j in range(num_blocks):
            t = residual_block(t, downsample=(j==0 and i!=0), filters=num_filters)
        num_filters *= 2
    
    t = AveragePooling2D(4)(t)
    t = Flatten()(t)
    outputs = Dense(2, activation='softmax')(t)
    
    model = Model(inputs, outputs)

    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model
   
"""
# 只使用 90% 的 GPU 記憶體
gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.9)
sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options))
tf.compat.v1.keras.backend.set_session(sess)
"""

matrix_size=80
total_data_num=11900
train_point=int(total_data_num*0.8)

X_data = np.zeros((total_data_num, matrix_size, matrix_size, 3),dtype='float16')
Y_data = np.zeros((total_data_num, 1))

x_train = np.zeros((train_point, matrix_size, matrix_size, 3),dtype='float16')
y_train = np.zeros((train_point, 1))
x_test = np.zeros(( total_data_num-train_point, matrix_size, matrix_size, 3),dtype='float16')
y_test = np.zeros(( total_data_num-train_point, 1))

for i in range(int(X_data.shape[0]/2)):
    file_name="./learning_data/routable/num"
    img = cv2.imread(file_name+str(i)+'.jpg')
    img = img.reshape(matrix_size,matrix_size,3).astype('float16')
    X_data[i]=img
    Y_data[i]=1
    
for i in range(int(X_data.shape[0]/2)):
    file_name="./learning_data/unroutable/num"
    img = cv2.imread(file_name+str(i)+'.jpg')
    img = img.reshape(matrix_size,matrix_size,3).astype('float16')
    X_data[i+int(X_data.shape[0]/2)]=img
    Y_data[i+int(X_data.shape[0]/2)]=0

for _ in range(total_data_num):
    num_a=random.randint(0,X_data.shape[0]-1)
    num_b=random.randint(0,X_data.shape[0]-1)
    if num_a!=num_b:
        X_data[num_a],X_data[num_b]=X_data[num_b],X_data[num_a]
        Y_data[num_a],Y_data[num_b]=Y_data[num_b],Y_data[num_a]

x_train=X_data[:train_point]
y_train=Y_data[:train_point]
x_test=X_data[train_point:]
y_test=Y_data[train_point:]

#model = create_res_net()
model = tf.keras.models.load_model('./pre_train_ResNet_model.h5')
#model.summary()

checkpoint_filepath = 'weights.best.hdf5'
model_checkpoint_callback = ModelCheckpoint(filepath=checkpoint_filepath, monitor='val_accuracy', verbose=1, save_best_only=True)

# 載入最近的檢查點的權重
model.load_weights(checkpoint_filepath)

"""
train_history = model.fit(
    x=x_train, y=y_train,
    epochs=3, verbose=1, validation_data=(x_test, y_test),
    batch_size=128, callbacks=[model_checkpoint_callback]
)
model.save('./pre_train_ResNet_model.h5')
"""

"""
scores = model.evaluate(X_data, Y_data, verbose=0)
print("")
print("[Info] Accuracy of testing data = {:2.1f}%".format(scores[1]*100.0))
"""

prob = model.predict(x_train[0:10])

print(prob[0:10])
print(Y_data[0:10])

print(x_train[0])

"""
# 折線圖
plt.plot(train_history.history['accuracy'])
plt.plot(train_history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Test'], loc='upper left')
plt.savefig('./accuracy_'+datetime.datetime.now().strftime("%m-%d-%H-%M")+'.png')
"""
