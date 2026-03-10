from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import time

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

        score = cross_val_score(model, X, y, cv=5).mean()

        start = time.time()
        model.fit(X_train, y_train)
        end = time.time()

        results[name] = score
        trained_models[name] = model
        training_time[name] = round(end - start, 3)

    best_name = max(results, key=results.get)

    best_model = trained_models[best_name]

    leaderboard = sorted(results.items(), key=lambda x: x[1], reverse=True)

    feature_importance = get_feature_importance(best_model, X.columns)

    return {
        "model_scores": results,
        "leaderboard": leaderboard,
        "training_time": training_time,
        "best_model_name": best_name,
        "best_model": best_model,
        "feature_importance": feature_importance
    }