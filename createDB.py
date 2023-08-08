from dotenv import load_dotenv
import openai
import os
import pandas as pd
import sqlite3

#load data
df = pd.read_excel('Employee_Data1.xlsx')
#clean data
df.columns = df.columns.str.strip()
#create databse
connection = sqlite3.connect('demo1.db')
#uplaod  data from file
df.to_sql('Employees', connection, if_exists ='replace')
#close the connectin
connection.close()