import os
import pandas as pd
import numpy as np


def get_raw_data():
    """
    Loads field-level telemetry from local storage. Falls back to a
    synthetic dataset generator if the raw file is missing.
    """
    source_file = "nsta_field_production.csv"

    if os.path.exists(source_file):
        print(f"Reading local source data: {source_file}...")
        return pd.read_csv(source_file)

    print(f"Warning: '{source_file}' not found. Generating mock framework data...")

    # Reproducible seed for baseline verification
    np.random.seed(42)
    fields = [f"Field_{letter}" for letter in "ABCDEFGHIJ"]
    dates = pd.date_range(start="2025-01-01", periods=12, freq="ME")

    records = []
    for field in fields:
        # 20% baseline probability of a field being shut-in permanently
        is_shutin = np.random.choice([True, False], p=[0.2, 0.8])
        for date in dates:
            if is_shutin:
                oil_vol, gas_vol = 0.0, 0.0
            else:
                oil_vol = np.random.uniform(1000, 5000) if field != "Field_E" else 0.0
                gas_vol = np.random.uniform(500, 3000) if field != "Field_A" else 0.0

            records.append({
                "FIELD_NAME": field,
                "PRODUCTION_DATE": date.strftime("%Y-%m-%d"),
                "OIL_PROD_VOL": oil_vol,
                "GAS_PROD_VOL": gas_vol
            })

    df_mock = pd.DataFrame(records)
    df_mock.to_csv(source_file, index=False)
    print(f"Mock telemetry cached to local environment: '{source_file}'.")
    return df_mock


def run_basin_pipeline(df):
    """
    Standardizes schema formats, runs operational classification logic,
    and aggregates field data to a macro level.
    """
    print("Processing production analytics and asset classification...")

    # Clean up trailing/leading whitespace and standardize case
    df.columns = [col.strip().upper() for col in df.columns]

    # Handle schema divergence between true public files and standard mock layouts
    if 'OILPRODM3' in df.columns:
        print("Mapping official basin telemetry schema...")
        field_col = 'FIELDNAME'
        oil_col = 'OILPRODM3'

        # Combine associated and dry gas inputs for net gas metric
        df['GAS_TOTAL_VOL'] = pd.to_numeric(df['AGASPROKSM'], errors='coerce').fillna(0) + \
                              pd.to_numeric(df['DGASPROKSM'], errors='coerce').fillna(0)
        gas_col = 'GAS_TOTAL_VOL'

        # Industry conversion rules: 1 m3 oil = ~6.29 bbl | 1,000 m3 gas = ~6.11 boe
        df['TOTAL_BOE_OUTPUT'] = (pd.to_numeric(df[oil_col], errors='coerce').fillna(0) * 6.29) + \
                                 (df[gas_col] * 6.11)
    else:
        print("Mapping standard mock/generic schema...")
        field_col = [c for c in df.columns if 'FIELD' in c][0]
        oil_col = [c for c in df.columns if 'OIL' in c][0]
        gas_col = [c for c in df.columns if 'GAS' in c][0]

        df[oil_col] = pd.to_numeric(df[oil_col], errors='coerce').fillna(0)
        df[gas_col] = pd.to_numeric(df[gas_col], errors='coerce').fillna(0)
        df['TOTAL_BOE_OUTPUT'] = df[oil_col] + (df[gas_col] / 5.8)

    # Categorize fields based on dynamic volumetric thresholds
    def assign_status(row):
        if row['TOTAL_BOE_OUTPUT'] == 0:
            return 'Shut-In / Suspended'
        elif row[oil_col] > 0 and row[gas_col] == 0:
            return 'Pure Oil Production'
        elif row[gas_col] > 0 and row[oil_col] == 0:
            return 'Pure Gas Production'
        else:
            return 'Active Co-Production'

    df['OPERATIONAL_STATUS'] = df.apply(assign_status, axis=1)

    # Calculate GOR safely to prevent division by zero runtime crashes
    df['GAS_OIL_RATIO'] = df.apply(
        lambda r: r[gas_col] / r[oil_col] if r[oil_col] > 0 else 0, axis=1
    )

    # Aggregate granular field elements to generate basin macro summaries
    print("Summarizing field layers into basin-level aggregates...")
    macro_summary = df.groupby(['OPERATIONAL_STATUS']).agg(
        TOTAL_FIELDS=(field_col, 'nunique'),
        AGGREGATE_OIL_VOL=(oil_col, 'sum'),
        AGGREGATE_GAS_VOL=(gas_col, 'sum'),
        MEAN_GOR=('GAS_OIL_RATIO', 'mean')
    ).reset_index()

    return macro_summary


if __name__ == "__main__":
    # Execute structural pipeline
    data = get_raw_data()
    summary = run_basin_pipeline(data)

    # Present formatted terminal matrix
    print("\n" + "=" * 65)
    print("   EIA REPRODUCIBLE MODELING FRAMEWORK: FIELD PRODUCTION SUMMARY")
    print("=" * 65)
    print(summary.to_string(index=False))
    print("=" * 65)

    # Persist data layer
    summary.to_csv("macro_basin_production_summary.csv", index=False)
    print("Pipeline run completed successfully.")