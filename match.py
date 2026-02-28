import pandas as pd

def generate_comparison_report(source_df, target_df, join_on_columns):
    """
    Compares two dataframes and generates a report showing matches and mismatches.
    """
    # Merge dataframes with an indicator to track the source of each row
    comparison = pd.merge(
        source_df, 
        target_df, 
        on=join_on_columns, 
        how='outer', 
        suffixes=('_source', '_target'), 
        indicator=True
    )

    # Map indicator values to human-readable status
    status_map = {
        'both': 'Matched',
        'left_only': 'Missing in Target',
        'right_only': 'Missing in Source'
    }
    comparison['Comparison_Status'] = comparison['_merge'].map(status_map)

    # Drop the technical merge column
    comparison.drop(columns=['_merge'], inplace=True)

    # Generate Summary Statistics for the report
    summary = {
        'Total Records': len(comparison),
        'Matches Found': len(comparison[comparison['Comparison_Status'] == 'Matched']),
        'Discrepancies': len(comparison[comparison['Comparison_Status'] != 'Matched'])
    }

    return comparison, summary

# Example Usage
if __name__ == "__main__":
    # Sample Data
    data_client = pd.DataFrame({
        'ID': [1, 2, 3, 4],
        'Amount': [100, 200, 300, 400]
    })
    
    data_internal = pd.DataFrame({
        'ID': [1, 2, 5],
        'Amount': [100, 250, 500]
    })

    report_df, stats = generate_comparison_report(data_client, data_internal, ['ID'])

    print("--- Comparison Summary ---")
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n--- Detailed Report ---")
    print(report_df)

    # Export to CSV for client delivery
    # report_df