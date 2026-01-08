import pandas as pd
from io import StringIO  
import re

from pathlib import Path

UNIT_TO_PA = {
    "pa": 1, "pamps": 1, "pamp": 1,
    "na": 1e3, "namps": 1e3, "namp": 1e3,
    "ua": 1e6, "µa": 1e6, "microa": 1e6,
    "ma": 1e9, "mamps": 1e9, "mamp": 1e9,
    "a": 1e12, "amps": 1e12, "amp": 1e12
}


UNIT_TO_MOHM = {
    "mohm": 1, "milliohm": 1, "milliohms": 1,  # already in mOhm
    "ohm": 1000, "ohms": 1000,                 # convert Ohm → mOhm
    "kohm": 1e6, "kiloohm": 1e6, "kiloohms": 1e6,  # kOhm → mOhm
    "gohm": 1e12, "gigaohm": 1e12, "gigaohms": 1e12,  # GOhm → mOhm
    "megaohm": 1e9, "mohm_big": 1e9,           # MΩ → mOhm
    "uohm": 1e-3, "microohm": 1e-3, "microohms": 1e-3  # µΩ → mOhm
}
def is_continuity(testname):
    return "continuity-test-revc" in testname.lower()

def is_inv_continuity(testname):
    return "continuity-test-inv-revc" in testname.lower()

def is_leakage(testname):

    return "leakage rev a" in testname.lower()

def is_1s_leakage(testname):
    return "leakage 1s" in testname.lower()

def is_resistance(testname):
    return "resistance rev a" in testname.lower()

def is_inv_resistance(testname):
    return "resistance inverted rev a" in testname.lower()
def parse_ohms(text):
    """
    Parse a string for resistance values in ohms (Ω, ohm, kohm, mohm, uohm).
    Returns (value, unit) or (None, None) if not found.
    """
    if not isinstance(text, str) or not text:
        return None, None
    
    # Match number + ohm unit
    m = re.search(r"([+-]?\d+(?:\.\d+)?)\s*(ohm|Ω|kohm|mohm|uohm)", text, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower().replace(" ", "")
        return val, unit
    
    return None, None


def parse_current(text):
    """
    Parse a string for current values in nA, pA, µA, mA, etc.
    Returns (value, unit) or (None, None) if not found.
    """
    if not isinstance(text, str) or not text:
        return None, None
    
    # Match number + current unit
    m = re.search(r"([+-]?\d+(?:\.\d+)?)\s*([munpµ]A)", text, re.IGNORECASE)
    if m:
        val = float(m.group(1))
        unit = m.group(2).lower().replace("µ", "u")  # normalize µ to u
        return val, unit
    
    return None, None



def to_pA(value, unit):
    if value is None or unit is None:
        return None
    key = unit.lower().strip()
    key = key.replace("pamp", "pa").replace("namp", "na").replace("uamp", "ua").replace("microa", "µa")
    key = key.rstrip("s")
    mult = UNIT_TO_PA.get(key)
    return value * mult if mult else None

def to_mO(value, unit):
    if value is None or unit is None:
        return None
    key = unit.lower().strip()
    key = key.replace("mohm", "mohm").replace("nohm", "nohm").replace("uohm", "uohm").replace("kohm", "kohm")
    key = key.rstrip("s")
    mult = UNIT_TO_MOHM.get(key)
    return value * mult if mult else None

            
def process_csv(cable, fname):
    if(cable.type == "Tesla"):
        output_root = "teslaTemp"
    elif(cable.type == "Paradise"):
        output_root = "paradiseTemp"
    test_name = ""
    content = fname.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()
    try:
        header_idx = next(i for i, line in enumerate(lines) if "Instruction Type" in line)
    except StopIteration:
        return None
    
    test_name_pattern = re.compile(r'(?i)\btest\s*name\b\s*[:,\-]\s*(.*)')

    header_lines = lines[:header_idx]
    for line in header_lines:
        m = test_name_pattern.search(line)
        if m:
            candidate = m.group(1).strip()
            if candidate:
                test_name = candidate
                break


    csv_lines = lines[header_idx:]
    # Remove empty lines
    csv_lines = [line for line in csv_lines if line.strip()]

    # Join back into text
    csv_text = "\n".join(csv_lines)

    # Parse safely, skipping bad lines
    df = pd.read_csv(StringIO(csv_text), on_bad_lines='skip')
    df.columns = [c.strip() for c in df.columns]
    if(is_1s_leakage(test_name) or is_leakage(test_name)):
            df_filtered = df[df["Instruction Type"].astype(str).str.strip() == "CUSTOM"].copy()

    else:
        # Filter logic
        should_filter_4wire = (
            is_continuity(test_name) or is_inv_continuity(test_name) or
            is_resistance(test_name) or is_inv_resistance(test_name)
        )
        if should_filter_4wire and "Instruction Type" in df.columns:
            df_filtered = df[df["Instruction Type"].astype(str).str.strip() == "4WIRE"].copy()
        else:
            df_filtered = df[df["Instruction Type"].astype(str).str.strip() == "CUSTOM"].copy()

    if(is_1s_leakage(test_name) or is_leakage(test_name)):
        # Extract Channel + Measured_pA
        col_from, col_measured, col_expected = "From Points",  "Value Measured", "Value Expected"
        channels, measured_pa, expected_pa = [], [], []
        for _, row in df_filtered.iterrows():
            ch = cable.extract_channel(row.get(col_from, ""))
            if("a" not in row.get(col_measured, "").lower()):
                continue
            val, unit = parse_current(row.get(col_measured, ""))
            exp_val, exp_unit = parse_current(row.get(col_expected, ""))
            if exp_val is None or exp_unit is None:
                expected_pa_val = 0
            else:
                expected_pa_val = to_pA(exp_val, exp_unit)
            pa = to_pA(val, unit)
            channels.append(ch)
            measured_pa.append(pa)
            expected_pa.append(expected_pa_val)



        df_extracted = pd.DataFrame({
            "Channel": channels,
            "Measured_pA": measured_pa,
            "Expected_pA": expected_pa,
        }).dropna()


        if(is_leakage(test_name)):
            filtered_name = f"leakage_{cable.length}_{cable.serial_number}.csv"
            
            filtered_path = (
                Path(output_root)
                / str(cable.length) 
                / str(cable.serial_number)
            )
            filtered_path.mkdir(parents=True, exist_ok=True)

            filtered_path = filtered_path / filtered_name
            cable.leakage = df_extracted
            df_extracted.to_csv(filtered_path, index=False)
        elif(is_1s_leakage(test_name)):
            filtered_name = f"1sleakage_{cable.length}_{cable.serial_number}.csv"
            
            filtered_path = (
                Path(output_root)
                / str(cable.length)
                / str(cable.serial_number)
            )
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            cable.leakage_1s = df_extracted
            df_extracted.to_csv(filtered_path, index=False)
    elif(is_resistance(test_name) or is_inv_resistance(test_name) or is_continuity(test_name) or is_inv_continuity(test_name)):
        col_from, col_measured, col_expected = "From Points", "Value Measured", "Value Expected"
        channels, measured_r, expected_r = [], [], []

        for _, row in df_filtered.iterrows():
            ch = cable.extract_channel(row.get(col_from, ""))
            if("ohm" not in row.get(col_measured, "").lower()):
                continue
            val, unit = parse_ohms(row.get(col_measured, ""))
            expected = parse_ohms(row.get(col_expected, ""))
            mO = to_mO(val, unit)
            expected = to_mO(expected[0], expected[1])
            channels.append(ch)
            measured_r.append(mO)
            expected_r.append(expected)

        df_extracted = pd.DataFrame({
            "Channel": channels,
            "Measured_R (mOhm)": measured_r,
            "Expected_R (mOhm)": expected_r,
        }).dropna()

        if(is_resistance(test_name)):
            filtered_name = f"resistance_{cable.length}_{cable.serial_number}.csv"
            
            filtered_path = (
                Path(output_root)
                / str(cable.length)
                / str(cable.serial_number)
            )
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            cable.resistance = df_extracted
            df_extracted.to_csv(filtered_path, index=False)
        elif(is_inv_resistance(test_name)):
            filtered_name = f"inv_resistance_{cable.length}_{cable.serial_number}.csv"
            
            filtered_path = (
                Path(output_root)
                / str(cable.length)
                / str(cable.serial_number)
            )
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            cable.inv_resistance = df_extracted
            df_extracted.to_csv(filtered_path, index=False)
        elif(is_continuity(test_name)):
            filtered_name = f"continuity_{cable.length}_{cable.serial_number}.csv"
            
            filtered_path = (
                Path(output_root)
                / str(cable.length)
                / str(cable.serial_number)
            )
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            cable.continuity = df_extracted
            df_extracted.to_csv(filtered_path, index=False)
            type = "Continuity"
        elif(is_inv_continuity(test_name)):
            filtered_name = f"inv_continuity_{cable.length}_{cable.serial_number}.csv"
            
            filtered_path = (
                Path(output_root)
                / str(cable.length)
                / str(cable.serial_number)
            )
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            cable.inv_continuity = df_extracted
            df_extracted.to_csv(filtered_path, index=False)
 

