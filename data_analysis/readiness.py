def dataset_readiness(analysis):

    issues = []
    score = 100

    missing = sum(analysis["missing_values"].values())
    duplicates = analysis["duplicate_rows"]

    if missing > 0:
        issues.append("Some values are missing.")
        score -= 20

    if duplicates > 0:
        issues.append("Duplicate rows found.")
        score -= 10

    if len(analysis["numerical_columns"]) == 0:
        issues.append("No numeric columns detected.")
        score -= 30

    if score >= 80:
        status = "READY"
    elif score >= 50:
        status = "WARNING"
    else:
        status = "NOT READY"

    return {"score": score, "status": status, "issues": issues}