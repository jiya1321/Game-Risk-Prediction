import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

np.random.seed(42)

n_samples = 1000

gaming_hours = np.random.uniform(0, 16, n_samples)
sleep_hours = np.random.uniform(3, 10, n_samples)
academic_performance = np.random.randint(1, 4, n_samples)
emotional_state = np.random.randint(1, 5, n_samples)
skip_responsibilities = np.random.randint(1, 5, n_samples)
social_interactions = np.random.randint(0, 20, n_samples)
age_group = np.random.randint(1, 5, n_samples)
game_genres = np.random.randint(1, 8, n_samples)
concentration_difficulty = np.random.randint(0, 2, n_samples)

risk_scores = (
    gaming_hours * 2.5 +
    (10 - sleep_hours) * 2 +
    academic_performance * 3 +
    emotional_state * 2.5 +
    skip_responsibilities * 3.5 +
    (10 - social_interactions) * 1.5 +
    concentration_difficulty * 5 +
    np.random.normal(0, 5, n_samples)
)

risk_labels = np.zeros(n_samples, dtype=int)
risk_labels[risk_scores < 40] = 0
risk_labels[(risk_scores >= 40) & (risk_scores < 70)] = 1
risk_labels[risk_scores >= 70] = 2

features = np.column_stack([
    gaming_hours,
    sleep_hours,
    academic_performance,
    emotional_state,
    skip_responsibilities,
    social_interactions,
    age_group,
    game_genres,
    concentration_difficulty
])

X_train, X_test, y_train, y_test = train_test_split(features, risk_labels, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print(f'Model Accuracy: {accuracy * 100:.2f}%')

with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

print('Model trained and saved as model.pkl')
