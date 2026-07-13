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

# Load the insurance dataset and prepare it for analysis
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
    sorted(df["Device Category"].unique()),
    default=sorted(df["Device Category"].unique())
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

# Calculate key performance indicators for the dashboard
users = int(filtered_df["Users"].sum())
revenue = filtered_df["Revenue"].sum()
quotes = int(filtered_df["Insurance Quotes"].sum())
policies = int(filtered_df["Policies Purchased"].sum())
if users > 0:
    conversion = (policies / users)*100
else:
    conversion = 0


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


# Create marketing channel analysis visualisations
left,right = st.columns(2)
with left:
    channel_users = (
    filtered_df.groupby("Marketing Channel")["Users"]
    .sum()
    .reset_index()
)

channel_users = channel_users.sort_values(
    "Users",
    ascending=False
)

fig = px.bar(
    channel_users,
    x="Marketing Channel",
    y="Users",
    title="Users by Marketing Channel",
    text="Users"
)

fig.update_traces(
    textposition="outside"
)

fig.update_layout(
    template="plotly_white",
    xaxis_title="Marketing Channel",
    yaxis_title="Users"
)

st.plotly_chart(
    fig,
    use_container_width=True
)
with right:
    revenue_channel = (
    filtered_df.groupby("Marketing Channel")["Revenue"]
    .sum()
    .reset_index()
)

revenue_channel = revenue_channel.sort_values(
    "Revenue",
    ascending=True
)


fig = px.bar(
    revenue_channel,
    x="Revenue",
    y="Marketing Channel",
    orientation="h",
    title="Revenue by Marketing Channel",
    text="Revenue"
)


fig.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside"
)


fig.update_layout(
    template="plotly_white",
    xaxis_title="Revenue ($)",
    yaxis_title="Marketing Channel"
)


st.plotly_chart(
    fig,
    use_container_width=True
)

# ROW 2
left,right = st.columns(2)

with left:

    device = (
        filtered_df.groupby("Device Category")["Users"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        device,
        names="Device Category",
        values="Users",
        title="Device Category Distribution",
        hole=0.4
    )

    fig.update_traces(
        textinfo="percent+label"
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
        title="User Engagement vs Policy Purchases"
    )

    fig.update_traces(
        textposition="top center"
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Website Users",
        yaxis_title="Policies Purchased"
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


top_users = (
    filtered_df.groupby("Marketing Channel")["Users"]
    .sum()
    .idxmax()
)

top_revenue = (
    filtered_df.groupby("Marketing Channel")["Revenue"]
    .sum()
    .idxmax()
)


conversion_channel = (
    filtered_df.assign(
        Conversion=
        filtered_df["Policies Purchased"] /
        filtered_df["Users"]
    )
    .groupby("Marketing Channel")["Conversion"]
    .mean()
    .idxmax()
)


col1,col2,col3 = st.columns(3)


with col1:
    st.info(
        f"""
        Traffic Insight

        {top_users} generates the highest
        number of website users.
        """
    )


with col2:
    st.success(
        f"""
        Revenue Insight

        {top_revenue} provides the highest
        revenue contribution.
        """
    )


with col3:
    st.warning(
        f"""
        Conversion Insight

        {conversion_channel} has the strongest
        user-to-policy conversion.
        """
    )

# Data Table 
st.subheader("Filtered Dataset")
st.dataframe(filtered_df)
