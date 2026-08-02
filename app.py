import pandas as pd
from sqlalchemy import create_engine
# Create a database engine
# Load the CSV file into a DataFrame
df = pd.read_csv('dataset/dataset.csv')
print(df.head())  # Display the first few rows of the DataFrame
print(df.columns.tolist())  # Display the column names of the DataFrame

engine = create_engine('sqlite:///song_dataset.db')

df.to_sql('songs', con=engine, if_exists='replace', index=False)
