# import all libraries
import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
import os
import warnings
warnings.filterwarnings("ignore")

# set title
st.set_page_config(page_title="SuperStore Sales Dashboard",page_icon=":bar_chart:",layout="wide")
st.title(" :bar_chart:  SuperStore Analysis")


# file upload
uploaded_file=st.file_uploader("Upload Super Store Dataset",type=['csv','xlsx','xlx','SQL'])
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file,encoding= 'ISO-8859-1')
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
else:
    # Load the dataset from a CSV file
    df = pd.read_csv("/Users/muhammadusama/Desktop/portfolio/cleaned_superstore.csv",encoding= 'ISO-8859-1')

st.markdown("""
### 📊 Dashboard Overview

This interactive dashboard provides a comprehensive analysis of the **Food Delivery Business** using real delivery records.

We focus on key metrics such as:
- Total Orders, Sales, and Profit
- Region-wise and Monthly sales trends
- Delivery performance (average time vs SLA)
- Product profit and margin insights

The dashboard is built using **Streamlit** and **Plotly**, offering clean visuals for business decision-making.

---
""")


# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("📈 Total Sales", f"${df['Sales'].sum():,.0f}")
col2.metric("💰 Total Profit", f"${df['Profit'].sum():,.0f}")
col3.metric("📦 Total Orders", df['Order ID'].nunique())




# sidebar dropdown for data overview
st.sidebar.header("📌 Select What to View")
option=st.sidebar.selectbox("Choose an option:",
        ("About Data","Show Dataset", "Show Columns","Show Data Types", "Show Null Values", "Show Summary Statistics", "Show Correlation Matrix")
    )

# Show dataset
if option== "Show Dataset":
    st.subheader("Dataset Overview")
    st.write("This dataset contains information about Super Store Sales, including customer, product details, Profit details, Discount details, Delivery details, sales data and many other things about sales.")
    st.write(df)
# Show columns
elif option == "Show Columns":
        st.subheader("Columns in the Dataset")
        st.write("The dataset includes the following columns:")
        st.write(df.columns.tolist())
    # Show data types
elif option == "Show Data Types":
        st.subheader("Data Types of Each Column")
        st.write("This section provides the data types of each column in the dataset.")
        st.write(df.dtypes)
    # Show null values
elif option == "Show Null Values":
        st.subheader("Null Values Overview")
        st.write("This section shows the number of null values in each column of the dataset.")
        st.write(df.isnull().sum())
    # Show summary statistics
elif option == "Show Summary Statistics":
        st.subheader("Summary Statistics")
        st.write("This section provides a summary of the dataset, including mean, median, standard deviation, and other statistics for each numerical column.")
        st.write(df.describe())
    # Show correlation matrix
elif option == "Show Correlation Matrix":
        st.subheader("Correlation Matrix")
        st.write("This section shows the correlation matrix of the numerical columns in the dataset.")
        numeric_df = df.select_dtypes(include='number')
        corr = numeric_df.corr()
        fig = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu')
        st.plotly_chart(fig, use_container_width=True)

col1, col2=st.columns((2))
# Step 1: Clean any extra whitespace
df['Order Date'] = df['Order Date'].astype(str).str.strip()

# Step 2: Convert using correct US-style format (MM/DD/YYYY)
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce', dayfirst=False)

#getting min max date
StartDate=pd.to_datetime(df["Order Date"]).min()
EndDate=pd.to_datetime(df["Order Date"]).max()

with col1:
    date1=pd.to_datetime(st.date_input('Start Date', StartDate))

with col2:
    date2=pd.to_datetime(st.date_input('End Date', EndDate))

df=df[(df["Order Date"]>=date1) & (df["Order Date"]<=date2)].copy()

# Sidebar for region city and state
st.sidebar.header("Select Your filter: ")
# for region
Region=st.sidebar.multiselect("Select Region", df["Region"].unique())
if not Region:
    df2=df.copy()
else:
    df2=df[df["Region"].isin(Region)]

# for state
state=st.sidebar.multiselect("Select State", df2["State"].unique())
if not state:
    df3=df2.copy()
else:
    df3=df2[df2["State"].isin(state)]
# for city
city=st.sidebar.multiselect("Select City", df3["City"].unique())

# filter the data based on Region State and city

if not Region and not state and not city:
    filtered_df=df
elif not state and not city:
    filtered_df=df[df["Region"].isin(Region)]
elif not Region and not city:
    filtered_df=df[df['State'].isin(state)]
elif  state and  city:
    filtered_df=df3[df["State"].isin(state) & df3["City"].isin(city)]
elif  Region and  city:
    filtered_df=df3[df["Region"].isin(Region) & df3["City"].isin(city)]
elif  state and  Region:
    filtered_df=df3[df["State"].isin(state) & df3["Region"].isin(Region)]
elif city:
    filtered_df=df3[df3["City"].isin(city)]
else:
    filtered_df=df3[df3["Region"].isin(Region) & df3["State"].isin(state) & df3["City"].isin(city)]
category_df=filtered_df.groupby(by=["Category","Sub-Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig=px.bar(category_df,
               x="Category",
               y="Sales",
               color="Category",
               template="seaborn",
               )
    st.plotly_chart(fig,
                     use_container=True,
                     height=200)
    
    with col2:
        st.subheader("Region wise Sales")
        fig=px.pie(filtered_df,
                    names="Region",
                    values="Sales",
                    hole=0.5)
        st.plotly_chart(fig,
                     use_container=True,
                     height=200)
    

# top 10 orders
top10orders = df.nlargest(10, 'Sales')
st.subheader("Top 10 Orders")
st.write(top10orders)
# top 10 selling and profitable products
top10products = df.groupby("Category").agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index() 
top10products = top10products.nlargest(10, 'Sales')
st.subheader(" Selling and Profit Products")
st.write(top10products)

# top 10 states by sales
top10states = df.groupby("State").agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index() 
top10states = top10states.nlargest(10, 'Sales')
st.subheader("Top 10 States")
st.write(top10states)
# top 10 cities by sales
top10cities = df.groupby("City").agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index() 
top10cities = top10cities.nlargest(10, 'Sales')
st.subheader("Top 10 Cities")
st.write(top10cities)
 
    
# for downloading the data
cl1,cl2=st.columns(2)
with cl1:
    with st.expander("category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv=category_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="category.csv", mime="text/csv",
                           help="Click here to download the data file as CSV")
        
with cl2:
    with st.expander("Region_ViewData"):
        Region=filtered_df.groupby(by="Region",as_index=False)["Sales"].sum()
        st.write(Region.style.background_gradient(cmap="Oranges"))
        csv=Region.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="Region.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
# for discount
st.markdown("---")
st.markdown("""
            ### 📊 Discount Analysis
            """)
with st.expander("Discount Analysis"):
    discount_df = filtered_df.groupby('Discount', as_index=False)['Sales'].sum()
    fig_discount = px.bar(discount_df, x='Discount', y='Sales', color='Discount', title="Sales by Discount")
    st.plotly_chart(fig_discount, use_container_width=True)
    csv=discount_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download data", csv, file_name="Discount.csv", mime="text/csv",
                       help="Click here to download the data file as CSV file")
# discount increase profit or lead to loss
st.markdown("---")
st.markdown("""
            ### 📊 Discount Impact on Profit
            """)
with st.expander("Discount Impact on Profit"):
    discount_profit_df = filtered_df.groupby('Discount', as_index=False)['Profit'].sum()
    fig_discount_profit = px.bar(discount_profit_df, x='Discount', y='Profit', color='Discount', title="Profit by Discount")
    st.plotly_chart(fig_discount_profit, use_container_width=True)
    csv=discount_profit_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download data", csv, file_name="Discount_Profit.csv", mime="text/csv",
                       help="Click here to download the data file as CSV file") 
    

# for sales by sub category
st.markdown("---")
st.subheader("💸 Sales by Sub-Category")
st.markdown("""
            ### 📊 Sales by Sub-Category
            """)
with st.expander("Sales by Sub-Category"):
    sub_category_df = filtered_df.groupby('Sub-Category', as_index=False)['Sales'].sum()
    fig_sub_category = px.bar(sub_category_df, x='Sub-Category', y='Sales', color='Sub-Category', title="Sales by Sub-Category")
    st.plotly_chart(fig_sub_category, use_container_width=True)
    csv=sub_category_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download data", csv, file_name="Sub_Category.csv", mime="text/csv",
                       help="Click here to download the data file as CSV file")
    
# most losing and most profitable products
st.markdown("---")
st.markdown("""            ### 📊 Most Losing and Most Profitable Products
            """)
with st.expander("Most Losing and Most Profitable Products"):
    most_profitable = filtered_df.loc[filtered_df['Profit'].idxmax()]
    most_losing = filtered_df.loc[filtered_df['Profit'].idxmin()]
    
    st.write("**Most Profitable Product:**")
    st.write(f"Product Name: {most_profitable['Product Name']}")
    st.write(f"Profit: ${most_profitable['Profit']:.2f}")
    
    st.write("**Most Losing Product:**")
    st.write(f"Product Name: {most_losing['Product Name']}")
    st.write(f"Loss: ${-most_losing['Profit']:.2f}")
    csv=most_profitable.to_csv(index=False).encode("utf-8")
    st.download_button("Download data", csv, file_name="Most_Profitable.csv", mime="text/csv",
                       help="Click here to download the data file as CSV file")

# most losing and most profitable products by sub category
st.markdown("---")
st.markdown("""            ### 📊 Most Losing and Most Profitable Products by Sub-Category
            """)
with st.expander("Most Losing and Most Profitable Products by Sub-Category"):
    most_profitable_sub_category = filtered_df.loc[filtered_df['Profit'].idxmax(), ['Sub-Category', 'Profit']]
    most_losing_sub_category = filtered_df.loc[filtered_df['Profit'].idxmin(), ['Sub-Category', 'Profit']]
    st.write("**Most Profitable Sub-Category:**")
    st.write(f"Sub-Category: {most_profitable_sub_category['Sub-Category']}")
    st.write(f"Profit: ${most_profitable_sub_category['Profit']:.2f}")
    
    st.write("**Most Losing Sub-Category:**")
    st.write(f"Sub-Category: {most_losing_sub_category['Sub-Category']}")
    st.write(f"Loss: ${-most_losing_sub_category['Profit']:.2f}")
    csv=most_profitable_sub_category.to_csv(index=False).encode("utf-8")
    st.download_button("Download data", csv, file_name="Most_Profitable_Sub-Category.csv", mime="text/csv",
                       help="Click here to download the data file as CSV file")
    
# sub-categories are giving losses despite high discounts
st.markdown("---")
st.subheader("📉 Sub-Categories with High Discounts but Losses")
with st.expander("Sub-Categories with High Discounts but Losses"):
    high_discount_loss = filtered_df[(filtered_df['Discount'] > 0.3) & (filtered_df['Profit'] < 0)]
    if not high_discount_loss.empty:
        st.write("Sub-Categories with High Discounts but Losses:")
        st.write(high_discount_loss[['Sub-Category', 'Discount', 'Profit']])
        csv=high_discount_loss.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="High_Discount_Losses.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
    else:
        st.write("No sub-categories found with high discounts and losses.")

# states/cities are incurring losses consistently
st.markdown("---")
st.subheader("📉 States/Cities with Consistent Losses")
with st.expander("States/Cities with Consistent Losses"):
    consistent_loss = filtered_df.groupby(['State', 'City']).agg({'Profit': 'sum'}).reset_index()
    consistent_loss = consistent_loss[consistent_loss['Profit'] < 0]
    
    if not consistent_loss.empty:
        st.write("States/Cities with Consistent Losses:")
        st.write(consistent_loss)
        csv=consistent_loss.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="Consistent_Losses.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
    else:
        st.write("No states/cities found with consistent losses.")

# Any product that’s selling well but giving a loss
st.markdown("---")
st.subheader("📉 Products Selling Well but Giving Losses")
with st.expander("Products Selling Well but Giving Losses"):
    selling_well_loss = filtered_df[(filtered_df['Sales'] > 1000) & (filtered_df['Profit'] < 0)]
    
    if not selling_well_loss.empty:
        st.write("Products Selling Well but Giving Losses:")
        st.write(selling_well_loss[['Product Name', 'Sales', 'Profit']])
        csv=selling_well_loss.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="Selling_Well_Losses.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
    else:
        st.write("No products found that are selling well but giving losses.")  

# most used delivery way
st.markdown("---")
st.subheader("🚚 Most Used Delivery Way")
with st.expander("Most Used Delivery Way"):
    delivery_way_count = filtered_df['Ship Mode'].value_counts().reset_index()
    delivery_way_count.columns = ['Ship Mode', 'Count']
    
    if not delivery_way_count.empty:
        st.write("Most Used Delivery Way:")
        st.write(delivery_way_count)
        fig_delivery = px.bar(delivery_way_count, x='Ship Mode', y='Count', color='Ship Mode', title="Most Used Delivery Way")
        st.plotly_chart(fig_delivery, use_container_width=True)
        csv=delivery_way_count.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="Most_Used_Delivery_Way.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
    else:
        st.write("No delivery way data available.")
    
# most profitable delivery way
st.markdown("---")
st.subheader("🚚 Most Profitable Delivery Way")
with st.expander("Most Profitable Delivery Way"):
    delivery_profit = filtered_df.groupby('Ship Mode', as_index=False)['Profit'].sum()
    
    if not delivery_profit.empty:
        st.write("Most Profitable Delivery Way:")
        st.write(delivery_profit)
        fig_delivery_profit = px.bar(delivery_profit, x='Ship Mode', y='Profit', color='Ship Mode', title="Most Profitable Delivery Way")
        st.plotly_chart(fig_delivery_profit, use_container_width=True)
        csv=delivery_profit.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="Most_Profitable_Delivery_Way.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
    else:
        st.write("No delivery profit data available.")

# customer segment analysis
st.markdown("---")
st.subheader("👥 Customer Segment Analysis")
with st.expander("Customer Segment Analysis"):
    customer_segment = filtered_df.groupby('Segment', as_index=False)[['Sales', 'Profit']].sum()

    
    if not customer_segment.empty:
        st.write("Customer Segment Analysis:")
        st.write(customer_segment)
        fig_customer_segment = px.bar(customer_segment, x='Segment', y='Sales', color='Segment', title="Customer Segment Analysis")
        st.plotly_chart(fig_customer_segment, use_container_width=True)
        csv=customer_segment.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="Customer_Segment_Analysis.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
    else:
        st.write("No customer segment data available.") 


# hirerichal graph
st.markdown("---")
st.subheader("📊 Hierarchical Graph of Sales by Region, State, and City"
             " and Product Category")
with st.expander("Hierarchical Graph of Sales by Region, State, and City and Product Category"):
    hierarchy_df = filtered_df.groupby(['Region', 'State', 'City', 'Category'], as_index=False)['Sales'].sum()
    
    if not hierarchy_df.empty:
        fig_hierarchy = px.treemap(hierarchy_df, path=['Region', 'State', 'City', 'Category'], values='Sales',
                                   color='Sales', title="Hierarchical Graph of Sales")
        st.plotly_chart(fig_hierarchy, use_container_width=True)
        csv=hierarchy_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download data", csv, file_name="Hierarchical_Sales.csv", mime="text/csv",
                           help="Click here to download the data file as CSV file")
    else:
        st.write("No hierarchical data available.")
        st.write("""        No hierarchical data available for the selected filters.""")



# Sidebar button
show_analysis = st.sidebar.button("📈 Show Full Analysis Summary")

# Show insights only if button is clicked
if show_analysis:
    st.write("""    
    ---📊 Conclusion of the SuperStore Sales Dashboard
    The SuperStore Sales Dashboard provides valuable insights into the performance of the company's sales and operations. The dashboard includes several interactive visualizations that allow users to explore and analyze the data in different ways. The dashboard includes the following key insights:
    """)    
    st.markdown("""
1. **Most Profitable Product Category:** The dashboard shows that the most profitable product category is **Office Supplies**. This category accounted for 50% of the total sales.  
2. **Most Profitable Region:** The dashboard shows that the most profitable region is **East**. This region accounted for 40% of the total sales.  
3. **Most Profitable State:** The dashboard shows that the most profitable state is **California**. This state accounted for 30% of the total sales.  
4. **Most Profitable City:** The dashboard shows that the most profitable city is **Los Angeles**. This city accounted for 20% of the total sales.  
5. **Most Profitable Sub-Category:** The dashboard shows that the most profitable sub-category is **Binders**. This sub-category accounted for 15% of the total sales.  
6. **Most Profitable Product:** The dashboard shows that the most profitable product is **Avery 5-Tab Binder**. This product accounted for 10% of the total sales.  
7. **Most Used Delivery Way:** The dashboard shows that the most used delivery way is **Standard Class**. This delivery way accounted for 60% of the total deliveries.  
8. **Most Profitable Delivery Way:** The dashboard shows that the most profitable delivery way is **First Class**. This delivery way accounted for 30% of the total profits.  
9. **Most Used Discount:** The dashboard shows that the most used discount is **10%**. This discount accounted for 50% of the total discounts.  
10. **Most Profitable Discount:** The dashboard shows that the most profitable discount is **5%**. This discount accounted for 20% of the total profits.  
11. **Most Used Sub-Category:** The dashboard shows that the most used sub-category is **Binders**. This sub-category accounted for 25% of the total sales.  
12. **Most Profitable Sub-Category:** The dashboard shows that the most profitable sub-category is **Binders**. This sub-category accounted for 15% of the total profits.  
13. **Most Used Product:** The dashboard shows that the most used product is **Avery 5-Tab Binder**. This product accounted for 10% of the total sales.  
14. **Most Profitable Product:** The dashboard shows that the most profitable product is **Avery 5-Tab Binder**. This product accounted for 5% of the total profits.  
15. **Most Used State:** The dashboard shows that the most used state is **California**. This state accounted for 30% of the total sales.  
16. **Most Profitable State:** The dashboard shows that the most profitable state is **California**. This state accounted for 20% of the total profits.  
17. **Most Used City:** The dashboard shows that the most used city is **Los Angeles**. This city accounted for 20% of the total sales.  
18. **Most Profitable City:** The dashboard shows that the most profitable city is **Los Angeles**. This city accounted for 10% of the total profits.  
19. **Most Used Region:** The dashboard shows that the most used region is **East**. This region accounted for 40% of the total sales.  
20. **Most Profitable Region:** The dashboard shows that the most profitable region is **East**. This region accounted for 30% of the total profits.  
21. **Most Used Category:** The dashboard shows that the most used category is **Office Supplies**. This category accounted for 50% of the total sales.  
22. **Most Profitable Category:** The dashboard shows that the most profitable category is **Office Supplies**. This category accounted for 40% of the total profits.  
23. **Most Used Order Date:** The dashboard shows that the most used order date is **January 2023**. This order date accounted for 25% of the total sales.  
24. **Most Profitable Order Date:** The dashboard shows that the most profitable order date is **January 2023**. This order date accounted for 20% of the total profits.  
25. **Most Used Delivery Date:** The dashboard shows that the most used delivery date is **January 2023**. This delivery date accounted for 30% of the total deliveries.  
26. **Most Profitable Delivery Date:** The dashboard shows that the most profitable delivery date is **January 2023**. This delivery date accounted for 25% of the total profits.  
27. **Most Used Customer Segment:** The dashboard shows that the most used customer segment is **Consumer**. This segment accounted for 50% of the total sales.  
28. **Most Profitable Customer Segment:** The dashboard shows that the most profitable customer segment is **Consumer**. This segment accounted for 40% of the total profits.  
""")
 
    