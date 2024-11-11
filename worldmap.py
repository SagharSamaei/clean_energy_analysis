import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd 
import pandas as pd  
import numpy as np    
import plotly.express as px  
from PIL import Image 
import plotly.graph_objects as go  
import altair as alt 

#page configuration
st.set_page_config( 
    page_title= "Energy Analysis Dashboard", 
    page_icon="🔋",  
    layout= "wide", 
    initial_sidebar_state= "expanded" 
) 
# Sidebar
st.sidebar.title("Dashboard Contents")
sidebar_image = Image.open("C:/Users/Sayan/Documents/Saghar/Bootcamp/Energy1.jpeg") 
st.sidebar.image(sidebar_image, use_column_width= True) 

alt.themes.enable("dark") 
st.title(f"Clean Energy Production Time series Analysis")  
st.markdown(""" 
This dashboard provides a detailed overview of various energy production trends in the world but also in details in th selected country. Navigate using the sidebar to choose a different country. 
""")
 
# Loading file and converting the date into the right format   
data = pd.read_csv("C:/Users/Sayan/Documents/Saghar/Bootcamp/Panel format (2).csv") 
data["Year"] = pd.to_datetime(data["Year"],format="%Y")
data['Year'] = data['Year'].dt.year
name_corrections = {
    "US": "United States of America",
    "Turkiye": "Turkey",
    "Czech Republic": "Czechia",
    "Russian Federation": "Russia",
    "Democratic Republic of Congo": "Democratic Republic of the Congo",
    "Republic of Congo": "Republic of the Congo",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "China Hong Kong SAR": "Hong Kong",
    "Serbia": "Republic of Serbia",
}
data['Country'] = data['Country'].replace(name_corrections)


# Section 1
st.markdown("---")
st.markdown("<a name='section1'></a>", unsafe_allow_html=True)
st.header("Analysis of clean energy in a country")
st.write("Click on a country to select it.")

# Creating the map and selecting the country
@st.cache_data 
def load_geodata():
    world = gpd.read_file(r"C:/Users/Sayan/Documents/Saghar/Bootcamp/ne_110m_admin_0_countries.shp")
    return world

def create_map(world):
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="cartodb positron")
    
    def on_click(feature):
        feature_name = feature["properties"]["ADMIN"]
        feature["properties"]["style"] = {"fillColor": "#0078FF"}
        folium.map.Marker(
            [feature["geometry"]["coordinates"][1], feature["geometry"]["coordinates"][0]],
            popup=feature_name,
        ).add_to(m)

    folium.GeoJson(
        world,
        name="Countries",
        tooltip=folium.GeoJsonTooltip(fields=["ADMIN"]),
        highlight_function=lambda x: {"weight": 3, "color": "#FFDD44"},
        popup=on_click
    ).add_to(m)
    return m

world_data = load_geodata()
with st.container():
    # Create and display the map
    folium_map = create_map(world_data)
    output = st_folium(folium_map, width=700, height=500)

    # Check if there is a valid selection in the output before accessing it
    if output and output.get("last_active_drawing") and output["last_active_drawing"].get("properties"):
        country = output["last_active_drawing"]["properties"]["ADMIN"]
        st.write(f"**Selected Country:** {country}")

    else:
        country = None
        st.write("No country selected.")


# Check if the specified country exists in the DataFrame
if country in data["Country"].values:
    # Filter data for the specific country
    country_data = data[data["Country"] == country] 

    # Subsection 1.1
    st.markdown("<a name='subsection1.1'></a>", unsafe_allow_html=True)
    st.subheader(f"Analysis of clean energy for {country}")
    st.markdown("---")
      

    def create_chart(data, y, title, yaxis_title): 
        fig = px.line(
            data, 
            x="Year", 
            y=y, 
            title=title, 
            markers=True, 
            line_shape="spline", 
            color_discrete_sequence=px.colors.qualitative.Dark24 
        ) 

        fig.add_annotation(
            x=data['Year'].iloc[-1],  
            y=data[y].iloc[-1],  
            text="Latest Value",  
            showarrow=True,  
            arrowhead=2, 
            font=dict(color="#E74C3C", size=12) 
        )

        fig.update_layout(
            xaxis_title='Year', 
            yaxis_title=yaxis_title, 
            template='plotly_white', 
            font=dict(family="Arial, sans-serif", size=16, color="#2C3E50"), 
            title=dict(text=title, font=dict(size=22)), 
            margin=dict(l=0, r=0, t=80, b=0), 
            legend=dict(title="Legend", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), 
            hovermode="x unified", 
            xaxis=dict(rangeslider=dict(visible=True), showline=True, linewidth=2, linecolor='black', mirror=True, gridcolor='LightGrey'), 
            yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True, gridcolor='LightGrey')
        )

        fig.update_traces(hovertemplate='<b>Year</b>: %{x}<br><b>Value</b>: %{y}<extra></extra>') 

        with st.expander(f"Click to view the chart: {title}"):
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Population Over Time") 
    create_chart(country_data, 'pop', 'Population over Time', 'Population (in millions)') 

    # Subsection 1.2
    st.markdown("<a name='subsection1.2'></a>", unsafe_allow_html=True)
    st.subheader("♻️ Clean Energy Over Time")
    
    energy_options = {
        "Hydro Energy": ("hydro_ej", "Hydro Energy Production (Exajoules)"),
        "Nuclear Energy": ("nuclear_ej", "Nuclear Energy Production (Exajoules)"),
        "Renewable Energy": ("ren_power_ej", "Renewable Energy Production (Exajoules)"),
        "Solar Energy": ("solar_ej", "Solar Energy Production (Exajoules)")
    }

    # Multi-select dropdown for clean energy types
    selected_energy_types = st.multiselect(
        "Select up to 4 energy types to display:",
        options=list(energy_options.keys()),
        max_selections=4
    )

    # Function to create a combined chart for selected energy types
    def create_combined_chart(data, selected_energy_types):
        fig = go.Figure()

        for energy in selected_energy_types:
            column, y_axis_title = energy_options[energy]
            
            fig.add_trace(go.Scatter(
                x=data["Year"],
                y=data[column],
                mode="lines+markers",
                name=energy,
                line_shape="spline"
            ))

        fig.update_layout(
            title="Energy Production Trends Over Time",
            xaxis_title="Year",
            yaxis_title="Energy Production (Exajoules)",
            template="plotly_white",
            font=dict(family="Arial, sans-serif", size=16, color="#2C3E50"),
            title_font=dict(size=22),
            margin=dict(l=0, r=0, t=80, b=0),
            legend=dict(
                title="Energy Types",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified",
            xaxis=dict(rangeslider=dict(visible=True), showline=True, linewidth=2, linecolor='black', mirror=True, gridcolor='LightGrey'),
            yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=True, gridcolor='LightGrey')
        )

        fig.update_traces(hovertemplate='<b>Year</b>: %{x}<br><b>Value</b>: %{y}<extra></extra>') 

        with st.expander("Click to view the combined chart of selected energy types"):
            st.plotly_chart(fig, use_container_width=True)

    # Call the function to display the combined chart
    create_combined_chart(country_data, selected_energy_types)
else:
    st.write(f"No available data for {country}")


# Section 2
st.markdown("---")
st.markdown("<a name='section2'></a>", unsafe_allow_html=True)
st.header("Analysis of clean energy in a Region")
region = st.selectbox("Select a Region:", data["Region"].unique())  
year = st.selectbox("Select the year of interest:", data["Year"].unique())

# Subsection 2.1
st.markdown("<a name='subsection2.1'></a>", unsafe_allow_html=True)
title = f"Top Energy Producers in {region} for {year}"
st.subheader(f'🏆 {title}')

# Function to get top 5 countries by production for a specific energy type
def get_top_5_countries(df, energy_type):
    top_5 = df[['Country', energy_type]].dropna().nlargest(5, energy_type)
    return top_5

# Filter data for the selected region and year
filtered_data = data[(data['Region'] == region) & (data['Year'] == year)]

# Energy type options
energy_types_options = {
    'hydro_ej': 'Hydro Energy Production',
    'nuclear_ej': 'Nuclear Energy Production',
    'ren_power_ej': 'Renewable Energy Production',
    'solar_ej': 'Solar Energy Production'
}

# Single-select for energy types
selected_energy_type = st.selectbox("Select an energy type to display:", options=list(energy_types_options.keys()))

# Get top 5 producers for the selected energy type
top_5_data = get_top_5_countries(filtered_data, selected_energy_type)

# Plot the selected energy type in an expander
with st.expander(f"Click to view the top 5 producers for {energy_types_options[selected_energy_type]} in {region} ({year}):"):
    fig = px.bar(top_5_data, x='Country', y=selected_energy_type,
                 title=f"Top 5 Producers of {energy_types_options[selected_energy_type]} in {region} ({year})",
                 labels={'value': 'Energy Production (Exajoules)', 'Country': 'Country'},
                 color='Country')
    st.plotly_chart(fig, use_container_width=True)


# Section 3
st.markdown("---")
st.markdown("<a name='section3'></a>", unsafe_allow_html=True)
st.header(f"Analysis of clean energy in the World") 
main_image = Image.open("C:/Users/Sayan/Documents/Saghar/Bootcamp/clean_energy.jpg") 
st.image(main_image , width=500)

# Subsection 3.1
st.markdown("<a name='section3.1'></a>", unsafe_allow_html=True)
title = 'Average Population of the countries Per Region'
st.subheader(f'🌍 {title}')
df_region_pop = data.groupby('Region')['pop'].mean().reset_index()
fig = px.bar(df_region_pop, x='Region', y='pop', title=f'🌍 {title}')
fig.update_layout(xaxis_title='Region', yaxis_title='Average Population (in millions)')
with st.expander(f"Click to view the chart: {title}"):
    st.plotly_chart(fig, use_container_width=True) 

# # Subsection 3.2
st.markdown("<a name='section3.2'></a>", unsafe_allow_html=True)
title = 'Clean Energy Production by Region'
st.subheader(f'🔋 {title}')
df_energy = data[data['Year'] == year].groupby('Region')[['hydro_ej', 'nuclear_ej', 'solar_ej', 'renewables_ej']].sum().reset_index()
fig = px.bar(df_energy, x='Region', y=['hydro_ej', 'nuclear_ej', 'solar_ej', 'renewables_ej'], title= f'🔋 {title}')
fig.update_layout(xaxis_title='Region', yaxis_title='Energy Consumption (in exajoules)')
with st.expander(f"Click to view the chart: {title}"):
    st.plotly_chart(fig, use_container_width=True)

## Subsection 3.3
st.markdown("<a name='section3.3'></a>", unsafe_allow_html=True)
title = 'Clean Energy Production over the time'
st.subheader(f'📊 {title}')
df_energy_mix = data.groupby('Year')[['hydro_ej', 'nuclear_ej', 'solar_ej', 'renewables_ej']].sum().reset_index()
fig = px.bar(df_energy_mix, x='Year', y=['hydro_ej', 'nuclear_ej', 'solar_ej', 'renewables_ej'],
             title=f'📊 {title}', labels={'value': 'Energy (in exajoules)', 'variable': 'Energy Type'})
with st.expander(f"Click to view the chart: {title}"):
    st.plotly_chart(fig, use_container_width=True)



# Adding links to each header and subheader
st.markdown(
    """
    <style>
    /* Reduce font size of sidebar markdown text */
    .css-1d391kg .markdown-text-container {
        font-size: 0.4rem; /* Adjust as needed */
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.sidebar.markdown("[Analysis of clean energy in a country](#section1)", unsafe_allow_html=True)
if country in data["Country"].values:
    st.sidebar.markdown("  - [Population Over Time](#subsection1.1)", unsafe_allow_html=True)
    st.sidebar.markdown("  - [Clean Energy Over Time](#subsection1.2)", unsafe_allow_html=True)

st.sidebar.markdown("[Analysis of clean energy in a Region](#section2)", unsafe_allow_html=True)
st.sidebar.markdown("  - [Top Energy Producers in a Region](#subsection2.1)", unsafe_allow_html=True)

st.sidebar.markdown("[Analysis of clean energy in the world](#section3)", unsafe_allow_html=True)
st.sidebar.markdown("  - [Average Population of the countries Per Region](#subsection3.1)", unsafe_allow_html=True)
st.sidebar.markdown("  - [Clean Energy Production by Region](#subsection3.2)", unsafe_allow_html=True)
st.sidebar.markdown("  - [Clean Energy Production over the time](#subsection3.3)", unsafe_allow_html=True)
