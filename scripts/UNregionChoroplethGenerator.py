import pandas as pd
import plotly.express as px
import country_converter as coco

def create_un_region_choropleth(df, region_col, value_col, title="UN Regions Choropleth Map", 
                               color_scale="RdYlGn", width=1000, height=600):
    
    # Initialize country converter
    cc = coco.CountryConverter()
    
    # Create a list to store country-value pairs
    country_values = []
    
    # Process each row in the dataframe
    for _, row in df.iterrows():
        region_name = row[region_col]
        value = row[value_col]
            
        # Get countries in this UN region
        countries_in_region = cc.data[cc.data['UNregion'] == region_name]['ISO3'].tolist()
        
        # Add each country with the region's value
        for country_iso3 in countries_in_region:
            country_values.append({
                'country_code': country_iso3,
                'value': value,
                'region': region_name
            })
    
    choropleth_df = pd.DataFrame(country_values)
    
    # Create the choropleth map
    fig = px.choropleth(
        choropleth_df,
        locations='country_code',
        color='value',
        hover_name='country_code',
        hover_data={'region': True, 'value': True},
        color_continuous_scale=color_scale,
        title=title,
        labels={'value': 'Value', 'country_code': 'Country'}
    )
    
    # Update layout - SINGLE consolidated update
    fig.update_layout(
        width=width,
        height=height,
        title_x=0.5,
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showcountries=False,  # Remove country borders
            showsubunits=False,   # Remove state/province borders
            projection_type='natural earth'
        )
    )
    
    # Remove borders between colored regions
    fig.update_traces(marker_line_width=0)
    
    return fig