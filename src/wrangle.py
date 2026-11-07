import pandas as pd

df = pd.read_excel("data/raw/total_count_intentional_homicide.xlsx", header=2)

#print(df.shape)
#print(df.info())
#print(df.head())

df = df[(df["Indicator"] == "Victims of intentional homicide")
         & (df["Sex"] == "Total") & (df["Dimension"] == "Total") 
         & (df["Age"] == "Total") & (df["Category"] == "Total") 
         & (df["Unit of measurement"] == "Counts")
        
        ]
#print(df.shape)

summarised_totalcount = df.drop(columns=["Source", "Region", "Subregion", 
                                         "Indicator", "Sex", "Dimension", 
                                         "Age", "Category", "Unit of measurement"])

#print(summarised_totalcount.shape)

#print(summarised_totalcount.info())

summarised_totalcount.to_csv("data/processed/TotalCounts.csv", index=False)


df = pd.read_excel("data/raw/total_count_intentional_homicide.xlsx", header=2)
df = df[(df["Indicator"] == "Victims of intentional homicide")
         & (df["Sex"] == "Total") & (df["Dimension"] == "Total") 
         & (df["Age"] == "Total") & (df["Category"] == "Total") 
         & (df["Unit of measurement"] == "Rate per 100,000 population")
        
        ]
#print(df.shape)

summarised_rate = df.drop(columns=["Source", "Region", "Subregion", 
                                         "Indicator", "Sex", "Dimension", 
                                         "Age", "Category", "Unit of measurement"])


summarised_rate.to_csv("data/processed/Total_Rate.csv", index=False)