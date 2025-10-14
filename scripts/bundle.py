# make_bundle.py
import json, numpy as np, pandas as pd
from pathlib import Path

# -----------------------------
# CONFIG — file paths
# -----------------------------
file_path_main      = "../results/Scale_up_output_MS.pkl"
file_path_percent   = "../results/Scale_up_PERCENT_ECW_POLL_MS.pkl"
file_path_cr_man    = "../results/Scale_up_CR_MAN_MS.pkl"
file_path_cr_repur  = "../results/Scale_up_CR_REPUR_MS.pkl"
file_path_coalbag   = "../results/Scale_up_COALBAG_MS.pkl"
file_path_cr_stock  = "../results/Scale_up_CR_STOCK.pkl"

# If your notebook already built this mapping, you can paste it here.
# Otherwise we’ll rebuild from country_converter like your notebook does.
UNRegion_list = ['Australia and New Zealand','Caribbean','Central America','Central Asia',
                 'Eastern Africa','Eastern Asia','Eastern Europe','Melanesia','Micronesia',
                 'Middle Africa','Northern Africa','Northern America','Northern Europe',
                 'Polynesia','South America','South-eastern Asia','Southern Africa',
                 'Southern Asia','Southern Europe','Western Africa','Western Asia','Western Europe']

# -----------------------------
# Helpers
# -----------------------------
def coerce_numeric(v):
    """
    Safely make a float out of:
    - plain numbers
    - uncertainties.ufloat objects (use nominal_value)
    - strings/None -> return None
    """
    try:
        # ufloat support without importing uncertainties in this script
        # has attributes .nominal_value / .std_dev?
        nv = getattr(v, "nominal_value", None)
        if nv is not None:
            return float(nv)
        return float(v)
    except Exception:
        return None

def clean_df_numeric(df):
    """Return a copy with all numeric-like entries coerced to float, others -> None."""
    return df.applymap(coerce_numeric)

def df_to_weekmap(df):
    """
    Input: df indexed by UN region; columns are week identifiers (int/str).
    Output: dict: { region: { '1': value, '2': value, ... } }
    Only keeps numeric columns; stringifies week keys.
    """
    out = {}
    for region, row in df.iterrows():
        series = {}
        for col in row.index:
            # keep only columns that look like week numbers
            try:
                week = str(int(col))
            except Exception:
                continue
            val = coerce_numeric(row[col])
            series[week] = val
        out[region] = series
    return out

def load_nominal_pickle(path):
    """
    Load a pickle like in your notebook and return:
    - df_nominal with only week columns (drop the first 2 meta columns)
    Assumes your pickles have first 2 cols = ECW bounds, then week columns.
    """
    df = pd.read_pickle(path)
    # keep only target UN regions (same as notebook)
    df = df.loc[UNRegion_list]
    # drop 1st two metadata columns (bounds)
    # (if your pickle schema differs, adjust this slice)
    week_cols = df.columns[2:]
    df_nominal = df[week_cols].copy()
    df_nominal = clean_df_numeric(df_nominal)
    return df_nominal, week_cols

# -----------------------------
# Build region_to_iso via country_converter (like your notebook)
# -----------------------------
def build_region_to_iso():
    try:
        import country_converter as coco
    except ImportError:
        raise SystemExit("Please install country_converter: pip install country_converter")

    cc = coco.CountryConverter()
    mapping = {}
    # cc.data has columns "UNregion" and "ISO3"; some rows may have NaN
    df_cc = cc.data
    for region in UNRegion_list:
        iso_list = df_cc.loc[df_cc["UNregion"] == region, "ISO3"].dropna().tolist()
        mapping[region] = [str(x) for x in iso_list if isinstance(x, str)]
    return mapping

# -----------------------------
# MAIN
# -----------------------------
def main():
    print("[1/6] Loading datasets...")
    df_main,     wk_main     = load_nominal_pickle(file_path_main)
    df_percent,  wk_percent  = load_nominal_pickle(file_path_percent)
    df_cr_man,   wk_man      = load_nominal_pickle(file_path_cr_man)
    df_cr_repur, wk_repur    = load_nominal_pickle(file_path_cr_repur)
    df_coalbag,  wk_coal     = load_nominal_pickle(file_path_coalbag)
    df_cr_stock, wk_stock    = load_nominal_pickle(file_path_cr_stock)

    # sanity: derive weeks from the largest span we saw
    # Prefer numeric weeks 1..N in your pickles; convert to strings
    max_weeks = max(len(wk_main), len(wk_percent), len(wk_man), len(wk_repur), len(wk_coal), len(wk_stock))
    weeks = [str(i) for i in range(1, max_weeks + 1)]
    print(f"[2/6] Weeks detected: 1..{max_weeks}")

    print("[3/6] Building region_to_iso mapping...")
    region_to_iso = build_region_to_iso()

    print("[4/6] Converting dataframes to JSON structures...")
    datasets = {
        "ALL":                 df_to_weekmap(df_main),
        "ECW Coverage %":      df_to_weekmap(df_percent),
        "CR Box Manufacturing":df_to_weekmap(df_cr_man),
        "CR Box Repurposing":  df_to_weekmap(df_cr_repur),
        "Coalbaghouse":        df_to_weekmap(df_coalbag),
        "CR Box Stock":        df_to_weekmap(df_cr_stock),
    }

    print("[5/6] Extracting ECW per-person bounds (lower/upper) from main pickle...")
    # Reload main pickle (full) to read the first two columns as ECW lower/upper *per person*
    df_ecw_full = pd.read_pickle(file_path_main).loc[UNRegion_list]
    # take first two columns as [lower, upper]
    ecw_cols = df_ecw_full.columns[:2]
    ecw_per_person = {}
    for region in UNRegion_list:
        row = df_ecw_full.loc[region, ecw_cols]
        lower_pp = coerce_numeric(row.iloc[0])  # these are multipliers per person
        upper_pp = coerce_numeric(row.iloc[1])
        ecw_per_person[region] = {"lower": lower_pp, "upper": upper_pp}

    bundle = {
        "weeks": weeks,
        "un_regions": UNRegion_list,
        "region_to_iso": region_to_iso,        # { UN region: [ISO3,...] }
        "datasets": datasets,                  # { dataset_name: { region: { "1": val, ... } } }
        "ecw_per_person": ecw_per_person,      # { region: {lower:x, upper:y} }  (multiply by CADRPP in JS)
    }

    out_path = Path("data_bundle.json")
    out_path.write_text(json.dumps(bundle))
    print(f"[6/6] Wrote {out_path.resolve()}")

if __name__ == "__main__":
    main()
