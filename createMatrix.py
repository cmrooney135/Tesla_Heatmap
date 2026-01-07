import numpy as np
import re
import matplotlib.pyplot as plt
import pandas as pd
#create dictionary for the titles of channels corresponding to the number in csv
Top1 = ['A2', 'C2', 'A4', 'C4', 'A6', 'C6', 'A8', 'C8', 'A13', 'C13', 'A15', 'C15', 'A17', 'C17', 
       'A19', 'C19', 'A24', 'C24', 'A26', 'C26', 'A28', 'C28']
Top2 = ['A30', 'C30', 'A35', 'C35', 'A37', 'C37', 'A39', 'C39', 'A41', 'C41', 'A44', 'B44', 'C47', 
        'A47', 'C49', 'A49', 'C51', 'A51', 'C53', 'A53', 'C58', 'A58']
Top3 = ['C60', 'A60', 'C62','A62', 'C64', 'A64', 'C69', 'A69', 'C71',
        'A71', 'C73', 'A73', 'C75', 'A75', 'C80', 'A80', 'C82', 'A82', 'C84', 'A84', 'C86', 'A86']

Bottom1= ['G2', 'E2', 'G4', 'E4', 'G6', 'E6', 'G8', 'E8', 'G13', 'E13', 'G15', 'E15',
          'G17', 'E17', 'G19', 'E19', 'G24', 'E24', 'G26', 'E26', 'G28', 'E28']
Bottom2 = ['G30','E30','G35','E35','G37','E37','G39','E39','G41','E41',
            'F44','G44','E47','G47','E49','G49','E51','G51','E53','G53','E58','G58']
Bottom3 = ['E60','G60','E62','G62','E64','G64','E69','G69','E71','G71',
           'E73','G73','E75','G75','E80','G80','E82','G82','E84','G84','E86','G86']

custom_order = Top1 + Top2 + Top3 + Bottom1 + Bottom2 + Bottom3


def convert_to_nanoamps(value):

    if isinstance(value, str):
        value = value.strip().lower().replace(',', '')
        if 'pa' in value:
            return float(value.replace('pa', '').strip()) * 1e-3

        elif 'na' in value:
            return float(value.replace('na', '').strip())
    try:
        return float(value)  # Assume it's already in nanoamps
    except:
        return None


def create_matrix(df):
    df['Current_nA'] = df['Value Measured'].apply(convert_to_nanoamps)
    new_df = pd.DataFrame(index=range(len(custom_order)), columns=['From Points', 'Current_nA'])
    for j, item in enumerate(custom_order):
        for i in range(len(df)):
            if (item +" (DIB - SIGNAL)") in str(df.at[i, 'From Points']):
                new_df.at[j, 'From Points'] = item
                new_df.at[j, 'Current_nA'] = (df.at[i, 'Current_nA'])
            if (item +" (DIB - DGS)") in str(df.at[i, 'From Points']):
                new_df.at[j, 'From Points'] = item
                new_df.at[j, 'Current_nA'] = (df.at[i, 'Current_nA'])


    new_df.to_csv("temp/processed_matrix.csv", index=False)
    current_values = new_df['Current_nA'].dropna().values
    if current_values.size != 132:
        raise ValueError("DataFrame must contain exactly 132 values for a 2x66 grid.")
    data_matrix = current_values.reshape((2, 66))
    
    return data_matrix
