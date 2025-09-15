USE BELOW FOR CREATING COUNTRY CLASSES

"
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

def generate_countries_from_iso_csv(country_csv_path, cr_box_csv_path=None):
    """
    Generate a dictionary of Country objects from a CSV with ISO-3 codes and country names.
    Optionally load CR_Box properties from a separate CSV.
    """
    # Load the CSV with correct encoding
    df = pd.read_csv(country_csv_path, encoding='cp1252')
    
    required_cols = ['ISO-3', 'Country Name']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"CSV must have a column named '{col}'")
    
    countries = {}
    for _, row in df.iterrows():
        c = Country(name=row['Country Name'])
        c.properties['ISO-3'] = row['ISO-3']
        if cr_box_csv_path:
            c.load_properties_from_csv(cr_box_csv_path, country_col="Country")
        countries[c.name] = c
    
    return countries

from country_pkg import Country
"