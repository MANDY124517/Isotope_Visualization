import streamlit as st
import pandas as pd
try:
    import plotly.express as px
except ImportError:
    # Fallback import method
    import plotly
    import plotly.graph_objects as go
    import plotly.express as px
import pydeck as pdk
import numpy as np
from io import StringIO

# Configure page
st.set_page_config(
    page_title="Global Isotope Production",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); }
    h1, h2, h3 { color: #4fc3f7; }
    .stSelectbox, .stSlider, .stMultiSelect { background-color: rgba(25, 55, 75, 0.7); }
    .stButton>button { background: linear-gradient(to right, #2193b0, #6dd5ed); color: white; border: none; }
    .stDataFrame { background-color: rgba(255, 255, 255, 0.1); }
    .stTab [aria-selected="true"] { background-color: #2193b0 !important; color: white !important; }
    .css-1aumxhk { background-color: rgba(15, 30, 45, 0.8); }
</style>
""", unsafe_allow_html=True)

# Country coordinates mapping
COUNTRY_COORDS = {
    "Australia": {"lat": -25.27, "lon": 133.78},
    "Austria": {"lat": 47.52, "lon": 14.55},
    "Belarus": {"lat": 53.71, "lon": 27.95},
    "Belgium": {"lat": 50.50, "lon": 4.47},
    "Brazil": {"lat": -14.24, "lon": -51.93},
    "Chile": {"lat": -35.68, "lon": -71.54},
    "Czech Republic": {"lat": 49.82, "lon": 15.47},
    "Egypt": {"lat": 26.82, "lon": 30.80},
    "European Commission": {"lat": 50.85, "lon": 4.35},  # Brussels
    "Finland": {"lat": 61.92, "lon": 25.75},
    "France": {"lat": 46.23, "lon": 2.21},
    "Germany": {"lat": 51.17, "lon": 10.45},
    "India": {"lat": 20.59, "lon": 78.96},
    "Indonesia": {"lat": -0.79, "lon": 113.92},
    "Iran": {"lat": 32.43, "lon": 53.69},
    "Japan": {"lat": 36.20, "lon": 138.25},
    "Korea": {"lat": 35.91, "lon": 127.77},  # South Korea
    "Pakistan": {"lat": 30.38, "lon": 69.35},
    "South Africa": {"lat": -30.56, "lon": 22.94},
    "Spain": {"lat": 40.46, "lon": -3.75},
    "Switzerland": {"lat": 46.82, "lon": 8.23},
    "Syria": {"lat": 34.80, "lon": 38.99},
    "Turkey": {"lat": 38.96, "lon": 35.24},
    "USA": {"lat": 37.09, "lon": -95.71}
}

# ISO country codes mapping
ISO_CODES = {
    "Australia": "AUS",
    "Austria": "AUT",
    "Belarus": "BLR",
    "Belgium": "BEL",
    "Brazil": "BRA",
    "Chile": "CHL",
    "Czech Republic": "CZE",
    "Egypt": "EGY",
    "European Commission": "EUR",  # Custom code
    "Finland": "FIN",
    "France": "FRA",
    "Germany": "DEU",
    "India": "IND",
    "Indonesia": "IDN",
    "Iran": "IRN",
    "Japan": "JPN",
    "Korea": "KOR",
    "Pakistan": "PAK",
    "South Africa": "ZAF",
    "Spain": "ESP",
    "Switzerland": "CHE",
    "Syria": "SYR",
    "Turkey": "TUR",
    "USA": "USA"
}

# Main app
def main():
    st.title("🌍 Global Isotope Production Dashboard")
    st.markdown("Visualize worldwide production of medical and industrial isotopes")
    
    # Load data section
    st.subheader("Isotope Production Data")
    st.info("Using dataset: isotope_production_by_country_2002.csv")
    
    # Replace the sample_data section with:
uploaded_file = st.file_uploader("D:/lenovo/data visuals/isotope_production_by_country_2002.csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("D:/lenovo/data visuals/isotope_production_by_country_2002.csv")  # Use sample if no upload
    
    # Load data
    df = pd.read_csv("D:/lenovo/data visuals/isotope_production_by_country_2002.csv")
    
    # Data cleaning
    # Convert "NR" to NaN and handle zeros
    df['Total_Production_TBq'] = pd.to_numeric(df['Total_Production_TBq'], errors='coerce')
    df['Total_Production_TBq'].fillna(0, inplace=True)
    
    # Add coordinates and ISO codes
    df['Latitude'] = df['Country'].map(lambda x: COUNTRY_COORDS.get(x, {}).get('lat', 0))
    df['Longitude'] = df['Country'].map(lambda x: COUNTRY_COORDS.get(x, {}).get('lon', 0))
    df['ISO'] = df['Country'].map(lambda x: ISO_CODES.get(x, ''))
    
    # Create isotope lists
    df['Isotope_List'] = df['Major_Isotopes'].apply(
        lambda x: [iso.strip() for iso in x.split(',')] if isinstance(x, str) else []
    )
    
    # Filters
    st.sidebar.header("Filters")
    min_production = st.sidebar.slider(
        "Minimum Production (TBq)", 
        0, 
        int(df['Total_Production_TBq'].max()) + 1000,
        100
    )
    
    selected_countries = st.sidebar.multiselect(
        "Select Countries", 
        df['Country'].unique(),
        default=df['Country'].unique()[:5]
    )
    
    # Apply filters
    filtered_df = df[
        (df['Total_Production_TBq'] >= min_production) &
        (df['Country'].isin(selected_countries))
    ]
    
    # Main visualization tabs
    tab1, tab2, tab3 = st.tabs(["World Production Map", "Country Comparison", "Isotope Analysis"])
    
    with tab1:
        st.header("Global Isotope Production Map")
        st.caption("Bubble size represents production volume")
        
        # Calculate viewport
        lat = filtered_df['Latitude'].mean() if not filtered_df.empty else 0
        lon = filtered_df['Longitude'].mean() if not filtered_df.empty else 0
        
        # Create PyDeck map
        layer = pdk.Layer(
            "ScatterplotLayer",
            filtered_df,
            get_position=['Longitude', 'Latitude'],
            get_radius='Total_Production_TBq/20',
            get_fill_color=[255, 200, 0, 180],
            pickable=True,
            auto_highlight=True,
            radius_min_pixels=5,
            radius_max_pixels=100,
        )
        
        view_state = pdk.ViewState(
            latitude=lat,
            longitude=lon,
            zoom=1,
            pitch=0,
        )
        
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>{Country}</b><br>"
                        "Production: {Total_Production_TBq} TBq<br>"
                        "Major Isotopes: {Major_Isotopes}",
                "style": {"backgroundColor": "steelblue", "color": "white"}
            }
        )
        
        st.pydeck_chart(deck)
        
        # Add choropleth map
        st.subheader("Production by Country")
        fig = px.choropleth(
            filtered_df,
            locations="ISO",
            color="Total_Production_TBq",
            hover_name="Country",
            hover_data=["Major_Isotopes", "Total_Production_TBq"],
            projection="natural earth",
            color_continuous_scale=px.colors.sequential.Plasma,
            height=500,
            title="Global Isotope Production (TBq)"
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Country Comparison")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Producing Countries")
            top_countries = filtered_df.sort_values('Total_Production_TBq', ascending=False).head(10)
            fig = px.bar(
                top_countries,
                x='Total_Production_TBq',
                y='Country',
                orientation='h',
                color='Total_Production_TBq',
                text='Total_Production_TBq',
                height=500,
                title="Top 10 Isotope Producing Countries"
            )
            fig.update_traces(texttemplate='%{text:.2s} TBq', textposition='outside')
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Production Distribution")
            fig = px.pie(
                filtered_df,
                values='Total_Production_TBq',
                names='Country',
                height=500,
                title="Share of Global Isotope Production"
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Detailed Production Data")
        st.dataframe(filtered_df[['Country', 'Major_Isotopes', 'Total_Production_TBq']]
                     .sort_values('Total_Production_TBq', ascending=False)
                     .style.format({'Total_Production_TBq': '{:,.1f} TBq'})
                     .background_gradient(cmap='Blues', subset=['Total_Production_TBq']), 
                     height=400)
    
    with tab3:
        st.header("Isotope Analysis")
        
        # Create a list of all isotopes
        all_isotopes = []
        for isotopes in df['Isotope_List']:
            all_isotopes.extend(isotopes)
        
        isotope_counts = pd.Series(all_isotopes).value_counts().reset_index()
        isotope_counts.columns = ['Isotope', 'Count']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Most Common Isotopes")
            fig = px.bar(
                isotope_counts.head(10),
                x='Count',
                y='Isotope',
                orientation='h',
                color='Count',
                height=400,
                title="Top 10 Isotopes by Country Production"
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Isotope Production Network")
            st.markdown("""
            **Key Isotopes and Their Producers:**
            - Medical Imaging: Tc-99m, I-131
            - Industrial: Ir-192, Co-60
            - Research: C-11, F-18
            """)
            
            # Create isotope-country matrix
            isotope_matrix = []
            for _, row in filtered_df.iterrows():
                for isotope in row['Isotope_List']:
                    isotope_matrix.append({
                        'Isotope': isotope,
                        'Country': row['Country'],
                        'Production': row['Total_Production_TBq']
                    })
            
            if isotope_matrix:
                matrix_df = pd.DataFrame(isotope_matrix)
                fig = px.treemap(
                    matrix_df,
                    path=['Isotope', 'Country'],
                    values='Production',
                    color='Production',
                    color_continuous_scale='RdYlGn',
                    height=400,
                    title="Isotope Production by Country"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No isotope data available for selected countries")
        
        st.subheader("Isotope Production Details")
        st.markdown("""
        | Isotope | Common Applications | Top Producers |
        |---------|----------------------|---------------|
        | **Tc-99m** | Medical imaging | Belgium, India, Chile |
        | **I-131** | Thyroid treatment | Belgium, Iran, Korea |
        | **Ir-192** | Industrial radiography | Australia, Japan, USA |
        | **Mo-99** | Parent for Tc-99m | Belgium, South Africa |
        | **F-18** | PET scans | Austria, Switzerland, Turkey |
        | **Co-60** | Sterilization, cancer therapy | India, Russia, Canada |
        """)

if __name__ == "__main__":
    main()