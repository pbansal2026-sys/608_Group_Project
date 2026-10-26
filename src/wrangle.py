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
