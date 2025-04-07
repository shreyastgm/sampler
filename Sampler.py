# Welcome message
print('''
-----------------------------------------------------------------------------------------
                        ~ Welcome to data sampler utility ~
This script generates sample data based on the inputs and filters provided by the user.
Please ensure that the input file and data has been validated and cleaned before using.
-----------------------------------------------------------------------------------------
''')

OPTIONS = {
    1: "At least one", 
    2: "Most values",
    3: "Random",
}

# Modify the following to set default values for execution
default_filters = {
    "Branch": OPTIONS[1],
    "Invoice Date": OPTIONS[1],
    "Customer Name": OPTIONS[1],
    "Item Main Group": OPTIONS[2],
}

# Code starts here
import pandas as pd
import random

def sample_csv(input_csv, output_csv, rules):
    df = pd.read_csv(input_csv)
    original_len = len(df)

    # Base condition: input must have at least 20 rows
    if original_len < 20:
        print(f"\n❌ Input file has only {original_len} rows. Need at least 20 to run sampling.")
        return

    sampled_indices = set()

    for column, method in rules.items():
        if column not in df.columns:
            print(f"Warning: Column '{column}' not found in CSV.")
            continue

        if method == 'At least one':
            for value in df[column].dropna().unique():
                value_rows = df[df[column] == value]
                sampled_row = value_rows.sample(n=1)
                sampled_indices.update(sampled_row.index)

        elif method == 'Most values':
            unique_values = df[column].dropna().unique()
            n_values = int(len(unique_values) * 0.85)
            selected_values = random.sample(list(unique_values), n_values)
            for value in selected_values:
                value_rows = df[df[column] == value]
                sampled_row = value_rows.sample(n=1)
                sampled_indices.update(sampled_row.index)

        elif method == 'Random':
            sampled_row = df.sample(frac=0.05)
            sampled_indices.update(sampled_row.index)

    # Ensure target sample size is at least 20 or 5% of input
    target_size = max(int(original_len * 0.05), 20)
    current_sample = df.loc[list(sampled_indices)]

    if len(current_sample) < target_size:
        remaining = df.drop(index=sampled_indices)
        needed = target_size - len(current_sample)
        if needed > 0 and len(remaining) > 0:
            to_sample = min(needed, len(remaining))
            additional_samples = remaining.sample(n=to_sample)
            current_sample = pd.concat([current_sample, additional_samples])
            sampled_indices.update(additional_samples.index)

    if len(current_sample) > target_size:
        print(f"\nNote: Final sample has {len(current_sample)} rows, which exceeds the target of {target_size} to satisfy all filter rules.")

    current_sample.to_csv(output_csv, index=False)
    print(f"\n✅ Sampled data saved to {output_csv} ({len(current_sample)} rows).")


if __name__ == "__main__":
    # Taking inputs from user
    input_file = input("* Enter the file to be Audited: ")
    if not input_file:
        print("No input provided taking default filename.")
        input_file = "Test.csv" # Default filename to be used
    output_file = input_file[:-4]+' Audit Sample.csv'

    # Get number of filters to be applied
    filter_count = input("\n* Enter the number of filters to be applied: ")
    if not filter_count:
        filter_count = 0
    
    filters = {}
    for i in range(int(filter_count)):
        key = input(f"\n* Enter column name for condition {i+1}: ")
        print("\nFilter OPTIONS:")
        for val in OPTIONS:
            print(str(val)+")", OPTIONS[val])
        value = int(input(f"\n* Select filter option for {key}: "))
        filters[key] = OPTIONS[value]
    
    # Use Default filters in case of no input
    if not filters:
        print("No input provided taking default filter values.")
        filters = default_filters

    print("\n* List of filters to be used:")
    for key in filters:
        print(key+":", filters[key])

    # Get confirmation before execution    
    input("\n* Press enter to start execution if satisfied with current input, else retry ")

    sample_csv(input_file, output_file, filters)