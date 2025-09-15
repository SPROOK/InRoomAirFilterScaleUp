from pathlib import Path
import pandas as pd
import country_converter as coco

class Country:
    _cc = coco.CountryConverter()  # shared converter for all instances

    def __init__(self, name, properties=None):
        self.raw_name = name
        self.name = self._standardize_name(name)
        self.properties = properties if properties else {}
        self.data_loaded = False

    @classmethod
    def _standardize_name(cls, name):
        try:
            return cls._cc.convert(names=name, to='name_short')
        except Exception:
            return name  # fallback: leave name as-is
    
    def load_properties_from_csv(self, csv_path, country_col="country"):
        df = pd.read_csv(csv_path)
        df[country_col] = df[country_col].apply(self._standardize_name)
        row = df[df[country_col] == self.name]
        if not row.empty:
            self.properties.update(row.iloc[0].to_dict())

    def load_CR_Box(self):
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent
        csv_path = BASE_DIR / "data" / "CR_Box_Countries.csv"
        self.load_properties_from_csv(csv_path, country_col="Country")

    def add_property(self, key, value):
        """Manually add a property to this country"""
        self.properties[key] = value

    def __repr__(self):
        return f"<Country {self.name}, properties: {list(self.properties.keys())}>"
    
    def summary(self):
        print(f"--- {self.name} ---")
        for key, value in self.properties.items():
            print(f"{key}: {value}")

