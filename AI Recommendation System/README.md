## AI Recommendation System

Model: Random Forest Classifier

Accuracy: 74.1%

Outputs:
- Employee Recommendation Prediction
- Feature Importance Analysis
- Confusion Matrix

Note:
The trained model is stored at `models/employee_recommendation_model.pkl`.
It can be regenerated from `datasets/cleaned/Business_Operation_ml_ready.csv`
using the training notebook or the following command from the repository root:

```powershell
.venv\Scripts\python.exe -m pip install -r docs\requirements.txt
```

The checked-in model was serialized with scikit-learn 1.7.2. Keep the pinned
version when loading this artifact to avoid model persistence compatibility
warnings.

The reusable recommendation logic is in `backend/api/recommendation.py`.
