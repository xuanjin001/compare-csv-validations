import pandas as pd

def compare_csvs(file1_path, file2_path, key_column, columns_to_compare):
    # Load the datasets
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)
    
    # Ensure the key column and comparison columns exist in both
    all_cols = [key_column] + columns_to_compare
    df1_subset = df1[all_cols].set_index(key_column)
    df2_subset = df2[all_cols].set_index(key_column)
    
    # 1. Identify Missing and New Records
    missing_in_f2 = df1_subset.index.difference(df2_subset.index)
    new_in_f2 = df2_subset.index.difference(df1_subset.index)
    
    # 2. Compare Data for overlapping keys
    common_keys = df1_subset.index.intersection(df2_subset.index)
    
    # Align the dataframes to the same keys and columns
    comparison_f1 = df1_subset.loc[common_keys, columns_to_compare]
    comparison_f2 = df2_subset.loc[common_keys, columns_to_compare]
    
    # Create a mask where the values are NOT equal
    diff_mask = (comparison_f1 != comparison_f2).any(axis=1)
    differences = comparison_f1[diff_mask].copy()
    
    # Add the "changed" values from the second file for visibility
    for col in columns_to_compare:
        differences[f"{col}_new"] = comparison_f2.loc[diff_mask, col]

    return {
        "missing": missing_in_f2.tolist(),
        "new": new_in_f2.tolist(),
        "changes": differences
    }

# --- Example Usage ---
results = compare_csvs('MOCK_DATA_2.csv', 'MOCK_DATA_1.csv', 'id', ['email'])
print(results['changes'])