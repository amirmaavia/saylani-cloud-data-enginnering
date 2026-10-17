import pandas as pd 
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv("supermarket_sales_case_study.csv")
audit = pd.DataFrame({
    "missing_count": df.isnull().sum(),
    "duplicate_row": df.duplicated().sum()
})
print(audit)
invoice_duplicates = df.duplicated(["Invoice ID"]).sum()
Distinct_Genders = df["Gender"].unique()
Distinct_Payment = df["Payment"].unique()
print(audit)
#55
print("Invoice Duplicate:",invoice_duplicates)
#6
print("Distinct_Genders:", Distinct_Genders)
#7
print("Distinct_Payment:", Distinct_Payment)

print(len(df))
RemoveCopies = df.drop_duplicates()
print(len(RemoveCopies))
Clean_Invoice_Conflict = RemoveCopies.drop_duplicates(subset="Invoice ID", keep="last")
print(len(Clean_Invoice_Conflict))
Clean_Invoice_Conflict = Clean_Invoice_Conflict
Clean_Invoice_Conflict["Invoice ID"] = Clean_Invoice_Conflict["Invoice ID"].str.strip().str.lower()
Clean_Invoice_Conflict["Branch"] = Clean_Invoice_Conflict["Branch"].str.strip().str.lower()
Clean_Invoice_Conflict["City"] = Clean_Invoice_Conflict["City"].str.strip().str.lower()
Clean_Invoice_Conflict["Customer type"] = Clean_Invoice_Conflict["Customer type"].str.strip().str.lower()
Clean_Invoice_Conflict["Gender"] = Clean_Invoice_Conflict["Gender"].str.strip().str.lower()
Clean_Invoice_Conflict["Product line"] = Clean_Invoice_Conflict["Product line"].str.strip().str.lower()
Clean_Invoice_Conflict["Payment"] = Clean_Invoice_Conflict["Payment"].str.strip().str.lower()

Clean_Invoice_Conflict["Unit price"] = Clean_Invoice_Conflict["Unit price"].abs() 
Clean_Invoice_Conflict["Quantity"] = Clean_Invoice_Conflict["Quantity"].abs() 
Clean_Invoice_Conflict["Tax 5%"] = Clean_Invoice_Conflict["Tax 5%"].abs() 
Clean_Invoice_Conflict["Total"] = Clean_Invoice_Conflict["Total"].abs() 
Clean_Invoice_Conflict["cogs"] = Clean_Invoice_Conflict["cogs"].abs() 
Clean_Invoice_Conflict["gross margin percentage"] = Clean_Invoice_Conflict["gross margin percentage"].abs() 
Clean_Invoice_Conflict["gross income"] = Clean_Invoice_Conflict["gross income"].abs() 
Clean_Invoice_Conflict["Rating"] = Clean_Invoice_Conflict["Rating"].abs() 
Clean_Invoice_Conflict["Date"] = pd.to_datetime(Clean_Invoice_Conflict["Date"],errors="coerce" )
Clean_Invoice_Conflict["Time"] = pd.to_datetime(Clean_Invoice_Conflict["Time"],errors="coerce")

Total = (Clean_Invoice_Conflict["Quantity"] * Clean_Invoice_Conflict["Unit price"] * 1.05)
mask = Total >= 0.5
Clean_Invoice_Conflict.loc[mask, "Total"] = Total[mask].round(2)

Clean_Invoice_Conflict["Rating"] = Clean_Invoice_Conflict["Rating"].fillna("Unknown")
Clean_Invoice_Conflict = Clean_Invoice_Conflict.dropna(subset=["Date"])
print(Clean_Invoice_Conflict.head())
print( len(Clean_Invoice_Conflict)) 

# First Result Clean_Invoice_Conflict 
Clean_Invoice_Conflict["Year"] = Clean_Invoice_Conflict["Date"].dt.year 
Clean_Invoice_Conflict["Quarter"] = Clean_Invoice_Conflict["Date"].dt.quarter
Clean_Invoice_Conflict["Hour"] = Clean_Invoice_Conflict["Time"].dt.hour
Clean_Invoice_Conflict["Day of Week"] = Clean_Invoice_Conflict["Date"].dt.day_of_week
Clean_Invoice_Conflict["Time"] = Clean_Invoice_Conflict["Time"].dt.time
Clean_Invoice_Conflict['Weekday'] = (
    Clean_Invoice_Conflict['Date'].dt.day_name()
)

conditions = [
    (Clean_Invoice_Conflict["Hour"] >= 10) & (Clean_Invoice_Conflict["Hour"] < 13),
    (Clean_Invoice_Conflict["Hour"] >= 13) & (Clean_Invoice_Conflict["Hour"] < 17),
    (Clean_Invoice_Conflict["Hour"] >= 17) & (Clean_Invoice_Conflict["Hour"] < 21),
]
choices = ["Morning", "Afternoon", "Evening"]
Clean_Invoice_Conflict["Bucket"] = pd.Series(pd.NA, index=Clean_Invoice_Conflict.index,dtype="object")
Clean_Invoice_Conflict.loc[conditions[0], "Bucket"] = choices[0]
Clean_Invoice_Conflict.loc[conditions[1], "Bucket"] = choices[1]
Clean_Invoice_Conflict.loc[conditions[2], "Bucket"] = choices[2]
Transaction_Bucket = {
    "Morning": len(Clean_Invoice_Conflict[Clean_Invoice_Conflict["Bucket"] == "Morning"]),
    "Afternoon": len(Clean_Invoice_Conflict[Clean_Invoice_Conflict["Bucket"] == "Afternoon"]),
    "Evening": len(Clean_Invoice_Conflict[Clean_Invoice_Conflict["Bucket"] == "Evening"])}

Bucket_Hours = {
    "Morning": 3,
    "Afternoon": 4,
    "Evening": 4
}

Transactions_Per_Hour = {
    bucket: count / Bucket_Hours[bucket]
    for bucket, count in Transaction_Bucket.items()
}
# Second Result Transactions_Per_Hour
print(Transactions_Per_Hour)
print(Clean_Invoice_Conflict.head())

Quarterly_Group = (Clean_Invoice_Conflict.groupby(['Branch','Year','Quarter'], as_index=False)['Total'].sum())
print(Quarterly_Group.head())

Targets = pd.DataFrame({
    "Branch": Quarterly_Group['Branch'].unique(),
    'Target': 100000
})

Result = Quarterly_Group.merge(
    Targets,
    on='Branch',
    how='left'
)

Result['Variance'] = Result['Total'] - Result['Target']
Result['% of Target'] = (
    Result['Total'] / Result['Target'] * 100
).round(2)
# Branch Summery
Branch_Summary = Result.groupby('Branch').agg(
    Average_Quarterly_Revenue=('Total', 'mean'),
    Quarters_Hit=('Variance', lambda values: (values >= 0).sum()),
    Best_Quarter_Revenue=('Total', 'max'),
    Worst_Quarter_Revenue=('Total', 'min')
).reset_index()
Yearly_Revenue = (Quarterly_Group.groupby(['Branch', 'Year'])['Total'].sum().unstack())

Yearly_Revenue["YoY growth %"] = (
    (Yearly_Revenue[2024] / Yearly_Revenue[2023] - 1) 
    * 100)
print(Yearly_Revenue)

weekdays_day = (
     Clean_Invoice_Conflict[['Date', 'Weekday']]
    .drop_duplicates()
    .groupby('Weekday')['Date']
    .nunique()
)
weekdays_transactions = (
    Clean_Invoice_Conflict.groupby('Weekday').size()
)
# Clean_Invoice_Conflict["Time"] = clean_Invoice_Conflict["Date"]

weekdays_summary = pd.DataFrame({
    'Transactions': weekdays_transactions,
    'Number_of_Days': weekdays_day
})
weekdays_summary['Average_Per_Day'] = (
    weekdays_summary['Transactions'] /
    weekdays_summary['Number_of_Days']
)
print(weekdays_summary)
weekday_order = [
    'Monday', 'Tuesday', 'Wednesday', 'Thursday',
    'Friday', 'Saturday', 'Sunday'
]
weekday_summary = pd.DataFrame({
    'Transactions': weekdays_transactions,
    'Number_of_Days': weekdays_day
}).reindex(weekday_order)
dates = Clean_Invoice_Conflict[['Date', 'Weekday']].drop_duplicates()
hours = list(range(10, 21))
grid = dates.assign(_key=1).merge(
    pd.DataFrame({'Hour': hours, '_key': 1}), on='_key'
).drop(columns='_key')

daily_hourly = (
    Clean_Invoice_Conflict.groupby(['Date', 'Weekday', 'Hour'])
      .size()
      .rename('Transactions')
      .reset_index()
)
daily_hourly = grid.merge(
    daily_hourly, on=['Date', 'Weekday', 'Hour'], how='left'
)
daily_hourly['Transactions'] = daily_hourly['Transactions'].fillna(0)

heatmap_data = (
    daily_hourly.groupby(['Weekday', 'Hour'])['Transactions']
    .mean()
    .unstack('Hour')
    .reindex(weekday_order)
)

print("\\nAverage transactions by weekday and hour:")
print(heatmap_data.round(2))

# Plot heatmap
fig, ax = plt.subplots(figsize=(12, 6))
im = ax.imshow(heatmap_data, aspect='auto', interpolation='nearest')

ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels([f'{h}:00' for h in heatmap_data.columns])
ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index)

ax.set_xlabel('Hour of day')
ax.set_ylabel('Weekday')
ax.set_title('Average Transactions by Weekday and Hour')

cbar = fig.colorbar(im, ax=ax)
cbar.set_label('Average transactions per day at that hour')

plt.tight_layout()
plt.show()

for branch in Quarterly_Group['Branch'].unique():
    branch_data = Quarterly_Group[
        Quarterly_Group['Branch'] == branch
    ].sort_values(['Year', 'Quarter']).copy()

    branch_data['Quarter_Label'] = (
        branch_data['Year'].astype(str)
        + ' Q'
        + branch_data['Quarter'].astype(str)
    )

    plt.figure(figsize=(10, 5))

    plt.plot(
        branch_data['Quarter_Label'],
        branch_data['Total'],
        marker='o',
        label='Quarterly Revenue'
    )
    plt.xlabel('Quarter')
    plt.ylabel('Total Revenue')
    plt.title(f'Quarterly Revenue for {branch}')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    Clean_Invoice_Conflict.to_csv(
    'clean_invoice_data.csv',
    index=False,
    encoding='utf-8-sig'
)

print(Quarterly_Group)
branch_revenue = Quarterly_Group.groupby('Branch')['Total'].sum()
yoy_growth = Yearly_Revenue['YoY growth %']
quarter_counts = Quarterly_Group.groupby('Branch').size()
highest_revenue_branch = branch_revenue.idxmax()
highest_growth_branch = yoy_growth.idxmax()
lowest_growth_branch = yoy_growth.idxmin()

print(
    f"Quarterly records analyzed: {len(Quarterly_Group)}\n"
    f"Quarters achieving the $100,000 target: {(Quarterly_Group['Total'] >= 100000).sum()}\n"
    f"Highest combined revenue: Branch {highest_revenue_branch.upper()} "
    f"(${branch_revenue[highest_revenue_branch]:,.2f})\n"
    f"Highest YoY growth (2024 vs 2023): Branch {highest_growth_branch.upper()} "
    f"({yoy_growth[highest_growth_branch]:.2f}%)\n"
    f"Lowest YoY growth (2024 vs 2023): Branch {lowest_growth_branch.upper()} "
    f"({yoy_growth[lowest_growth_branch]:.2f}%)\n"
    f"Quarters available per branch: {quarter_counts.to_dict()}\n"
    f"All branches have all 8 quarters: {quarter_counts.eq(8).all()}"
)


# # 2. Create the heatmap (annot=True displays the numbers inside the blocks)
# sns.heatmap(data, annot=True, cmap='coolwarm')

# # 3. Display the plot (Required for standard .py scripts, optional for Notebooks)
# plt.show()
# print(audit[audit.missing_count > 0])
# print("Exact duplicate rows",df.duplicated().sum())
# rows_in = len(df)
# df = df.drop_duplicates()
# print("Exact duplicate rows",df.duplicated().sum())
# df["quantity_cleaning"] = pd.to_numeric(df["quantity"],errors="coerce")
# df["unit_price_clean"] = pd.to_numeric(df["unit_price"],errors="coerce")
# df["order_date"] = pd.to_datetime(df["order_date"],errors="coerce")
# stores = pd.read_csv("brewbuzz_stores.csv")
# print(stores.head())
