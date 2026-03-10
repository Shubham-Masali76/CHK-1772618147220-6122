import plotly.express as px


def plot_feature_importance(feature_df):

    if feature_df is None:
        return None

    fig = px.bar(
        feature_df,
        x="importance",
        y="feature",
        orientation="h",
        title="Feature Importance",
    )

    fig.update_layout(
        yaxis={'categoryorder':'total ascending'}
    )

    return fig