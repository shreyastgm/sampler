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
}

# Modify the following to set default values for execution
default_filename = "Input.csv"
default_amount_column = "Net Amount In INR"
default_customer_column = "Customer Name"
default_filters = {
    "Branch": OPTIONS[1],
    "Invoice Date": OPTIONS[1],
    "Customer Name": OPTIONS[1],
    "Item Main Group": OPTIONS[2]
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
            print(f"⚠️ Column '{column}' not found in DataFrame.")
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

    # Ensure target sample size is at least 20 or 5% of input
    target_size = max(int(original_len * 0.05), 20)
    current_sample = df.loc[list(sampled_indices)]

    if amount_column in df.columns:
        df[amount_column] = df[amount_column].astype(float).abs()
        current_sample[amount_column] = current_sample[amount_column].astype(float).abs()

        total_amount = df[amount_column].sum()
        min_sample_amount = total_amount * 0.10
        amount_threshold = total_amount * 0.05

        # Add rows where Net Amount > 5% of total
        high_value_rows = df[df[amount_column] > amount_threshold]
        
        # Ensure uniqueness by Customer Name if it exists
        if customer_column in df.columns:
            existing_customers = set(current_sample[customer_column])
            unique_highs = []
            seen_amounts = set()
            for _, row in high_value_rows.sort_values(by=amount_column, ascending=False).iterrows():
                amount = row[amount_column]
                customer = row[customer_column]
                if amount not in seen_amounts and customer not in existing_customers:
                    unique_highs.append(row)
                    seen_amounts.add(amount)
                    existing_customers.add(customer)

            if unique_highs:
                current_sample = pd.concat([current_sample, pd.DataFrame(unique_highs)])
        else:
            # If no Customer Name column, just add rows with Net Amount > 5% of total
            current_sample = pd.concat([current_sample, high_value_rows])

        # Now check if the total sample amount is >= 10% of total
        sample_amount = current_sample[amount_column].sum()
        if sample_amount < min_sample_amount:
            print(f"Sample Net Amount = {sample_amount:.2f}, less than 10% of total ({min_sample_amount:.2f}), adding more results to output.")
            # Add more rows with highest Net Amount until reaching 10%
            remaining_df = df.drop(index=current_sample.index)
            remaining_df = remaining_df.sort_values(by=amount_column, ascending=False)
            
            # Avoid adding duplicate rows by checking if they are already in the sample
            for _, row in remaining_df.iterrows():
                if row.name not in sampled_indices:
                    current_sample = pd.concat([current_sample, pd.DataFrame([row])])
                    sample_amount += row[amount_column]
                    sampled_indices.add(row.name)
                if sample_amount >= min_sample_amount:
                    break

    if len(current_sample) < target_size:
        remaining = df.drop(index=sampled_indices)
        needed = target_size - len(current_sample)
        if needed > 0 and len(remaining) > 0:
            to_sample = min(needed, len(remaining))
            additional_samples = remaining.sample(n=to_sample)
            current_sample = pd.concat([current_sample, additional_samples])
            sampled_indices.update(additional_samples.index)

    current_sample = current_sample.drop_duplicates()
    current_sample.to_csv(output_csv, index=False)
    print(f"\n✅ {len(current_sample)} rows ({round(len(current_sample)*100/original_len)}% data) saved to {output_csv}.")


if __name__ == "__main__":
    # Taking inputs from user
    input_file = input("* Enter the file to be Audited: ")
    if not input_file:
        print("No input provided taking default filename.")
        input_file = default_filename

    output_file = input_file[:-4]+' Audit Sample.csv'

    amount_column = input("* Enter the name for amount column: ")
    if not amount_column:
        print("No input provided taking default amount column.")
        amount_column = default_amount_column

    customer_column = input("* Enter the name for customer column: ")
    if not customer_column:
        print("No input provided taking default customer column.")
        customer_column = default_customer_column

    # Get number of filters to be applied
    filter_count = input("* Enter the number of filters to be applied: ")
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
    else:
        print("\n* List of filters to be used:")
        for key in filters:
            print(key+":", filters[key])

    # Get confirmation before execution    
    input("\n* Press enter to start execution if satisfied with current input, else retry ")

    sample_csv(input_file, output_file, filters)
