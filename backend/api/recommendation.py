from pathlib import Path

import joblib
import pandas as pd


MODEL_PATH = Path(__file__).resolve().parents[2] / 'models' / 'employee_recommendation_model.pkl'


def load_model(model_path=MODEL_PATH):
    if not Path(model_path).exists():
        raise FileNotFoundError(
            f'Employee recommendation model not found at {model_path}. '
            'Run the recommendation training notebook first.'
        )
    return joblib.load(model_path)


def recommend_employees(data, top_n=5, model=None):
    if top_n < 1:
        raise ValueError('top_n must be at least 1.')

    employees = data.copy()
    if 'employee_id' not in employees.columns:
        raise ValueError("Input data must include an 'employee_id' column.")

    trained_model = model or load_model()
    feature_names = list(trained_model.feature_names_in_)
    missing_features = [
        feature for feature in feature_names if feature not in employees.columns
    ]
    if missing_features:
        raise ValueError(
            f'Input data is missing model features: {", ".join(missing_features)}'
        )

    model_input = employees[feature_names]
    probabilities = pd.DataFrame(trained_model.predict_proba(model_input)).to_numpy()
    positive_class_index = list(trained_model.classes_).index(1)
    predictions = trained_model.predict(model_input)

    result = employees[['employee_id']].copy()
    result['recommended'] = predictions
    result['probability'] = probabilities[:, positive_class_index]
    return (
        result.sort_values('probability', ascending=False)
        .drop_duplicates(subset=['employee_id'])
        .head(top_n)
        .reset_index(drop=True)
    )


def recommend_for_task(data, task, top_n=5, model=None):
    candidates = data.copy()
    filters = {
        'required_skill': task.get('required_skill'),
        'department': task.get('department'),
        'task_priority': task.get('task_priority'),
    }

    for field, value in filters.items():
        if value:
            column = f'{field}_{value}'
            if column not in candidates.columns:
                raise ValueError(f"Unsupported {field}: {value}")
            candidates = candidates[candidates[column] == 1]

    if candidates.empty:
        raise ValueError('No employees match the selected task requirements.')

    return recommend_employees(candidates, top_n=top_n, model=model)


def recommend_from_csv(csv_path, top_n=5, model=None):
    return recommend_employees(pd.read_csv(csv_path), top_n=top_n, model=model)


def recommend_task_from_csv(csv_path, task, top_n=5, model=None):
    return recommend_for_task(pd.read_csv(csv_path), task, top_n=top_n, model=model)