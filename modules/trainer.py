
# Import library
import tensorflow as tf
import tensorflow_transform as tft
from tfx.components.trainer.fn_args_utils import FnArgs
from typing import Text, Dict, List, Any

# Impor semua fungsi dan variabel dari transform.py
from transform import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    LABEL_KEY,
    transformed_name,
    input_fn,
    VOCAB_SIZE,
    FEATURES_TO_DROP
)

# ----------------------------------------------------------------
# 1. FUNGSI MODEL_BUILDER 
# ----------------------------------------------------------------
def model_builder(hyperparameters: Dict[Text, Any]) -> tf.keras.Model: 
    
    input_features = []
    numeric_inputs = []
    categorical_inputs = []
    
    for key in NUMERICAL_FEATURES:
        input_layer = tf.keras.Input(
            shape=(1,), 
            name=transformed_name(key), 
            dtype=tf.float32
        )
        input_features.append(input_layer)
        numeric_inputs.append(input_layer)

    for key in CATEGORICAL_FEATURES:
        input_layer = tf.keras.Input(
            shape=(1,), 
            name=transformed_name(key), 
            dtype=tf.int64
        )
        input_features.append(input_layer)
        categorical_inputs.append(input_layer)

    embedded_features = []
    embedding_dim = hyperparameters.get('embedding_dim', 8) 

    for input_layer in categorical_inputs:
        embedding = tf.keras.layers.Embedding(
            input_dim=VOCAB_SIZE, 
            output_dim=embedding_dim
        )(input_layer)
        flattened_embedding = tf.keras.layers.Flatten()(embedding)
        embedded_features.append(flattened_embedding)
    
    concatenated_numerics = tf.keras.layers.concatenate(numeric_inputs)
    concatenated_categoricals = tf.keras.layers.concatenate(embedded_features)
    concatenate_all = tf.keras.layers.concatenate(
        [concatenated_numerics, concatenated_categoricals]
    )

    deep = tf.keras.layers.Dense(hyperparameters.get('unit_1', 128), activation="relu")(concatenate_all)
    deep = tf.keras.layers.Dropout(hyperparameters.get('dropout_1', 0.2))(deep)
    deep = tf.keras.layers.Dense(hyperparameters.get('unit_2', 64), activation="relu")(deep)
    deep = tf.keras.layers.Dropout(hyperparameters.get('dropout_2', 0.2))(deep)
    deep = tf.keras.layers.Dense(hyperparameters.get('unit_3', 32), activation="relu")(deep)
    deep = tf.keras.layers.Dropout(hyperparameters.get('dropout_3', 0.2))(deep)

    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(deep)
    
    model = tf.keras.models.Model(inputs=input_features, outputs=outputs)
    
    model.compile( # <--- PASTIKAN INI DI SINI
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=hyperparameters.get('learning_rate', 0.001)),
        loss='binary_crossentropy',
        metrics=[tf.keras.metrics.BinaryAccuracy()]
    )
    
    return model
    


# ----------------------------------------------------------------
# 2. FUNGSI RUN_FN (Saving Model Dasar - Syntax Fix)
# ----------------------------------------------------------------
def run_fn(fn_args: FnArgs):
    
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)
    
    train_dataset = input_fn(fn_args.train_files, tf_transform_output)
    eval_dataset = input_fn(fn_args.eval_files, tf_transform_output)
    
    # Definisikan default hyperparameters
    hyperparameters = {
        'embedding_dim': 8, 'unit_1': 128, 'dropout_1': 0.2, 
        'unit_2': 64, 'dropout_2': 0.2, 'unit_3': 32, 
        'dropout_3': 0.2, 'learning_rate': 0.001
    }
    
    # Ambil hyperparameters terbaik jika ada dari Tuner
    if fn_args.hyperparameters:
        hyperparameters = fn_args.hyperparameters['values']
        
    # Bangun Model dan Latih Model
    model = model_builder(hyperparameters) 
    stop_early = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)
    
    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps,
        epochs=20,
        callbacks=[stop_early]
    )
    
    # SIMPAN MODEL
    # Model disimpan dengan default signature yang menerima transformed features
    # Untuk serving dengan raw inputs, transform graph perlu digunakan terlebih dahulu
    tf.keras.models.save_model(
        model,
        fn_args.serving_model_dir,
        overwrite=True,
        include_optimizer=False,
        signatures=None,  # Gunakan default signature (transformed features)
        options=tf.saved_model.SaveOptions(
            experimental_custom_gradients=False
        )
    )
