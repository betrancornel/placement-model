
import tensorflow as tf
import tensorflow_transform as tft
from typing import Text

# Fitur yang tidak berguna atau membocorkan jawaban
FEATURES_TO_DROP = ["sl_no", "salary"]

# Fitur Numerik (yang akan di-scaling)
NUMERICAL_FEATURES = [
    "ssc_p",
    "hsc_p",
    "degree_p",
    "etest_p",
    "mba_p",
]

# Fitur Kategorikal (yang akan diubah dari string ke angka/index)
CATEGORICAL_FEATURES = [
    "gender",
    "ssc_b",
    "hsc_b",
    "hsc_s",
    "degree_t",
    "workex",
    "specialisation",
]

# Fitur Target (Label)
LABEL_KEY = "status"
VOCAB_SIZE = 101 

def transformed_name(key):
    """Memberi nama '_xf' pada fitur yang sudah ditransformasi"""
    return key + "_xf"


def preprocessing_fn(inputs):    
    outputs = {}
    for feature in NUMERICAL_FEATURES:
        # FIX KRITIS: Eksplisit konversi ke float32 untuk menghindari string/int campuran
        outputs[transformed_name(feature)] = tft.scale_to_0_1(
            tf.cast(inputs[feature], tf.float32)
        )

    for feature in CATEGORICAL_FEATURES:
        outputs[transformed_name(feature)] = tft.compute_and_apply_vocabulary(
            inputs[feature]
        )
        
    # Transformasi Label: 'Placed' -> 1.0, selainnya -> 0.0
    outputs[transformed_name(LABEL_KEY)] = tf.cast(
        tf.equal(inputs[LABEL_KEY], tf.constant("Placed")), tf.float32 
    )
    
    return outputs


def _gzip_reader_fn(filenames):
    """Membaca file TFRecord terkompresi."""
    return tf.data.TFRecordDataset(filenames, compression_type='GZIP')

def input_fn(file_pattern: Text,
             tf_transform_output: tft.TFTransformOutput,
             batch_size: int = 32) -> tf.data.Dataset:
    """Membuat tf.data.Dataset untuk training atau evaluasi."""
    
    transform_feature_spec = (
        tf_transform_output.transformed_feature_spec().copy()
    )
    
    # FIX KRITIS: KEMBALI KE ARSITEKTUR PALING SEDERHANA.
    # Dataset TFX harus mengembalikan keys *_xf
    dataset = tf.data.experimental.make_batched_features_dataset(
        file_pattern=file_pattern,
        batch_size=batch_size,
        features=transform_feature_spec, # <-- INI MENGEMBALIKAN KEYS *_xf
        reader=_gzip_reader_fn,
        label_key=transformed_name(LABEL_KEY)
    )
    
    # HAPUS SEMUA KODE map_fn yang bermasalah.
    return dataset
