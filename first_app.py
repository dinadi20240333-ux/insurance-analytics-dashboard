import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# PAGE CONFIG 
st.set_page_config(
    page_title="Insurance Analytics Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# CUSTOM CSS
st.markdown("""
<style>
.main {
    background-color: #f8faff;
}
h1 {
    color:#12355B;
}
[data-testid="metric-container"] {
    background-color:white;
    border-radius:15px;
    padding:15px;
    box-shadow:0px 3px 10px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)


# TITLE 
st.title("🛡️ Insurance Website User Behaviour Analytics Dashboard")
st.write(
    "Interactive analysis of customer behaviour, marketing performance "
    "and insurance conversion insights."
)

# LOAD DATA 
df = pd.read_csv("insurance.data.aggregated.csv")

# Clean column values
df["Marketing Channel"] = df["Marketing Channel"].str.strip()
df["Device Category"] = df["Device Category"].str.strip()

df.rename(columns={
    "TotalNumberOfInsurancePoliciesPurchaed": "Policies Purchased",
    "TotalNumberOfInsuranceQuotes": "Insurance Quotes"
}, inplace=True)

# SIDEBAR 
st.sidebar.title("Dashboard Filters")

channels = st.sidebar.multiselect(
    "Marketing Channel",
    sorted(df["Marketing Channel"].unique()),
    default=sorted(df["Marketing Channel"].unique())
)
devices = st.sidebar.multiselect(
    "Device Category",
    df["Device Category"].unique(),
    default=df["Device Category"].unique()
)
filtered_df = df[
    (df["Marketing Channel"].isin(channels)) &
    (df["Device Category"].isin(devices))
]
if filtered_df.empty:
    st.warning("No data available")
    st.stop()

# Load image
image = Image.open("insurance.jpeg")

st.sidebar.image(image, use_container_width=True)

st.sidebar.markdown(
"""
<div style='text-align:center; margin-top:10px'>
<h4>Insurance Analytics</h4>
<p style='font-size:12px'>
Customer behaviour • Revenue • Conversion insights
</p>
</div>
""",
unsafe_allow_html=True
)

# KPI CALCULATIONS 
users = int(filtered_df["Users"].sum())
revenue = filtered_df["Revenue"].sum()
quotes = int(filtered_df["Insurance Quotes"].sum())
policies = int(filtered_df["Policies Purchased"].sum())
conversion = (policies / users)*100


# KPI CARDS 
st.subheader("Key Performance Indicators")
k1,k2,k3,k4,k5 = st.columns(5)
k1.metric(
    "Total Users",
    f"{users:,}"
)
k2.metric(
    "Revenue",
    f"${revenue:,.0f}"
)
k3.metric(
    "Quotes",
    f"{quotes:,}"
)
k4.metric(
    "Policies Purchased",
    f"{policies:,}"
)
k5.metric(
    "Conversion Rate",
    f"{conversion:.2f}%"
)


# ROW 1 CHARTS 
left,right = st.columns(2)
with left:
    channel_users = (
        filtered_df.groupby("Marketing Channel")
        ["Users"].sum()
        .reset_index()
    )
    fig = px.bar(
        channel_users,
        x="Marketing Channel",
        y="Users",
        title="Users by Marketing Channel",
        text_auto=True
    )
    fig.update_layout(
        template="plotly_white"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )
with right:
    revenue_channel = (
        filtered_df.groupby("Marketing Channel")
        ["Revenue"].sum()
        .reset_index()
    )
    fig = px.bar(
        revenue_channel,
        y="Marketing Channel",
        x="Revenue",
        orientation="h",
        title="Revenue by Marketing Channel",
        text_auto=True
    )
    fig.update_layout(
        template="plotly_white"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ROW 2
left,right = st.columns(2)
with left:
    device = (
        filtered_df.groupby("Device Category")
        ["Users"].sum()
        .reset_index()
    )
    fig = px.pie(
        device,
        names="Device Category",
        values="Users",
        title="Device Category Distribution",
        hole=0.4
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )
with right:
    scatter = (
        filtered_df.groupby("Marketing Channel")
        [["Users","Policies Purchased"]]
        .sum()
        .reset_index()
    )
    fig = px.scatter(
        scatter,
        x="Users",
        y="Policies Purchased",
        size="Policies Purchased",
        color="Marketing Channel",
        title="User Engagement vs Purchases"
    )
    st.plotly_chart(
        fig,
        use_container_width=True
    )


# FUNNEL 
st.subheader("Insurance Conversion Funnel")
fig = go.Figure(
    go.Funnel(
        y=[
            "Website Users",
            "Insurance Quotes",
            "Policies Purchased"
        ],
        x=[
            users,
            quotes,
            policies
        ]
    )
)

fig.update_layout(
    template="plotly_white"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# INSIGHTS 
st.subheader("Key Business Insights")
col1,col2,col3 = st.columns(3)
with col1:
    st.info(
        "Marketing channels can be compared to identify "
        "which sources generate the highest website traffic."
    )

with col2:
    st.success(
        "Revenue analysis helps identify channels "
        "that provide higher business value."
    )

with col3:
    st.warning(
        "Conversion rate shows how effectively users "
        "move from browsing to purchasing."
    )


# Data Table 
st.subheader("Filtered Dataset")
st.dataframe(filtered_df)