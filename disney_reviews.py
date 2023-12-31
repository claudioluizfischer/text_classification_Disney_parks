# -*- coding: utf-8 -*-
"""Disney_reviews.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vVGBfxs84A166pu1zeor6orZPVMG5fg1
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf
import tensorflow_hub as hub

df = pd.read_csv("disney_reviews.csv", encoding='latin-1', usecols = ['Rating','Year_Month', 'Reviewer_Location', 'Review_Text', 'Branch'])

df.head()

df = df.dropna(subset = ['Rating', 'Review_Text'])

df.head()

plt.hist(df.Rating, bins = 5)
plt.title('Rating histogram')
plt.ylabel('N') #Number of reviews
plt.xlabel('Ratings')
plt.show()

df["Rating"].value_counts() #The historgram makes sense => people like Disney

#Setting up y value according to the reviews' scores
df["label"] = (df.Rating >= 4).astype(int)
df = df[["Review_Text","label"]]

train, val, test = np.split(df.sample(frac = 1), [int(0.8 * len(df)), int(0.9 * len(df))])

def df_to_dataset(dataframe, shuffle = True, batch_size = 1024):
  df = dataframe.copy()
  labels = df.pop('label')
  df = df["Review_Text"]
  ds = tf.data.Dataset.from_tensor_slices((df, labels))
  if shuffle:
    ds = ds.shuffle(buffer_size=len(dataframe))
  ds = ds.batch(batch_size)
  ds = ds.prefetch(tf.data.AUTOTUNE)
  return ds

train_data = df_to_dataset(train)
valid_data = df_to_dataset(val)
test_data = df_to_dataset(test)

list(train_data)[0]

"""#Embedding"""

#Transform the sentences into numbers that the computer can understand
embedding = "https://tfhub.dev/google/nnlm-en-dim50/2"
hub_layer = hub.KerasLayer(embedding, dtype = tf.string, trainable=True)

#Numpy array
hub_layer(list(train_data)[0][0])

"""#Model"""

model = tf.keras.Sequential()
model.add(hub_layer)
model.add(tf.keras.layers.Dense(16, activation='relu'))
model.add(tf.keras.layers.Dropout(0.4))
model.add(tf.keras.layers.Dense(16, activation='relu'))
model.add(tf.keras.layers.Dropout(0.4))
model.add(tf.keras.layers.Dense(1, activation='sigmoid'))

model.compile(optimizer= tf.keras.optimizers.Adam(learning_rate=0.001),
              loss = tf.keras.losses.BinaryCrossentropy(),
              metrics=['accuracy'])

model.evaluate(train_data)

model.evaluate(valid_data)

history = model.fit(train_data, epochs = 5, validation_data = valid_data)

model.evaluate(test_data)