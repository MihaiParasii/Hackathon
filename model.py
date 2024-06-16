import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import numpy as np
import re

# Load and preprocess the dataset
laptops_df = pd.read_csv('laptops.csv')

# Function to convert storage to GB
def convert_storage_to_gb(storage):
    storage = storage.lower().replace('flash storage', '').replace('ssd', '').replace('hdd', '').replace('emmc', '').strip()
    if 'tb' in storage:
        return int(float(storage.replace('tb', '').strip()) * 1024)
    elif 'gb' in storage:
        return int(storage.replace('gb', '').strip())
    return 0

# Apply the conversion to storage column
laptops_df['storage'] = laptops_df['storage'].apply(convert_storage_to_gb)

# Remove the 'GB' suffix from the RAM column and convert it to integer
laptops_df['ram'] = laptops_df['ram'].str.replace('GB', '').astype(int)
laptops_df['price'] = laptops_df['price'].astype(float)

# Feature selection
features = laptops_df[['ram', 'storage', 'price']]
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Train the k-NN model
knn = NearestNeighbors(n_neighbors=5, algorithm='auto')
knn.fit(features_scaled)

# Function to get recommendations
def get_recommendations(ram, storage, price):
    query = np.array([[ram, storage, price]])
    query_scaled = scaler.transform(query)
    distances, indices = knn.kneighbors(query_scaled)
    return laptops_df.iloc[indices[0]].to_dict(orient='records')

# Save the model and scaler
import joblib
joblib.dump(knn, 'knn_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
