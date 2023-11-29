import re

import numpy as np
import pandas as pd
import tensorflow as tf
from tf.keras.layers import Embedding


def prepare(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text


def prepare_data(file="./medium_data.csv"):
    df = pd.read_csv(file, parse_dates=["date"])
    df.title = df.title.apply(lambda x: prepare(x))
    tokenizer = tf.keras.preprocessing.text.Tokenizer(
        oov_token="<oov>"
    )  # айди для тех слов, которых нет в словаре
    tokenizer.fit_on_texts(df.title)
    total_words = len(tokenizer.word_index) + 1

    input_sequences = []
    for line in df.title:
        token_list = tokenizer.texts_to_sequences([line])[0]
        for i in range(1, len(token_list)):
            n_gram_sequence = token_list[: i + 1]
            input_sequences.append(n_gram_sequence)

    max_sequence_len = max([len(x) for x in input_sequences])
    input_sequences = np.array(
        tf.keras.preprocessing.sequence.pad_sequences(
            input_sequences, maxlen=max_sequence_len, padding="pre"
        )
    )

    X, y = input_sequences[:, :-1], input_sequences[:, -1]
    y = tf.keras.utils.to_categorical(y, num_classes=total_words)
    return X, y, total_words, tokenizer, max_sequence_len


def train(X, y, total_words):
    model = tf.keras.models.Sequential()
    model.add(Embedding(total_words, 128, input_length=max_sequence_len - 1))
    model.add(tf.keras.layers.LSTM(128))
    model.add(tf.keras.layers.Dense(total_words, activation="softmax"))
    model.compile(
        loss="categorical_crossentropy",
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        metrics=["accuracy"],
    )
    model.fit(X, y, epochs=30)
    return model


if __name__ == "__main__":
    X, y, total_words, tokenizer, max_sequence_len = prepare_data()
    model = train(X, y, total_words)
    tf.keras.saving.save_model(model, "model.keras", overwrite=True)
