# -*- coding: utf-8 -*-
"""air quality application

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EycVHuljaKAAVbTv33hN5xESis8lD52y
"""

# Importing Libraries
import pandas as pd
import numpy as np
import os
import glob
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

"""# Load and Merge the datasets"""

folder_path = "/content/"
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
# Read and merge all CSVs
dfs = []
for file in csv_files:
    df = pd.read_csv(file)
    dfs.append(df)
# Merge into one main dataframe
data = pd.concat(dfs, ignore_index=True)
# Show first few rows
print("Merged dataset shape:", data.shape)
data.head()

"""# Task 2 exploratory data analysis"""

data.info()

data.columns

data.isnull().sum()

print("\nData Types:")
data.dtypes

print("\nStatistical Summary:")
data.describe()

"""## Data preprocessing"""

# Handling Missing Values
# Fill missing numeric values with median
numeric_cols = data.select_dtypes(include=np.number).columns
data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())
# Fill missing wind directions with the most common value
data['wd'] = data['wd'].fillna(data['wd'].mode()[0])
data.isnull().sum()

# Remove Duplicate Rows
data = data.drop_duplicates()

# Feature Engineering
# Create a "datetime" feature
data['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])
# Sort by datetime
data = data.sort_values('datetime')

# Univariate Analysis: PM2.5 Distribution

sns.histplot(data['PM2.5'], bins=50, kde=True, color='blue')
plt.title("Distribution of PM2.5")
plt.xlabel("PM2.5 Concentration (µg/m³)")
plt.ylabel("Frequency")
plt.show()

# Time Series Line Plot: PM2.5 Over Time

data.set_index('datetime')['PM2.5'].resample('M').mean().plot(figsize=(14,5))
plt.title("Monthly Average PM2.5 Concentration Over Time")
plt.ylabel("PM2.5 (µg/m³)")
plt.xlabel("Date")
plt.grid()
plt.show()

# Bivariate Analysis: PM2.5 vs Temperature

sns.scatterplot(x='TEMP', y='PM2.5', data=data, alpha=0.4)
plt.title("Scatterplot: PM2.5 vs Temperature")
plt.xlabel("Temperature (°C)")
plt.ylabel("PM2.5 (µg/m³)")
plt.show()

# Boxplot: PM2.5 by Wind Direction

sns.boxplot(x='wd', y='PM2.5', data=data)
plt.title("Boxplot of PM2.5 by Wind Direction")
plt.xticks(rotation=45)
plt.show()

# Heatmap: Correlation Matrix

plt.figure(figsize=(10, 8))
corr = data[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.title("Correlation Heatmap")
plt.show()

# Bar Chart: Average PM2.5 by Month

monthly_avg = data.groupby(data['datetime'].dt.month)['PM2.5'].mean()
monthly_avg.plot(kind='bar', color='skyblue')
plt.title("Average PM2.5 by Month")
plt.xlabel("Month")
plt.ylabel("PM2.5 (µg/m³)")
plt.xticks(rotation=0)
plt.show()

# Multivariate Analysis: Pairplot of Pollutants

sns.pairplot(data[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO']].dropna(), diag_kind='kde')
plt.suptitle("Pairplot of Pollutants", y=1.02)
plt.show()

# Wind Speed vs PM2.5: Scatter Plot with Regression Line

sns.lmplot(x='WSPM', y='PM2.5', data=data, aspect=1.5, scatter_kws={'alpha':0.3})
plt.title("PM2.5 vs Wind Speed with Regression Line")
plt.show()

"""## Statistical summary"""

# Select numerical columns for summary
numerical_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
# Create a dictionary of statistics
summary_stats = {
    'Mean': data[numerical_cols].mean(),
    'Median': data[numerical_cols].median(),
    'Min': data[numerical_cols].min(),
    'Max': data[numerical_cols].max(),
    'Std Dev': data[numerical_cols].std(),
    'Skewness': data[numerical_cols].skew(),
    'Kurtosis': data[numerical_cols].kurt()
}
# Convert to DataFrame
import pandas as pd
custom_summary = pd.DataFrame(summary_stats)
custom_summary = custom_summary.transpose()
# Display nicely
print("Custom Statistical Summary:\n")
display(custom_summary.round(2))

"""# Task 3 Model building"""

# Feature Setup

# Drop rows with missing values in selected features
selected_features = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM',
                     'PM10', 'SO2', 'NO2', 'CO', 'O3', 'wd']
data_filtered = data[selected_features + ['PM2.5']].dropna()
X = data_filtered.drop(columns=['PM2.5'])
y = data_filtered['PM2.5']

# Column types
numeric_features = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
categorical_features = ['wd']
# Preprocessor
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric_features),
    ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
])

"""# Linear Regression"""

pipeline_lr = Pipeline([
    ('preprocess', preprocessor),
    ('model', LinearRegression())
])
pipeline_lr.fit(X, y)
y_pred_lr = pipeline_lr.predict(X)
print("Linear Regression:")
print("RMSE:", np.sqrt(mean_squared_error(y, y_pred_lr)))
print("MAE:", mean_absolute_error(y, y_pred_lr))
print("R² Score:", r2_score(y, y_pred_lr))

"""# Random Forest Regressor"""

pipeline_rf = Pipeline([
    ('preprocess', preprocessor),
    ('model', RandomForestRegressor(n_estimators=100, random_state=42))
])
pipeline_rf.fit(X, y)
y_pred_rf = pipeline_rf.predict(X)
print("Random Forest Regressor:")
print("RMSE:", np.sqrt(mean_squared_error(y, y_pred_rf)))
print("MAE:", mean_absolute_error(y, y_pred_rf))
print("R² Score:", r2_score(y, y_pred_rf))

"""# Task 4 Application development"""

import gradio as gr
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import numpy as np
import os, glob
#  Load & Preprocess Data
folder_path = "/content/"  # Change if needed
csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
dfs = [pd.read_csv(file) for file in csv_files]
data = pd.concat(dfs, ignore_index=True)
data['wd'] = data['wd'].fillna(data['wd'].mode()[0])
numeric_cols = data.select_dtypes(include=np.number).columns
data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())
data = data.drop_duplicates()
data['datetime'] = pd.to_datetime(data[['year', 'month', 'day', 'hour']])
data = data.sort_values('datetime')

features = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'wd']
target = 'PM2.5'
X = data[features].dropna()
y = data[target].loc[X.index]

numeric = X.select_dtypes(include='number').columns.tolist()
categorical = ['wd']
preprocessor = ColumnTransformer([
    ('num', StandardScaler(), numeric),
    ('cat', OneHotEncoder(), categorical)
])

# Train models (Linear Regression and Random Forest only)
def get_model(model_type):
    if model_type == "Linear Regression":
        model = LinearRegression()
    elif model_type == "Random Forest":
        model = RandomForestRegressor(n_estimators=100)
    else:
        raise ValueError("Unsupported model type. Choose 'Linear Regression' or 'Random Forest'.")

    pipeline = Pipeline([("pre", preprocessor), ("model", model)])
    pipeline.fit(X, y)
    return pipeline

#  GUI Functions
def home_page():
    return """
# Welcome to the PM2.5 Air Quality Analysis App 🌿

Explore and predict PM2.5 air pollution levels using weather and pollutant data.

### Features:
- **Data Overview**: Summary, types, and shape of the dataset.
- **Exploratory Data Analysis**: Visual trends and relationships.
- **Modeling & Prediction**: Predict PM2.5 using machine learning models.

Dataset includes variables like Temperature, Wind Speed, PM10, CO, SO₂, NO₂, O₃, and Wind Direction.

---

### Summary:
Air pollution is comprised of various chemicals and particles present in the atmosphere, which present significant hazards to both public health and the environment (Lim et al., 2020). Prolonged exposure to air pollution elevates the likelihood of experiencing a stroke, cardiovascular disease, lung carcinoma, and a multitude of other chronic pulmonary conditions (Brauer et al., 2021; Li et al., 2019). Consequently, it is of paramount importance and necessity to mitigate air pollution through the forecasting of air quality.

Beijing, the capital of China, has encountered some problems related to pollution control in the process of rapid economic development. The effect of air quality improvement in recent years has been relatively good in China, but the situation is still very serious (Li et al., 2024). Air pollution is still a great challenge to mankind all over the world (Sokhi et al., 2022).

---

### Dataset Information:
The dataset includes hourly air pollutants data from 12 nationally controlled air-quality monitoring sites: Gucheng, Wanshouxigong, Tiantan, Guanyuan, Dongsi, Nongzhanguan, Wanliu, Aotizhongxin, Shunyi, Changping, Dingling, and Huairou. The dataset includes two main categories:

1. **Air-quality pollutants** of 12 stations, including solid particulate matter (PM2.5, PM10) and gas pollutants (SO2, NO2, CO, O3).
2. **Meteorological conditions** including wind speed (Wspd), rainfall (Rain), temperature (Temp), dew point (Dewp), and pressure (Pre).

The air-quality data is sourced from the Beijing Municipal Environmental Monitoring Center, and the meteorological data is matched with the nearest weather stations from the China Meteorological Administration. The dataset spans the period from March 1st, 2013, to February 28th, 2017.
"""


def show_overview(option):
    if option == "Head":
        return data.head().to_markdown()
    elif option == "Shape":
        return f"Rows: {data.shape[0]}, Columns: {data.shape[1]}"
    elif option == "Data Types":
        return data.dtypes.to_string()
    elif option == "Summary":
        return data.describe().to_string()

def show_eda(plot_type):
    plt.clf()
    if plot_type == "PM2.5 Distribution":
        sns.histplot(data['PM2.5'], bins=50, kde=True, color='blue')
        plt.title("Distribution of PM2.5")
        plt.xlabel("PM2.5 Concentration (µg/m³)")
        plt.ylabel("Frequency")
    elif plot_type == "Monthly Trend":
        data.set_index('datetime')['PM2.5'].resample('M').mean().plot(figsize=(10,4))
        plt.title("Monthly Average PM2.5 Concentration Over Time")
        plt.ylabel("PM2.5 (µg/m³)")
        plt.xlabel("Date")
        plt.grid()
    elif plot_type == "PM2.5 vs Temperature":
        sns.scatterplot(x='TEMP', y='PM2.5', data=data, alpha=0.4)
        plt.title("Scatterplot: PM2.5 vs Temperature")
        plt.xlabel("Temperature (°C)")
        plt.ylabel("PM2.5 (µg/m³)")
    elif plot_type == "Boxplot by Wind Direction":
        sns.boxplot(x='wd', y='PM2.5', data=data)
        plt.title("Boxplot of PM2.5 by Wind Direction")
        plt.xticks(rotation=45)
    elif plot_type == "Correlation Heatmap":
        plt.figure(figsize=(10, 8))
        corr = data[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title("Correlation Heatmap")
    elif plot_type == "Average PM2.5 by Month":
        monthly_avg = data.groupby(data['datetime'].dt.month)['PM2.5'].mean()
        monthly_avg.plot(kind='bar', color='skyblue')
        plt.title("Average PM2.5 by Month")
        plt.xlabel("Month")
        plt.ylabel("PM2.5 (µg/m³)")
        plt.xticks(rotation=0)
    elif plot_type == "Pairplot of Pollutants":
        sns.pairplot(data[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO']].dropna(), diag_kind='kde')
        plt.suptitle("Pairplot of Pollutants", y=1.02)
        return plt.gcf()
    elif plot_type == "WSPM vs PM2.5 Regression":
        sns.lmplot(x='WSPM', y='PM2.5', data=data, aspect=1.5, scatter_kws={'alpha':0.3})
        plt.title("PM2.5 vs Wind Speed with Regression Line")
        return plt.gcf()
    return plt.gcf()

def predict(model_name, temp, pres, dewp, rain, wspm, pm10, so2, no2, co, o3, wd):
    df = pd.DataFrame([[temp, pres, dewp, rain, wspm, pm10, so2, no2, co, o3, wd]], columns=features)
    model = {"Linear Regression": lr_model, "Random Forest": rf_model}[model_name]
    pred = model.predict(df)[0]
    return f"Predicted PM2.5: {pred:.2f} µg/m³"

#  Gradio Interface
with gr.Blocks(title="PM2.5 Analysis App") as app:
    with gr.Tab("🏠 Home"):
        gr.Markdown(home_page())

    with gr.Tab("📊 Data Overview"):
        gr.Markdown("### View Dataset Information")
        overview_option = gr.Radio(["Head", "Shape", "Data Types", "Summary"], label="Select Info Type")
        overview_output = gr.Textbox(label="Result", lines=15)
        overview_option.change(fn=show_overview, inputs=overview_option, outputs=overview_output)

    with gr.Tab("📈 EDA"):
        gr.Markdown("### Exploratory Data Analysis")
        eda_options = [
            "PM2.5 Distribution", "Monthly Trend", "PM2.5 vs Temperature",
            "Boxplot by Wind Direction", "Correlation Heatmap",
            "Average PM2.5 by Month", "Pairplot of Pollutants",
            "WSPM vs PM2.5 Regression"
        ]
        eda_select = gr.Radio(eda_options, label="Choose Plot Type")
        eda_plot = gr.Plot()
        eda_select.change(fn=show_eda, inputs=eda_select, outputs=eda_plot)

    with gr.Tab("🧠 Modeling & Prediction"):
        gr.Markdown("### Predict PM2.5 Concentration")
        model_choice = gr.Dropdown(["Linear Regression", "Random Forest"], label="Choose Model")
        with gr.Row():
            temp = gr.Number(label="Temperature (TEMP)")
            pres = gr.Number(label="Pressure (PRES)")
            dewp = gr.Number(label="Dew Point (DEWP)")
            rain = gr.Number(label="Rain (RAIN)")
            wspm = gr.Number(label="Wind Speed (WSPM)")
        with gr.Row():
            pm10 = gr.Number(label="PM10")
            so2 = gr.Number(label="SO2")
            no2 = gr.Number(label="NO2")
            co = gr.Number(label="CO")
            o3 = gr.Number(label="O3")
            wd = gr.Textbox(label="Wind Direction (wd)", placeholder="e.g. NW")

        predict_btn = gr.Button("Predict")
        pred_output = gr.Textbox(label="Prediction Result")
        predict_btn.click(fn=predict, inputs=[model_choice, temp, pres, dewp, rain, wspm, pm10, so2, no2, co, o3, wd], outputs=pred_output)

app.launch()



