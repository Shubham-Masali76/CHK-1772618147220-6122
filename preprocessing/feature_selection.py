import pandas as pd
import numpy as np

def remove_highly_correlated_features(df, threshold=0.9, target_col=None):
    """
    Remove highly correlated features while preserving the target column.
    Only computes correlation on numeric columns.
    
    Args:
        df: DataFrame to process
        threshold: Correlation threshold (default 0.9)
        target_col: Name of target column to exclude from removal
    """
    df_copy = df.copy()
    
    # Select only numeric columns for correlation analysis
    numeric_df = df_copy.select_dtypes(include=[np.number])
    
    # If no numeric columns, return unchanged
    if numeric_df.empty:
        return df_copy, []
    
    # Calculate correlation matrix on numeric columns only
    corr = numeric_df.corr().abs()
    
    # Get upper triangle of correlation matrix
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    
    # Find columns to drop (highly correlated with others)
    to_drop = [col for col in upper.columns if any(upper[col] > threshold)]
    
    # Never drop the target column
    if target_col and target_col in to_drop:
        to_drop.remove(target_col)
    
    # Drop the columns
    if to_drop:
        df_result = df_copy.drop(columns=to_drop)
    else:
        df_result = df_copy
    
    return df_result, to_drop