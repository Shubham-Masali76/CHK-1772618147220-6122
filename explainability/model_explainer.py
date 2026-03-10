def explain_model_choice(best_model_name, scores):

    explanation = {}

    explanation["title"] = "Why this model was selected"

    explanation["message"] = (
        f"The system trained several machine learning models and compared their performance. "
        f"The model **{best_model_name}** achieved the highest score among all tested models."
    )

    if "Random Forest" in best_model_name:

        explanation["reason"] = (
            "Random Forest works well because it combines many decision trees. "
            "This helps reduce prediction errors and improves reliability."
        )

    elif "Logistic Regression" in best_model_name:

        explanation["reason"] = (
            "Logistic Regression is a simple and fast algorithm that works well "
            "when the relationship between features and the target is clear."
        )

    elif "Decision Tree" in best_model_name:

        explanation["reason"] = (
            "Decision Trees split the data into smaller groups based on feature values. "
            "They are easy to interpret and work well for structured data."
        )

    elif "Linear Regression" in best_model_name:

        explanation["reason"] = (
            "Linear Regression models the relationship between variables using a straight line. "
            "It works well when the relationship between variables is mostly linear."
        )

    else:

        explanation["reason"] = "This model produced the best predictive performance on your dataset."

    return explanation