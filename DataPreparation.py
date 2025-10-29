#Import libraries 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LassoCV

print('='*25)
print('Part 1: Data Preparation')
print('='*25)

#Load data
pd_data_path = 'Downloads/parkinsons+telemonitoring/parkinsons_updrs.data'
df = pd.read_csv(pd_data_path)
print(f"Successful loading of data!")



print("1.1. BASIC DATASET CHARACTERISTICS")
print("Information about the data:")
print('-'*28)
print({df.info()})
print(f"The shape of the data is: {df.shape}")
print('-'*36)
print(f"The number of records: {df.shape[0]}")
print('-'*28)
print(f"The number of features: {df.shape[1]}")
print('-'*26)
print(f"Stats about the columns:")
print('-'*24)
print(df.describe())
print('\n')
print("The first 5 rows of the dataset:")
print('-'*34)
print(df.head())




print("1.2. CLEANING DATA: MISSING, NULL, NAN")
missing_points = df.isnull().sum() #accounts for None/Null and NaN

missing_data = pd.DataFrame({
    'Column': missing_points.index,
    'Missing_Count': missing_points.values,
})

print("Information about missing values:")
print('-'*33)
print(missing_data)

if missing_points.sum() == 0: 
    print("No missing values found in the dataset!")
else: 
    print(f"{missing_points.sum()} missing values found")


#Infinite values check 
infinity_cols = (np.isinf(df.select_dtypes(include=[np.number]))).any()

if not infinity_cols.any():
    print("No infinite values found!")
else:
    print("Column with Infinite values:", list(inf_cols[inf_cols].index))



print("1.3. TRANSFORM DATA")
#Find non-numeric columns
non_numeric = df.select_dtypes(exclude=[np.number]).columns
print("Non-numeric columns:", list(non_numeric))

#Attempt to convert 
for col in non_numeric:
    df[col] = pd.to_numeric(df[col], errors='coerce')
print("All necessary columns are numeric")




print("1.4. DATA ANALYSIS. LISTING TYPES")
#Checking for 'subject#' column. Categorical, represents subjects.
if 'subject#' in df.columns:
    print(f"Number of unique subjects: {df['subject#'].nunique()}")
    print(f"Subject IDs range: {df['subject#'].min()} to {df['subject#'].max()}") #Tells us if IDs are continuous

print("\nData types of all columns:")
print(df.dtypes)

#Finding numeric vs categorical columns
numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_columns = df.select_dtypes(include=['object']).columns.tolist()

print(f"\nNumeric columns ({len(numeric_columns)}):")
print(numeric_columns)

print(f"\nCategorical columns ({len(categorical_columns)}):")
print(categorical_columns)
if len(categorical_columns) == 0: 
    print("This confirms that all columns are numeric!")




print("1.5. OUTLIER DETECTION")
#Z-score Method: to identify outlier by SD from mean. For Normal distribution
numeric_data = df.select_dtypes(include=[np.number]).drop(columns=['subject#'], errors='ignore') #Exclude non-numeric columns

#Absolute Z-scores
z_scores = np.abs(stats.zscore(numeric_data))
outlier_counts = (z_scores > 3).sum(axis=0) #Count outliers per columnm thredhold of 3
outlier_counts = pd.Series((z_scores > 3).sum(axis=0), index=numeric_data.columns)
outlier_counts = outlier_counts[outlier_counts > 0] #Columns with outliers
if outlier_counts[outlier_counts > 0].empty:
    print("No Z-score outliers found.")
else:
    print("\nZ-score Outliers:")
    print(outlier_counts[outlier_counts > 0].sort_values(ascending=False))

#IQR Method: to identify outlier by spread of middle 50%. Non-normal distribution. For skewed data
outlier_data = []
for col in numeric_data.columns:
    Q1 = numeric_data[col].quantile(0.25)
    Q3 = numeric_data[col].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    count = ((numeric_data[col] < lower) | (numeric_data[col] > upper)).sum()
    percent = (count / len(numeric_data)) * 100

    if count > 0:
        outlier_data.append([col, count, f"{percent:.2f}%", f"{lower:.2f}", f"{upper:.2f}"])


#Outlier DataFrame
if outlier_data:
    outlier_df = pd.DataFrame(outlier_data, columns=[
        'Feature', 'Outlier_Count', 'Outlier_Percentage', 'Lower_Bound', 'Upper_Bound'
    ])
    outlier_df = outlier_df.sort_values('Outlier_Count', ascending=False)

    print("\nTop Features with IQR Outliers:")
    print(outlier_df.head(10).to_string(index=False))
else:
    print("No IQR outliers found.")
#Note: both methods were used for a comprehensive measure, to cover normal and non-normal distribution

#Box Plots for Outlier Detection, outliers in features with most skewness
outlier_features = ['Shimmer(dB)', 'Shimmer:APQ5', 'NHR', 'Jitter(%)', 'PPE', 'RPDE']
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.ravel()

for idx, feature in enumerate(outlier_features):
    axes[idx].boxplot(df[feature], vert=True, patch_artist=True,
                     boxprops=dict(facecolor='lightblue', alpha=0.7),
                     medianprops=dict(color='red', linewidth=2))
    axes[idx].set_ylabel('Value')
    axes[idx].set_title(feature)
    axes[idx].grid(axis='y', alpha=0.3)

plt.suptitle('Outlier Detection - Selected Features', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()