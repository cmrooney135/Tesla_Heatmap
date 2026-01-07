
from typing import Optional

import pandas as pd
import numpy as np
    
class Cable:
    def __init__(self, type, length, serial_number):
        self.serial_number = serial_number
        self.type = type
        self.length = length
        self.matrix: Optional[np.ndarray] = None
        self.leakage: Optional[pd.DataFrame] = None
        self.leakage_1s: Optional[pd.DataFrame] = None
        self.resistance: Optional[pd.DataFrame] = None
        self.inv_resistance: Optional[pd.DataFrame] = None
        self.continuity: Optional[pd.DataFrame] = None
        self.inv_continuity: Optional[pd.DataFrame] = None
    def set_serial_number(self, sn):
        self.serial_number = sn
    def set_matrix(self, matrix):
        self.matrix = matrix
    def set_type(self,type):
        self.type = type
    def set_length(self, length):
        self.length = length
    
    def add_df(self, type: str, df:pd.DataFrame)->None:
        if(type == "Leakage"):
            self.leakage = df
        elif(type == "1s Leakage"):
            self.leakage_1s = df
        elif(type == "Resistance"):
            self.resistance = df
        elif(type == "Inv Resistance"):
            self.inv_resistance = df
        elif(type == "Continuity"):
            self.continuity = df
        elif(type == "Inv Continuity"):
            self.inv_continuity = df

    def __str__(self):
        return f"Cable SN: {self.serial_number}\n"
