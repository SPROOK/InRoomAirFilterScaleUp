USE BELOW FOR CREATING COUNTRY CLASSES

"
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

def generate_countries(country_csv_path, cr_box_csv_path=None):
    """
    Generate a dictionary of Country objects from a CSV of country names.
    Optionally load CR_Box properties from a separate CSV.
    
    Returns:
        dict: {country_name: Country instance}
    """
    # Load the CSV with the list of countries
    df = pd.read_csv(country_csv_path)
    
    if 'Country' not in df.columns:
        raise ValueError("CSV must have a column named 'Country'")
    
    countries = {}
    for name in df['Country']:
        c = Country(name)
        if cr_box_csv_path:
            c.load_properties_from_csv(cr_box_csv_path, country_col="Country")
        countries[c.name] = c
    return countries

from country_pkg import Country
"