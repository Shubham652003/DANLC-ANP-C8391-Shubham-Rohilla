import pandas as pd
import streamlit as st
import plotly.express as px

# Set the layout for the Streamlit page
st.set_page_config(layout="wide")

# Load the dataset
df = pd.read_csv("data.csv")

# List of important columns based on the dataset provided
necessary_columns = [
    'State', 'District', 'Population', 'Male', 'Female',
    'Literate', 'Female_Literate', 'Male_Literate', 
    'Latitude', 'Longitude', 'Total_Power_Parity', 
    'Power_Parity_Above_Rs_545000', 'Power_Parity_Rs_90000_150000'
]

# Filter the dataset for necessary columns
df = df[necessary_columns]

# Add calculated columns
df['Sex Ratio'] = (df['Female'] / df['Male']) * 1000  # Sex ratio calculation
df['Literacy Rate'] = (df['Literate'] / df['Population']) * 100  # Overall literacy rate
df['Female Literacy Rate'] = (df['Female_Literate'] / df['Female']) * 100  # Female literacy rate
df['Male Literacy Rate'] = (df['Male_Literate'] / df['Male']) * 100  # Male literacy rate

# List of states for selection
list_of_state = list(df["State"].unique())
list_of_state.insert(0, "Overall India")  # Start with "Overall India"

# Sidebar title and user inputs
st.sidebar.title("India Data Visualization")
selected_state = st.sidebar.selectbox("Select a state", list_of_state)

# Select primary and secondary parameters from the necessary columns and calculated columns
primary_options = [
    'Population', 'Male', 'Female', 'Sex Ratio', 'Literacy Rate', 'Female Literacy Rate', 
    'Male Literacy Rate', 'Total_Power_Parity', 'Latitude', 'Longitude',
    'Power_Parity_Above_Rs_545000', 'Power_Parity_Rs_90000_150000'
]

chart_options = ["Select Chart", "Bar Chart", "Line Chart", "Pie Chart", "Histogram", "Mapbox"]
primary = st.sidebar.selectbox("Select Primary Parameter", primary_options)
secondary = st.sidebar.selectbox("Select Secondary Parameter", primary_options)
chart_type = st.sidebar.selectbox("Select Chart Type", chart_options)
plot_button = st.sidebar.button("Plot")  # Keep plot button location as it is

# Display a big title and introductory text if no state is selected
if selected_state == "Overall India" and chart_type == "Select Chart":
    st.markdown("<h1 style='text-align: center; color: black;'>India Data Visualization</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Welcome to the India Data Visualization Dashboard!</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Please select a state and chart type from the sidebar to begin exploring the data.</p>", unsafe_allow_html=True)
else:
    # Filter data based on user selection
    if selected_state == "Overall India":
        # Create a summary DataFrame for each state with required aggregations and calculated columns
        df_state = df.groupby('State').agg({
            'Population': 'sum',
            'Male': 'sum',
            'Female': 'sum',
            'Literate': 'sum',
            'Female_Literate': 'sum',
            'Male_Literate': 'sum',
            'Total_Power_Parity': 'sum',
            'Power_Parity_Above_Rs_545000': 'sum',
            'Power_Parity_Rs_90000_150000': 'sum',
            'Latitude': 'mean',
            'Longitude': 'mean'
        }).reset_index()

        # Add calculated columns for 'Sex Ratio', 'Literacy Rate', 'Female Literacy Rate', 'Male Literacy Rate'
        df_state['Sex Ratio'] = (df_state['Female'] / df_state['Male']) * 1000
        df_state['Literacy Rate'] = (df_state['Literate'] / df_state['Population']) * 100
        df_state['Female Literacy Rate'] = (df_state['Female_Literate'] / df_state['Female']) * 100
        df_state['Male Literacy Rate'] = (df_state['Male_Literate'] / df_state['Male']) * 100

        # Drop intermediate columns used for calculations
        df_state = df_state.drop(columns=['Literate', 'Female_Literate', 'Male_Literate'])
        x_axis_label = "State"  # Use "State" as x-axis label for "Overall India"

    else:
        # Filter data for the selected state
        df_state = df[df["State"] == selected_state].dropna(subset=["Latitude", "Longitude"])
        x_axis_label = "District"  # Use "District" as x-axis label for specific states

    # Visualization based on user selection
    if plot_button:
        st.markdown(f"**Primary Parameter:** {primary} represents the selected primary metric for the visualization.")
        st.markdown(f"**Secondary Parameter:** {secondary} represents the selected secondary metric for comparison.")
        
        if chart_type == "Bar Chart":
            # Create a grouped bar plot
            fig = px.bar(df_state, x=x_axis_label, y=[primary, secondary], barmode="group",
                         title=f"Comparison of {primary} and {secondary} in {selected_state}",
                         labels={primary: primary, secondary: secondary})
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Line Chart":
            # Create a line plot
            fig = px.line(df_state, x=x_axis_label, y=[primary, secondary],
                          title=f"Trend of {primary} and {secondary} in {selected_state}",
                          labels={primary: primary, secondary: secondary})
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Pie Chart":
            # Create a pie chart
            fig = px.pie(df_state, values=primary, names=x_axis_label, title=f"{primary} Distribution in {selected_state}")
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Histogram":
            # Create a histogram
            fig = px.histogram(df_state, x=primary, title=f"Histogram of {primary} in {selected_state}",
                               labels={primary: primary})
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == "Mapbox":
            # Add markdown for Mapbox size and color explanation
            st.markdown(f"Map visualization where **size** represents `{primary}` and **color** represents `{secondary}`.")
            
            # Mapbox visualization
            if 'Latitude' in df_state.columns and 'Longitude' in df_state.columns:
                fig = px.scatter_mapbox(
                    df_state,
                    lat="Latitude", 
                    lon="Longitude", 
                    size=primary,  
                    color=secondary,  
                    hover_name="State",  
                    title=f"Mapbox Visualization of {primary} and {secondary} in {selected_state}",
                    mapbox_style="open-street-map", 
                    zoom=4,  
                    center={"lat": df_state["Latitude"].mean(), "lon": df_state["Longitude"].mean()}  
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Latitude and Longitude columns are missing from the dataset.")
