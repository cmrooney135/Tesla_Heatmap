import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
from Cable import Cable
from Heatmap import display_matrix  
from uploadData import upload_and_split_file  
import os
from createMatrix import create_matrix

st.title("Heatmap Visualization for Cables")

os.makedirs("temp", exist_ok=True)
uploaded_files = st.file_uploader("Upload your CSV files", type="csv", accept_multiple_files=True)
cables = []

pattern = re.compile(r"0[0-4].{8}")

if uploaded_files:
    for uploaded_file in uploaded_files:
        serial_number = "Unknown"
        match = pattern.search(uploaded_file.title)  # or uploaded_file.name
        if match:
            serial_number = match.group()
            if len(serial_number) >= 2:
                    first_two_digits = serial_number[:2]
                    second_digit = first_two_digits[1]          
                    if second_digit == "0":
                        cable_type = "Paradise"
                        cable_length = 11
                    elif second_digit == "1":
                        cable_type = "Paradise"
                        cable_length = 15
                    elif second_digit == "3":
                        cable_type = "Tesla"
                        cable_length = 11
                    elif second_digit == "4":
                        cable_type = "Tesla"
                        cable_length = 15

            cable = Cable(cable_type, cable_length, serial_number)
            

    # Upload and split the file
        upload_and_split_file(uploaded_file)
        with open("temp/txt_temp.txt", "r", encoding="utf-8") as txt_file:
            for line in txt_file:
                match = re.search(r"S/N[:\s,]*([A-Z0-9]+)", line)
                if match:
                    serial_number = match.group(1)
                    break
        # Read the CSV data into a DataFrame
        df = pd.read_csv("temp/csv_temp.csv")
        df.columns = df.columns.str.strip()
        matrix = create_matrix(df)
        #do analysis on df to create port_matrix
        # 
        cable = Cable(serial_number, matrix)    
        cables.append(cable)
        display_matrix(cable)
