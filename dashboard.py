import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="dark")

def create_daily_orders_df(df):
    daily_orders_df = (
        df.resample(rule="D", on="order_date")
        .agg({
            "order_id": "nunique",
            "total_price": "sum"
        })
        .reset_index()
    )
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)
    return daily_orders_df


def create_sum_order_items_df(df):
    return (
        df.groupby("product_name")
        .quantity_x
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )


def create_bygender_df(df):
    return (
        df.groupby("gender")
        .customer_id
        .nunique()
        .reset_index(name="customer_count")
    )


def create_byage_df(df):
    byage_df = (
        df.groupby("age_group")
        .customer_id
        .nunique()
        .reset_index(name="customer_count")
    )
    byage_df["age_group"] = pd.Categorical(
        byage_df["age_group"],
        ["Youth", "Adults", "Seniors"]
    )
    return byage_df


def create_bystate_df(df):
    return (
        df.groupby("state")
        .customer_id
        .nunique()
        .reset_index(name="customer_count")
    )


def create_rfm_df(df):
    rfm_df = (
        df.groupby("customer_id", as_index=False)
        .agg({
            "order_date": "max",
            "order_id": "nunique",
            "total_price": "sum"
        })
    )

    rfm_df.columns = [
        "customer_id",
        "max_order_timestamp",
        "frequency",
        "monetary"
    ]

    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()

    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(
        lambda x: (recent_date - x).days
    )

    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_date", "delivery_date"]
for col in datetime_columns:
    all_df[col] = pd.to_datetime(all_df[col])

all_df.sort_values(by="order_date", inplace=True)
all_df.reset_index(drop=True, inplace=True)

min_date = all_df["order_date"].min()
max_date = all_df["order_date"].max()

with st.sidebar:
    st.image(
        "https://raw.githubusercontent.com/mhvvn/dashboard_streamlit/refs/heads/main/img/tshirt.png",
        width=80
    )
    start_date, end_date = st.date_input(
        "Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_df[
    (all_df["order_date"] >= pd.to_datetime(start_date)) &
    (all_df["order_date"] <= pd.to_datetime(end_date))
]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bygender_df = create_bygender_df(main_df)
byage_df = create_byage_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)


st.header("My Collection Dashboard ✨")

st.subheader("Daily Orders")

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Orders", daily_orders_df.order_count.sum())
with col2:
    st.metric(
        "Total Revenue",
        format_currency(daily_orders_df.revenue.sum(), "AUD", locale="es_CO")
    )

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_date"], daily_orders_df["order_count"], marker="o")
st.pyplot(fig)

st.subheader("Best & Worst Performing Product")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(30, 14))

product_palette = {
    "Denim": "#90CAF9",
    "Joggers": "#0066CC",
    "Pleated": "#FFB6B6",
    "Casual Slim Fit": "#FF2D2D",
    "Shearling": "#7CFC98",
    "Mandarin Collar": "#90CAF9",
    "Dress": "#0066CC",
    "Cords": "#FFB6B6",
    "Wool": "#FF2D2D",
    "Cuban Collar": "#7CFC98"
}

best_df = sum_order_items_df.head(5)

sns.barplot(
    x="quantity_x",
    y="product_name",
    data=best_df,
    hue="product_name",
    palette=product_palette,
    dodge=False,
    ax=ax[0]
)

ax[0].set_title("Best Performing Product", fontsize=28, weight="bold")
ax[0].set_xlabel("quantity_x", fontsize=18)
ax[0].set_ylabel("product_name", fontsize=18)
ax[0].tick_params(axis="x", labelsize=14)
ax[0].tick_params(axis="y", labelsize=16)

ax[0].legend(
    title="product_name",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5)
)

worst_df = sum_order_items_df.sort_values(
    by="quantity_x", ascending=True
).head(5)

sns.barplot(
    x="quantity_x",
    y="product_name",
    data=worst_df,
    hue="product_name",
    palette=product_palette,
    dodge=False,
    ax=ax[1]
)

ax[1].set_title("Worst Performing Product", fontsize=28, weight="bold")
ax[1].set_xlabel("quantity_x", fontsize=18)
ax[1].set_ylabel("product_name", fontsize=18)
ax[1].tick_params(axis="x", labelsize=14)
ax[1].tick_params(axis="y", labelsize=16)

ax[1].legend(
    title="product_name",
    loc="center left",
    bbox_to_anchor=(1.02, 0.5)
)

st.pyplot(fig)


st.subheader("Customer Demographics")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        x="gender",
        y="customer_count",
        data=bygender_df.sort_values(by="customer_count", ascending=False),
        ax=ax
    )
    ax.set_title("Number of Customer by Gender")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(
        x="age_group",
        y="customer_count",
        data=byage_df,
        ax=ax
    )
    ax.set_title("Number of Customer by Age")
    st.pyplot(fig)

fig, ax = plt.subplots(figsize=(20, 10))

state_palette = {
    "South Australia": "#90CAF9",
    "Western Australia": "#1976D2",
    "Queensland": "#FFB6B6",
    "New South Wales": "#FF1744",
    "Victoria": "#7CFC98",
    "Northern Territory": "#2CB1A1",
    "Australian Capital Territory": "#FFD166",
    "Tasmania": "#FF8C00"
}

sns.barplot(
    x="customer_count",
    y="state",
    data=bystate_df.sort_values(by="customer_count", ascending=False),
    hue="state",
    dodge=False,
    palette=state_palette,
    ax=ax
)

ax.set_title("Number of Customer by State", fontsize=30, weight="bold")
ax.legend(title="state", bbox_to_anchor=(1.02, 1), loc="upper left")
st.pyplot(fig)


st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
col1.metric("Average Recency (days)", round(rfm_df.recency.mean(), 1))
col2.metric("Average Frequency", round(rfm_df.frequency.mean(), 2))
col3.metric("Average Monetary", format_currency(rfm_df.monetary.mean(), "AUD", locale="es_CO"))

fig, ax = plt.subplots(1, 3, figsize=(35, 15))
sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency").head(5), ax=ax[0])
sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1])
sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2])

st.pyplot(fig)

st.caption("Copyright (c) My Collection 2025")
