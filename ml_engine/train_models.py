from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score

import time

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from explainability.feature_importance import get_feature_importance


def detect_problem_type(y):

    if y.dtype == "object":
        return "classification"

    if y.nunique() <= 20:
        return "classification"

    return "regression"


def train_models(df, target):

    X = df.drop(columns=[target])
    y = df[target]

    problem_type = detect_problem_type(y)

    if problem_type == "classification":

        models = {
            "Logistic Regression": LogisticRegression(max_iter=1000),
            "Random Forest": RandomForestClassifier(),
            "Decision Tree": DecisionTreeClassifier()
        }

    else:

        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest Regressor": RandomForestRegressor(),
            "Decision Tree Regressor": DecisionTreeRegressor()
        }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    results = {}
    trained_models = {}
    training_time = {}

    for name, model in models.items():

        # Cross validation scoring
        if problem_type == "classification":
            scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
        else:
            scores = cross_val_score(model, X, y, cv=5, scoring="r2")

        score = scores.mean()

        # Training time tracking
        start = time.time()

        model.fit(X_train, y_train)

        end = time.time()

        training_time[name] = round(end - start, 3)

        results[name] = score
        trained_models[name] = model

    # Best model selection
    best_model_name = max(results, key=results.get)
    best_model = trained_models[best_model_name]

    # Feature importance
    feature_importance = get_feature_importance(best_model, X.columns)

    # Model leaderboard
    leaderboard = sorted(results.items(), key=lambda x: x[1], reverse=True)

    return {
        "problem_type": problem_type,
        "model_scores": results,
        "leaderboard": leaderboard,
        "training_time": training_time,
        "best_model_name": best_model_name,
        "best_model": best_model,
        "feature_importance": feature_importance
    }