
# Import library
import tensorflow as tf
import tensorflow_transform as tft
import keras_tuner as kt
from tfx.v1.components import TunerFnResult
from tfx.components.trainer.fn_args_utils import FnArgs

# !!! Impor input_fn dari transform.py !!!
from transform import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    transformed_name,
    input_fn, # <-- input_fn diimpor dari transform
    VOCAB_SIZE
)

def model_builder(hyperparameters):

    input_features = []
    numeric_inputs = []
    categorical_inputs = []
    
    # Input Numerikal
    for key in NUMERICAL_FEATURES:
        input_layer = tf.keras.Input(
            shape=(1,), 
            name=transformed_name(key),
            dtype=tf.float32
        )
        input_features.append(input_layer)
        numeric_inputs.append(input_layer)

    # Input Kategorikal
    for key in CATEGORICAL_FEATURES:
        input_layer = tf.keras.Input(
            shape=(1,), 
            name=transformed_name(key),
            dtype=tf.int64
        )
        input_features.append(input_layer)
        categorical_inputs.append(input_layer)

    # Embedding Layer
    embedded_features = []
    embedding_dim = hyperparameters.Choice('embedding_dim', [4, 8, 16])

    for input_layer in categorical_inputs:
        embedding = tf.keras.layers.Embedding(
            input_dim=VOCAB_SIZE, 
            output_dim=embedding_dim
        )(input_layer)
        flattened_embedding = tf.keras.layers.Flatten()(embedding)
        embedded_features.append(flattened_embedding)
        
    concatenated_numerics = tf.keras.layers.concatenate(numeric_inputs)
    concatenated_categoricals = tf.keras.layers.concatenate(embedded_features)

    # Gabungkan semua fitur
    concatenate_all = tf.keras.layers.concatenate(
        [concatenated_numerics, concatenated_categoricals]
    )

    # DNN Tower (Tuned)
    deep = tf.keras.layers.Dense(hyperparameters.Choice(
        'unit_1', [128, 256]), 
        activation="relu")(concatenate_all)
    deep = tf.keras.layers.Dropout(hyperparameters.Choice(
        'dropout_1', [0.2, 0.4]))(deep)

    deep = tf.keras.layers.Dense(hyperparameters.Choice(
        'unit_2', [64, 128]), 
        activation="relu")(deep)
    deep = tf.keras.layers.Dropout(hyperparameters.Choice(
        'dropout_2', [0.2, 0.4]))(deep)

    deep = tf.keras.layers.Dense(hyperparameters.Choice(
        'unit_3', [32, 64]), 
        activation="relu")(deep)
    deep = tf.keras.layers.Dropout(hyperparameters.Choice(
        'dropout_3', [0.2, 0.4]))(deep)

    # Output Layer
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(deep)
    model = tf.keras.models.Model(inputs=input_features, outputs=outputs)

    # Compile Model (Tuned)
    model.compile( # <--- PASTIKAN INI DI SINI
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=hyperparameters.Choice(
                'learning_rate', [0.0001, 0.001])),
        loss='binary_crossentropy',
        metrics=[tf.keras.metrics.BinaryAccuracy()]
    )
    
    return model

# --- Fungsi Tuner ---
def tuner_fn(fn_args: FnArgs):
    """Fungsi utama untuk TFX Tuner."""

    tf_transform_output = tft.TFTransformOutput(fn_args.transform_graph_path)

    # Menggunakan input_fn dari transform
    train_dataset = input_fn(
        fn_args.train_files, 
        tf_transform_output, 
        batch_size=32
    )
    eval_dataset = input_fn(
        fn_args.eval_files, 
        tf_transform_output, 
        batch_size=32
    )
    
    # Setup Keras Tuner
    tuner = kt.RandomSearch(
        model_builder,
        objective='val_binary_accuracy',
        max_trials=10, 
        directory=fn_args.working_dir,
        project_name='placement_tuning'
    )

    stop_early = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)

    return TunerFnResult(
        tuner=tuner,
        fit_kwargs={
            "x": train_dataset,
            'validation_data': eval_dataset,
            'steps_per_epoch': fn_args.train_steps,
            'validation_steps': fn_args.eval_steps,
            "epochs": 20, 
            "callbacks": [stop_early]
        }
    )
