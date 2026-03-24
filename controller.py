import cv2 
import os
import gc
import hashlib
import socket
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import mysql.connector as mssql
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow import keras
import pandas as pd
from IPython.display import display
import matplotlib.pyplot as plt
import os, sys
import random
import tqdm
import string
def getMachine_addr():
	os_type = sys.platform.lower()
	command = "wmic bios get serialnumber"
	return os.popen(command).read().replace("\n","").replace("	","").replace(" ","")

def getUUID_addr():
	os_type = sys.platform.lower()
	command = "wmic path win32_computersystemproduct get uuid"
	return os.popen(command).read().replace("\n","").replace("	","").replace(" ","")

def extract_command_result(key,string):
    substring = key
    index = string.find(substring)
    result = string[index + len(substring):]
    result = result.replace(" ","")
    result = result.replace("-","")
    return result


    

def get_ip_address_of_host():
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        mySocket.connect(('10.255.255.255', 1))
        myIPLAN = mySocket.getsockname()[0]
    except:
        myIPLAN = '127.0.0.1'
    finally:
        mySocket.close()
    return myIPLAN
def save_model():
    global model
    model= '../Model/forest_fire.h5'

    if os.path.exists(model):
        return True
    else:
        return False
def train():
    train_dir = '../Dataset'
    Name=[]
    for file in os.listdir(train_dir):
        Name+=[file]
    print(Name)
    print(len(Name))
    N=[]
    for i in range(len(Name)):
        N+=[i]
        
    mapping=dict(zip(Name,N)) 
    reverse_mapping=dict(zip(N,Name))
    dataset=[]
    testset=[]
    count=0
    for file in Name:
        t=0
        path=os.path.join(train_dir,file)
        for im in os.listdir(path):
            image=load_img(os.path.join(path,im), color_mode='rgb', target_size=(40,40))
            image=img_to_array(image)
            image=image/255.0
            if t<40:
                dataset+=[[image,count]]
            else:
                testset+=[[image,count]]
            t+=1     
        count+=1
    data,labels0=zip(*dataset)
    test,testlabels0=zip(*testset)
    labels1=to_categorical(labels0)
    labels=np.array(labels1)
    data=np.array(data)
    test=np.array(test)
    trainx,testx,trainy,testy=train_test_split(data,labels,test_size=0.2,random_state=44)
    print(trainx.shape)
    print(testx.shape)
    print(trainy.shape)
    print(testy.shape)
    datagen = ImageDataGenerator(horizontal_flip=True,vertical_flip=True,rotation_range=20,zoom_range=0.5,
                            width_shift_range=0.2,height_shift_range=0.2,shear_range=0.1,fill_mode="nearest")
    pretrained_model3 = tf.keras.applications.DenseNet201(input_shape=(40,40,3),include_top=False,weights='imagenet',pooling='avg')
    pretrained_model3.trainable = False
    inputs3 = pretrained_model3.input
    x3 = tf.keras.layers.Dense(128, activation='relu')(pretrained_model3.output)
    outputs3 = tf.keras.layers.Dense(2, activation='softmax')(x3)
    model = tf.keras.Model(inputs=inputs3, outputs=outputs3)
    model.compile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])
    history=model.fit(datagen.flow(trainx,trainy,batch_size=32),validation_data=(testx,testy),epochs=50)
    model.save('../Model/forest_fire.h5')
    input()
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('../Plots/accuracy.png')
    # summarize history for loss
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    plt.savefig('../Plots/loss.png')

def md5(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    return md5_hash.hexdigest()
def key_validate(str):
    conn = mssql.connect(
        user='root', password='root', host='localhost', database='forest'
        )
    cur = conn.cursor()
    private_key = extract_command_result("SerialNumber",getMachine_addr()) + extract_command_result("UUID",getUUID_addr())
    if private_key in str:
        cur.execute("select * from SOFTKEY where private_key = %s and public_key = %s",(md5(private_key),md5(extract_command_result(private_key,str))))
        data=cur.fetchone()
        if data:
            return True
        else:
            return False
    else:
        return False
