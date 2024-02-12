import pandas as pd
import numpy as np
import json
import pandas as pd
import re
import ast

# Define cleaning functions
def remove_brackets(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("(", "").replace(")", "")
	return text

def make_lists_normal(text):
	if isinstance(text, str):  # Ensure the text is a string
		return text.replace("[", "").replace("]", "").replace("'", "")
	return text

def clear_empty_columns(df):
	return df.replace('', np.nan).dropna(axis=1, how='all')

def cleanCsv(pathIn, pathOut):
	df = pd.read_csv(pathIn)

	for col in df.columns:
		if df[col].dtype == object:
			df[col] = df[col].apply(remove_brackets)
			df[col] = df[col].apply(make_lists_normal)

	df = clear_empty_columns(df)
	df.to_csv(pathOut, index=False)