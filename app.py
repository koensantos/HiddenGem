import pandas as pd
from sqlalchemy import create_engine
# Create a database engine
# Load the CSV file into a DataFrame
df = pd.read_csv('dataset/dataset.csv')
print(df.head())  # Display the first few rows of the DataFrame
print(df.columns.tolist())  # Display the column names of the DataFrame

def clean_dataframe(df):
    #Cleans dataframe by removing dups, handles missing values
    df = df.drop_duplicates()  # Remove duplicate rows
    df = df.dropna()  # Remove rows with missing values
    if df.duplicated().any():
        print("Warning: There are still duplicate rows in the DataFrame.")
    if df.isna().sum().any():
        print("Warning: There are still missing values in the DataFrame.")
    return df
df = clean_dataframe(df)

engine = create_engine('sqlite:///song_dataset.db')

df.to_sql('songs', con=engine, if_exists='replace', index=False)

check_df = pd.read_sql('SELECT * FROM songs', con=engine)
print(check_df.head())  # Display the first few rows of the DataFrame read from the

get_track_name = pd.read_sql('SELECT track_name FROM songs', con=engine)
print(get_track_name.head()) 