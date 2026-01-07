
import os
import re
from io import StringIO  # <-- FIXED: Added this import
import pandas as pd
from pathlib import Path

# ---------------------------
# File-type helpers
# ---------------------------
def is_continuity(filename):
    return "continuity-test-revc" in filename.lower()

def is_inv_continuity(filename):
    return "continuity-test-inv-revc" in filename.lower()

def is_leakage(filename):
    return "leakage rev a" in filename.lower()

def is_1s_leakage(filename):
    return "leakage 1s" in filename.lower()

def is_resistance(filename):
    return "resistance rev a" in filename.lower()

def is_inv_resistance(filename):
    return "resistance inverted rev a" in filename.lower()


# ---------------------------
# Parsing helpers
# ---------------------------
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





import re

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

def extract_channel(*texts):
    for t in texts:
        if not isinstance(t, str) or not t:
            continue
        m = re.search(r"\((F\d+)\)", t)
        if m:
            return m.group(1)
        m = re.search(r"\b(F\d+)\b", t)
        if m:
            return m.group(1)
        m = re.search(r"\((R\d+)\)", t)
        if m:
            return m.group(1)
        m = re.search(r"\b(R\d+)\b", t)
        if m:
            return m.group(1)
        if not isinstance(t, str) or not t:
            continue
        m = re.search(r"\((FS\d+)\)", t)
        if m:
            return m.group(1)
        m = re.search(r"\b(FS\d+)\b", t)
        if m:
            return m.group(1)
        m = re.search(r"\((RS\d+)\)", t)
        if m:
            return m.group(1)
        m = re.search(r"\b(RS\d+)\b", t)
        if m:
            return m.group(1)
        
    return "0"


# ---------------------------
# Core function
# ---------------------------
def split_file(filepath, size_folder, serial_folder, output_root: Path):
    """
    Returns two DataFrames:
      - filtered_df: filtered rows (4WIRE for continuity/resistance)
      - extracted_df: Channel + Measured_pA
    Adds file name, size folder, and serial folder columns for traceability.
    """
    fname = os.path.basename(filepath.name)
    type = ""
    content = filepath.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()

    try:
        header_idx = next(i for i, line in enumerate(lines) if "Instruction Type" in line)
    except StopIteration:
        return None, None


    # Extract only lines starting from header_idx
    csv_lines = lines[header_idx:]
    # Remove empty lines
    csv_lines = [line for line in csv_lines if line.strip()]

    # Join back into text
    csv_text = "\n".join(csv_lines)

    # Parse safely, skipping bad lines
    df = pd.read_csv(StringIO(csv_text), on_bad_lines='skip')
    df.columns = [c.strip() for c in df.columns]

    df.columns = [c.strip() for c in df.columns]
    if(is_1s_leakage(fname) or is_leakage(fname)):
        df_filtered = df[df["Instruction Type"].astype(str).str.strip() == "CUSTOM"].copy()
    else:
        # Filter logic
        should_filter_4wire = (
            is_continuity(fname) or is_inv_continuity(fname) or
            is_resistance(fname) or is_inv_resistance(fname)
        )
        if should_filter_4wire and "Instruction Type" in df.columns:
            df_filtered = df[df["Instruction Type"].astype(str).str.strip() == "4WIRE"].copy()
        else:
            df_filtered = df[df["Instruction Type"].astype(str).str.strip() == "CUSTOM"].copy()



    if(is_1s_leakage(fname) or is_leakage(fname)):
        # Extract Channel + Measured_pA
        col_from, col_measured, col_expected = "From Points",  "Value Measured", "Value Expected"
        channels, measured_pa, expected_pa = [], [], []
        for _, row in df_filtered.iterrows():
            ch = extract_channel(row.get(col_from, ""))
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

 
        if(is_leakage(fname)):
            filtered_name = f"leakage_{size_folder}_{serial_folder}.csv"
            filtered_path = output_root / size_folder / serial_folder
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            df_extracted.to_csv(filtered_path, index=False)
            type = "Leakage"
        elif(is_1s_leakage(fname)):
            filtered_name = f"1s_leakage_{size_folder}_{serial_folder}.csv"
            filtered_path =  output_root / size_folder / serial_folder
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            df_extracted.to_csv(filtered_path, index=False)
            type = "1s Leakage"
        return df_extracted, type
    elif(is_resistance(fname) or is_inv_resistance(fname) or is_continuity(fname) or is_inv_continuity(fname)):
        col_from, col_measured, col_expected = "From Points", "Value Measured", "Value Expected"
        channels, measured_r, expected_r = [], [], []

        for _, row in df_filtered.iterrows():
            ch = extract_channel(row.get(col_from, ""))
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

        if(is_resistance(fname)):
           filtered_name = f"resistance_{size_folder}_{serial_folder}.csv"
           filtered_path = output_root / size_folder / serial_folder 
           filtered_path.mkdir(parents=True, exist_ok=True)
           filtered_path = filtered_path / filtered_name
           df_extracted.to_csv(filtered_path, index=False)
           type = "Resistance"
        elif(is_inv_resistance(fname)):
            filtered_name = f"inv_resistance_{size_folder}_{serial_folder}.csv"
            filtered_path = output_root / size_folder / serial_folder 
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name

            df_extracted.to_csv(filtered_path, index=False)
            type = "Inv Resistance"
        elif(is_continuity(fname)):
           filtered_name = f"continuity_{size_folder}_{serial_folder}.csv"
           filtered_path = output_root / size_folder / serial_folder 
           filtered_path.mkdir(parents=True, exist_ok=True)
           filtered_path = filtered_path / filtered_name
           df_extracted.to_csv(filtered_path, index=False)
           type = "Continuity"
        elif(is_inv_continuity(fname)):
            filtered_name = f"inv_continuity_{size_folder}_{serial_folder}.csv"
            filtered_path = output_root / size_folder / serial_folder 
            filtered_path.mkdir(parents=True, exist_ok=True)
            filtered_path = filtered_path / filtered_name
            df_extracted.to_csv(filtered_path, index=False)
            type = "Inv Continuity"
        return df_extracted, type



# ---------------------------
# Main loop
# ---------------------------

def clean_data():
    root_dir = "Data"
    all_filtered = []
    all_extracted = []

    for size_folder in os.listdir(root_dir):
        size_path = os.path.join(root_dir, size_folder)
        if not os.path.isdir(size_path):
            continue

        for serial_folder in os.listdir(size_path):
            serial_path = os.path.join(size_path, serial_folder)
            if not os.path.isdir(serial_path):
                continue

            for file_name in os.listdir(serial_path):
                file_path = os.path.join(serial_path, file_name)
                if not os.path.isfile(file_path):
                    continue

                with open(file_path, "rb") as f:
                    filtered_df, extracted_df = split_file(f, size_folder, serial_folder)
                    if filtered_df is not None:
                        all_filtered.append(filtered_df)
                    if extracted_df is not None and not extracted_df.empty:
                        all_extracted.append(extracted_df)

    # Combine all DataFrames (or empty DataFrame if none)
    combined_filtered = pd.concat(all_filtered, ignore_index=True) if all_filtered else pd.DataFrame()
    combined_extracted = pd.concat(all_extracted, ignore_index=True) if all_extracted else pd.DataFrame()


    return combined_filtered, combined_extracted


if __name__ == "__main__":
    combined_filtered, combined_extracted = clean_data()
