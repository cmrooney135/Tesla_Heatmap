from __future__ import annotations

from typing import Optional


from typing import Optional
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
    
class Cable(ABC):
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

    def set_serial_number(self, sn: str) -> None:
        self.serial_number = sn

    def set_matrix(self, matrix: np.ndarray) -> None:
        self.matrix = matrix

    def set_type(self, type: str) -> None:
        self.type = type

    def set_length(self, length: float) -> None:
        self.length = length


    # ---------- Processing contract: subclasses must implement these ----------

    @abstractmethod
    def create_matrix(self, matrix_type) -> pd.DataFrame:
        pass
    @abstractmethod
    def extract_channel(self) -> pd.DataFrame:
        pass
    @abstractmethod
    def draw_heatmap(self, matrix_type):
        pass
    @abstractmethod
    def create_matrix(self, matrix_type):
        pass
    
    def __str__(self):
        return f"Cable SN: {self.serial_number}\n"
    def create_matrix(self, matrixData):
        return None
    
