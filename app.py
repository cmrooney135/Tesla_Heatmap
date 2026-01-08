import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
from Cable import Cable
from Heatmap import display_matrix  
from uploadData import process_csv
import os
from createMatrix import create_matrix
from Tesla import Tesla
from Paradise import Paradise


import os
import io
import zipfile

def build_zip_for_cable(cable, base_map=None, temp_root="."):
    """
    Returns (zip_buffer, zip_name) if success, else (None, error_msg).
    Expects folder structure:
      TeslaTemp/<serial_number>/...
      ParadiseTemp/<serial_number>/...
    """
    if base_map is None:
        base_map = {"Tesla": "teslaTemp", "Paradise": "paradiseTemp"}

    base_dir = base_map.get(cable.type)
    if not base_dir:
        return None, f"Unknown cable_type '{cable.type}'"
    

    if not cable.serial_number:
        return None, "Missing serial number"
    
    length_folder = f"{cable.length}"
    target_dir = os.path.join(
        temp_root,
        base_dir,
        length_folder,
        str(cable.serial_number)
    )
    
    if not os.path.isdir(target_dir):
        return None, f"Folder not found: {target_dir}"

    # Check folder is not empty
    has_files = any(
        len(files) > 0 for _, _, files in os.walk(target_dir)
    )
    if not has_files:
        return None, f"No files in {target_dir}"

    # Build ZIP in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(target_dir):
            for fname in files:
                abs_path = os.path.join(root, fname)
                # Make paths inside the zip start at <serial_number>/...
                rel_from_sn = os.path.relpath(abs_path, start=target_dir)
                arcname = os.path.join(str(cable.serial_number), rel_from_sn)
                zf.write(abs_path, arcname=arcname)

    zip_buffer.seek(0)
    zip_name = f"{cable.serial_number}_data.zip"
    return zip_buffer, zip_name


def create_cable(cable_type, cable_length, serial_number):
    if cable_type == "Tesla":
        return Tesla(cable_type, cable_length, serial_number)
    elif cable_type == "Paradise":
        return Paradise(cable_type, cable_length, serial_number)
    else:
        raise ValueError(f"Unknown cable type: {cable_type}")


st.set_page_config(
    layout="wide"
)

st.title("Heatmap Visualization for Cables")

os.makedirs("temp", exist_ok=True)
uploaded_files = st.file_uploader("Upload your CSV files", type="csv", accept_multiple_files=True)
cables = {}

pattern = re.compile(r"(?<![A-Za-z0-9])0[0-4][A-Za-z0-9]{8}(?![A-Za-z0-9])", re.IGNORECASE)

if uploaded_files:
    for uploaded_file in uploaded_files:
        serial_number = "Unknown"
            
        target_text = uploaded_file.name

        match = pattern.search(target_text)  # or uploaded_file.name
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

            
            if serial_number in cables:
                cable = cables[serial_number]
            else:
                cable = create_cable(cable_type, cable_length, serial_number)
                cables[serial_number] = cable

            process_csv(cable, uploaded_file)

    COL_LAYOUT = [3, 3, 2, 5, 5, 4]
    st.subheader("Processed Cables")


    disabled_leakage = getattr(cable, "leakage", None) is None
    print(getattr(cable, "leakage", None))
    disabled_1s = getattr(cable, "leakage_1s", None) is None
    print(getattr(cable, "leakage_1s", None))

    header_cols = st.columns(COL_LAYOUT)
    header_cols[0].markdown("**Serial Number**")
    header_cols[1].markdown("**Cable Type**")
    header_cols[2].markdown("**Length (in)**")
    header_cols[3].markdown("**Leakage Heatmap**", disabled_leakage)
    header_cols[4].markdown("**1s Leakage Heatmap**", disabled_1s)
    header_cols[5].markdown("**Download CSVs**")

    for cable in cables.values():
        cols = st.columns(COL_LAYOUT)

        cols[0].markdown(cable.serial_number)
        cols[1].markdown(cable.type)
        cols[2].markdown(cable.length)
        
        show_key_leak = f"show_leakage_{cable.serial_number}"
        show_key_1s   = f"show_1s_{cable.serial_number}"

        if show_key_leak not in st.session_state:
            st.session_state[show_key_leak] = False
        if show_key_1s not in st.session_state:
            st.session_state[show_key_1s] = False

        if cols[3].button(
            "Generate",
            key=f"leakage_{cable.serial_number}",
            disabled=disabled_leakage
        ):
            st.session_state[show_key_leak] = True
            
        if cols[4].button(
            "Generate",
            key=f"leakage_1s_{cable.serial_number}",
            disabled=disabled_1s
        ):
            st.session_state[show_key_1s] = True
        
        if st.session_state[show_key_leak]:
            fig_leak, ax_leak = cable.draw_heatmap("leakage")
            cols[3].pyplot(fig_leak, use_container_width=True)

        if st.session_state[show_key_1s]:
            fig_1s, ax_1s = cable.draw_heatmap("1s")
            cols[4].pyplot(fig_1s, use_container_width=True)

        zip_buf, zip_name_or_err = build_zip_for_cable(
            cable,
            base_map={"Tesla": "teslaTemp", "Paradise": "paradiseTemp"},
            temp_root="." 
        )

        if zip_buf:
            cols[5].download_button(
                label="Download ZIP",
                data=zip_buf,
                file_name=zip_name_or_err,   # this is the zip_name
                mime="application/zip",
                key=f"download_{cable.serial_number}",
            )

        else:
                # Show a disabled button with a tooltip-like note
                cols[5].button(
                    "Download ZIP",
                    key=f"download_disabled_{cable.serial_number}",
                    disabled=True,
                    help=str(zip_name_or_err)  # this is the error message
                )