USE BELOW FOR CREATING COUNTRY CLASSES






import sys
import country_converter as coco
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

country_list_csv = BASE_DIR / "data" / "STANDARD_COUNTRY_LIST.csv"

def generate_countries_from_multiple_csvs(
    country_csv_path,
    cr_box_csv_path=None,
    ecw_csv_path=None
):
    # ---------------- Main country CSV ----------------
    df = pd.read_csv(country_csv_path, encoding='cp1252')
    required_cols = ['ISO-3', 'Country Name']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"CSV must have a column named '{col}'")
    
    # ---------------- CR Box CSV ----------------
    cr_box_df = None
    if cr_box_csv_path:
        cr_box_df = pd.read_csv(cr_box_csv_path, encoding='cp1252')
        if "Country" not in cr_box_df.columns:
            raise ValueError("CR Box CSV must have a 'Country' column")
        cr_box_df["Country"] = cr_box_df["Country"].apply(Country._cc.convert, to="name_short")
    
    # ---------------- ECW CSV ----------------
    ecw_df = None
    if ecw_csv_path:
        ecw_df = pd.read_csv(ecw_csv_path, encoding='cp1252')
        required_ecw_cols = ['Country Name', 'Country Code']
        for col in required_ecw_cols:
            if col not in ecw_df.columns:
                raise ValueError(f"ECW CSV must have a column named '{col}'")
    
    countries = {}
    
    for _, row in df.iterrows():
        iso_code = row['ISO-3']
        country_name = row['Country Name']
        
        # Create country object
        c = Country(name=iso_code)
        c.properties['ISO-3'] = iso_code
        
        # ---------------- Merge CR Box properties ----------------
        if cr_box_df is not None:
            standardized_name = Country._cc.convert(country_name, to="name_short")
            cr_row = cr_box_df[cr_box_df["Country"] == standardized_name]
            if not cr_row.empty:
                for col in cr_row.columns:
                    if col != "Country":
                        c.properties[col] = cr_row.iloc[0][col]
            else:
                for col in cr_box_df.columns:
                    if col != "Country":
                        c.properties[col] = 0
        
        # ---------------- Merge ECW properties ----------------
        if ecw_df is not None:
            ecw_row = ecw_df[ecw_df["Country Code"] == iso_code]
            if not ecw_row.empty:
                for col in ecw_row.columns:
                    if col != "Country Code":
                        if col != "Country Name":
                            c.properties[col] = ecw_row.iloc[0][col]
        
        countries[iso_code] = c
    
    return countries


from country_pkg import Country
