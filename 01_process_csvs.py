import pandas as pd
import os
from io import StringIO

# Configuration
data_folder = r'D:\recreate-exports'  #update accordingly
output_folder = r'D:\recreate-exports-processed' #update accordingly

var_name_map = {
    'tas': 'Temperature',
    'pr': 'Precipitation',
    'evspsbl': 'Evaporation',
    'rdis': 'Discharge'
}

all_data = []
skipped_files = []

# Main loop
for filename in os.listdir(data_folder):
    if not filename.endswith('.csv'):
        skipped_files.append((filename, "Not a CSV file"))
        continue

    print(f"\n Processing: {filename}")

    name = filename.replace('.nc.csv', '').replace('.csv', '')
    parts = name.split('_')

    if len(parts) < 6:
        skipped_files.append((filename, "Filename too short or malformed"))
        continue

    try:
        tokens = parts[0].split('-')
        study_case = tokens[1]
        scenario = tokens[3]
        gcm = tokens[4]
        rcm = parts[1].replace("RC4", "RCA4")  # Normalize RC4 to RCA4
        climate_model = f"{gcm}/{rcm}"

        # Robust variable code detection
        variable_code = None
        for part in parts:
            for key in var_name_map.keys():
                if f"-{key}" in part or part == key:
                    variable_code = key
                    break
            if variable_code:
                break

        if not variable_code:
            skipped_files.append((filename, "Could not identify variable code in filename"))
            continue

        hydro_model = parts[3] if variable_code == 'rdis' else None
        variable = var_name_map.get(variable_code, variable_code)

    except Exception as e:
        skipped_files.append((filename, f"Metadata parsing error: {e}"))
        continue

    file_path = os.path.join(data_folder, filename)

    # Read and clean file
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        header_line = lines[0]
        delimiter = '\t' if '\t' in header_line else ','

        df = pd.read_csv(StringIO(''.join(lines)), delimiter=delimiter)

    except Exception as e:
        skipped_files.append((filename, f"File read error (after cleaning): {e}"))
        continue

    # Normalize columns
    df.columns = [col.lower().strip() for col in df.columns]
    print(f" Columns: {df.columns.tolist()} — looking for variable_code: '{variable_code}'")

    if 'time' not in df.columns or variable_code not in df.columns:
        skipped_files.append((filename, f"Missing 'time' or expected variable column '{variable_code}'"))
        continue

    try:
        df['date'] = pd.to_datetime(df['time'], errors='coerce').dt.date
        df = df.rename(columns={variable_code: 'value'})[['date', 'value']]
    except Exception as e:
        skipped_files.append((filename, f"Date conversion or column renaming error: {e}"))
        continue

    # Add metadata
    df['study_case'] = study_case
    df['scenario'] = scenario
    df['climate_model'] = climate_model
    df['variable'] = variable
    df['hydro_model'] = hydro_model

    all_data.append(df)


# Output
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)

    combined_path = os.path.join(output_folder, 'combined_data.csv')
    combined_df.to_csv(combined_path, index=False)
    print(f"\n Combined data saved to: {combined_path}")

    for site, group_df in combined_df.groupby('study_case'):
        site_path = os.path.join(output_folder, f"{site}_data.csv")
        group_df.to_csv(site_path, index=False)
        print(f" Saved site file: {site_path}")
else:
    print("\n No valid data was processed.")

# Generation of 'skipped file' report
if skipped_files:
    skip_report_path = os.path.join(output_folder, 'skipped_files_report.csv')
    pd.DataFrame(skipped_files, columns=['filename', 'reason']).to_csv(skip_report_path, index=False)
    print(f"\n Skipped file report saved to: {skip_report_path}")
else:
    print("\n All files processed successfully, no skips")
    


