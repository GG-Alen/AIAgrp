# Импорт необходимых библиотек
import json
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler



def load_data(soil_file, crop_file):
    """Загрузка данных из JSON-файлов."""
    with open(soil_file, 'r', encoding='utf-8') as f:
        soils = json.load(f)
    with open(crop_file, 'r', encoding='utf-8') as f:
        crops = json.load(f)
    return soils, crops


def prepare_features(soils, crops):
    """Подготовка признаков для модели."""
    soil_features, soil_names = [], []
    for soil in soils:
        features = [
            soil['acidity'],
            soil['moisture'],
            soil['humus'],
            {'granular': 1, 'cloddy': 0.5, 'dusty': 0}[soil['structure']],
            soil['macros']['nitrogen'],
            soil['macros']['phosphorus'],
            soil['macros']['potassium'],
            soil['macros']['magnesium'],
            soil['macros']['calcium']
        ]
        soil_features.append(features)
        soil_names.append(soil['name'])

    crop_features, crop_names = [], []
    for crop in crops:
        features = [
            crop['required_acidity'],
            crop['required_moisture'],
            crop['required_humus'],
            {'granular': 1, 'cloddy': 0.5, 'dusty': 0}[crop['preferred_structure']],
            crop['required_macros']['nitrogen'],
            crop['required_macros']['phosphorus'],
            crop['required_macros']['potassium'],
            crop['required_macros']['magnesium'],
            crop['required_macros']['calcium']
        ]
        crop_features.append(features)
        crop_names.append(crop['name'])

    return (
        np.array(soil_features), np.array(crop_features),
        soil_names, crop_names
    )


def create_model(input_dim):
    """Создание модели нейронной сети."""
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_dim=input_dim),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(input_dim, activation='linear')
    ])
    model.compile(optimizer='adam', loss='mse')
    return model


def find_matches(crop_features, soil_features, soil_names, model, scaler, crop_names):
    """Поиск соответствий культура-почва."""
    results = []
    for i, crop in enumerate(crop_features):
        crop_scaled = scaler.transform([crop])
        pred = model.predict(crop_scaled, verbose=0)
        distances = np.linalg.norm(soil_features - pred[0], axis=1)
        best_idx = np.argmin(distances)
        results.append({
            "culture": crop_names[i],
            "best_soil": soil_names[best_idx],
            "distance": float(distances[best_idx])  # преобразуем для JSON
        })
    return results


def save_results(results, filename='results.json'):
    """Сохранение результатов в JSON-файл."""
    with open(filename, 'w', encoding='utf-8') as f:
        results = json.dump(results, f, ensure_ascii=False, indent=2)



def init():
    # Загрузка и подготовка данных
    soils, crops = load_data('soils.json', 'crops.json')
    soil_features, crop_features, soil_names, crop_names = prepare_features(soils, crops)

    # Нормализация данных
    scaler = StandardScaler()
    all_features = np.vstack([soil_features, crop_features])
    scaler.fit(all_features)
    soil_features_scaled = scaler.transform(soil_features)
    crop_features_scaled = scaler.transform(crop_features)

    # Создание и обучение модели
    model = create_model(soil_features.shape[1])
    model.fit(soil_features_scaled, soil_features_scaled, epochs=100, verbose=0)

    # Поиск соответствий и сохранение результатов
    results = find_matches(crop_features_scaled, soil_features_scaled, soil_names, model, scaler, crop_names)
    save_results(results)

init()