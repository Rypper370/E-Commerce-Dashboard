import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency



def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_sum_category(df):
    sum_category_orders = df.groupby("product_category_name")["order_id"].count().reset_index()
    sum_category_orders.columns = ["product_category_name", "order_count"]
    sum_category_orders = sum_category_orders.sort_values(by="order_count", ascending=False)
    return sum_category_orders


def create_city(df):
    customers_distribution = df["customer_city"].value_counts().reset_index()
    customers_distribution.columns = ['customer_city', 'total customers']
    return customers_distribution

def create_lastPurchased(df):
    df["order_purchase_timestamp"] = pd.to_datetime(alldata["order_purchase_timestamp"])
    last_purchase = df.groupby("customer_id")["order_purchase_timestamp"].max().reset_index()
    last_purchase.head()
    return last_purchase


#load data
alldata = pd.read_csv("dashboard/alldata.csv")

datetime_columns = ["order_purchase_timestamp", "order_delivered_customer_date"]
alldata.sort_values(by="order_purchase_timestamp", inplace=True)
alldata.reset_index(drop = True, inplace=True) # menghindari kolom tambahan yang tidak perlu

for column in datetime_columns:
    alldata[column] = pd.to_datetime(alldata[column])

#filter data 2018
alldata = alldata[
    (alldata["order_purchase_timestamp"] >= "2018-01-01") &
    (alldata["order_purchase_timestamp"] <= "2018-12-31")
]

#mengurutkan data berdasarkan timestamp
alldata.sort_values(by="order_purchase_timestamp", inplace=True)
alldata.reset_index(drop=True,inplace=True)


min_date = alldata["order_purchase_timestamp"].min()
max_date = alldata["order_purchase_timestamp"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
mainData = alldata[(alldata["order_purchase_timestamp"] >= str(start_date)) & 
                (alldata["order_purchase_timestamp"] <= str(end_date))]


# Menyiapkan berbagai dataframe
dailyOrders = create_daily_orders_df(mainData)
sumCategory = create_sum_category(mainData)
city = create_city(mainData)
lastPurchased = create_lastPurchased(mainData)

#plot dailyorder 2018  
st.header("E-Commerce Sales Order Dashboard")
st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_order = dailyOrders.order_count.sum()
    st.metric("Total Order", value=total_order)

with col2:
    total_revenue = format_currency(dailyOrders.revenue.sum(), "BRL", locale='pt_BR')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(20,10))
ax.plot(
    dailyOrders["order_purchase_timestamp"],
    dailyOrders["order_count"],
    marker='o', 
    linewidth=2,
    color="skyblue"
)

ax.tick_params(axis='y', labelsize = 20)
ax.tick_params(axis='x', labelsize = 15)
st.pyplot(fig)


#plot Category product
st.subheader("Analisis Kategori Produk")

fig, ax= plt.subplots(nrows = 1, ncols=2, figsize=(35,15))

colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x = "order_count", 
    y="product_category_name",
    data=sumCategory.head(5),
    palette=colors, 
    ax=ax[0]
    )
ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Pesanan", fontsize = 30)
ax[0].set_title("Top 5 Kategorii Produk Paling Laris", loc="center", fontsize = 50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)


sns.barplot(
    x = "order_count", 
    y="product_category_name",
    data=sumCategory.sort_values(by="order_count", ascending=True).head(5),
    palette=colors, 
    ax=ax[1]
    )
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Pesanan", fontsize = 30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Top 5 Kategorii Produk Paling Tidak Laris", loc="center", fontsize = 50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

#plot city 
top10_cities = city.head(10)
st.subheader("Top 10 Kota dengan Pelanggan Terbanyak")

fig, ax = plt.subplots(figsize=(12,7))
sns.barplot(x=top10_cities["total customers"],
            y=top10_cities["customer_city"],
            palette = "mako",
            ax=ax)
ax.set_xlabel("Jumlah Pelanggan")
ax.set_ylabel("Kota")
st.pyplot(fig)


#plot lastPurchase customer 2018
st.subheader("Distribusi Waktu Transaksi Terakhir Pelanggan")
fig, ax = plt.subplots(figsize=(12,6))
sns.histplot(lastPurchased["order_purchase_timestamp"], bins=30, kde=True, color = "blue", ax=ax)
ax.set_xlabel("Jumlah Pelanggan", fontsize=12)
ax.set_ylabel("Tanggal", fontsize=12)
plt.xticks(rotation=45)
st.pyplot(fig)

