from uploadData import upload_and_split_file
import os
from Cable import Cable
import re

filenames = ["Leakage Fail-selected\\017AB4A061.csv","Leakage Fail-selected\\016B6CC061.csv","Leakage Fail-selected\\017AC03061.csv", "TeslaData\\11989-0312-Continuity-Test-Inv-RevC_TestReport_ParadiseContinuity_791_1_03AA0B0071.csv",
             "TeslaData\\11989-0312-Leakage Rev A_TestReport_Eagle Tester 1_184_1_03AA0B0071.csv"]
os.makedirs("temp", exist_ok=True)
cables = []



pattern = re.compile(r"(?<![A-Za-z0-9])0[0-4][A-Za-z0-9]{8}(?![A-Za-z0-9])", re.IGNORECASE)

for uploaded_file in filenames:
    serial_number = "Unknown"
    match = pattern.search(uploaded_file)  # or uploaded_file.name
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
        print("Cable serial number: ", {cable.serial_number}, "\n")
        print("Cable Length: ", {cable.length}, "\n")
        print("Cable type: ", {cable.type}, "\n")
        if(cable.leakage is not None):
            print("Cable leakage data: ", {cable.leakage.head}, "\n")
        if(cable.continuity is not None):
            print("Cable continuity data :", {cable.continuity.head}, "\n")
