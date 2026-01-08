from Cable import Cable
import re
import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import seaborn as sns


class Paradise(Cable):
    #region order of channels 
    Top1 = ['A2', 'C2', 'A4', 'C4', 'A6', 'C6', 'A8', 'C8', 'A13', 'C13', 'A15', 'C15', 'A17', 'C17', 
        'A19', 'C19', 'A24', 'C24', 'A26', 'C26', 'A28', 'C28']
    Top2 = ['A30', 'C30', 'A35', 'C35', 'A37', 'C37', 'A39', 'C39', 'A41', 'C41', 'A44', 'B44', 'C47', 
            'A47', 'C49', 'A49', 'C51', 'A51', 'C53', 'A53', 'C58', 'A58']
    Top3 = ['C60', 'A60', 'C62','A62', 'C64', 'A64', 'C69', 'A69', 'C71',
            'A71', 'C73', 'A73', 'C75', 'A75', 'C80', 'A80', 'C82', 'A82', 'C84', 'A84', 'C86', 'A86']
    Top = Top1 + Top2 + Top3

    Bottom1= ['G2', 'E2', 'G4', 'E4', 'G6', 'E6', 'G8', 'E8', 'G13', 'E13', 'G15', 'E15',
            'G17', 'E17', 'G19', 'E19', 'G24', 'E24', 'G26', 'E26', 'G28', 'E28']
    Bottom2 = ['G30','E30','G35','E35','G37','E37','G39','E39','G41','E41',
                'F44','G44','E47','G47','E49','G49','E51','G51','E53','G53','E58','G58']
    Bottom3 = ['E60','G60','E62','G62','E64','G64','E69','G69','E71','G71',
            'E73','G73','E75','G75','E80','G80','E82','G82','E84','G84','E86','G86']
    Bottom = Bottom1 + Bottom2 + Bottom3
    #endregion
    order = Top1 + Top2 + Top3 + Bottom1 + Bottom2 + Bottom3 
    def extract_channel(*texts):
        for t in texts:
            if not isinstance(t, str) or not t:
                continue

            for letter in ("A", "B", "C", "D", "E", "F", "G"):
                m = re.search(rf"\b{letter}\d+\b", t)
                if m:
                    return m.group(0)

        return None
    
    
    def split_top_bottom(self, matrix_type):
        ordered = self.create_matrix(matrix_type)

        # Total counts
        top_len = len(self.Top1) + len(self.Top2) + len(self.Top3)

        leakage = ordered["Leakage"].to_numpy()

        top_leakage = leakage[:top_len]
        bottom_leakage = leakage[top_len:]

        return top_leakage, bottom_leakage

    def create_matrix(self, matrix_type): 
        if(matrix_type == "leakage"):
            df = self.leakage.copy()
        elif(matrix_type == "1s"):
            df = self.leakage_1s.copy()
        df_idx = (
            df.drop_duplicates(subset="Channel", keep="first")
            .set_index("Channel")
        )

        ordered = df_idx.reindex(self.order)

        ordered = ordered.reset_index()
        print("ordered : \n")
        print(ordered)

        ordered["Leakage"] = pd.to_numeric(
            ordered["Measured_pA"], errors="coerce"
        ).fillna(0.0)
        ordered["Leakage"] = ordered["Leakage"].astype(float)
        return ordered

    def draw_heatmap(self, matrix_type):
        ordered = self.create_matrix(matrix_type)
        colors = [
        (0, 0, 1),       # deep blue
        (0.3, 0.3, 1),   # intermediate blue
        (0.6, 0.6, 1),   # light blue
        (1, 1, 1),       # white
        (1, 0.6, 0.6),   # light red
        (1, 0.3, 0.3),   # intermediate red
        (1, 0, 0)        # full red
        ]
        

        nodes = np.linspace(0, 1, len(colors))
        custom_cmap = LinearSegmentedColormap.from_list("custom_red_extended", list(zip(nodes, colors)))
        #split matrix[leakage] into 2 arrays, one for the TOP channels and one for the BOTTOM channels 
        
        top_leakage, bottom_leakage = self.split_top_bottom(matrix_type)
        top_leakage = top_leakage.reshape(1, -1)  
        bottom_leakage = bottom_leakage.reshape(1, -1)
        print("Top len:", len(self.Top))
        fig, axes = plt.subplots(3, 1, figsize=(24, 8), 
                                gridspec_kw={'height_ratios': [1, 0.1, 1]})
        fig.suptitle(f'Heatmap for cable with SN: {self.serial_number}', fontsize=20)

        # Plot first heatmap with color bar
    # Plot first heatmap
        sns.heatmap(top_leakage, ax=axes[0], cmap=custom_cmap, annot=False, square=False,
                    xticklabels=self.Top, yticklabels=[''], cbar=True, cbar_kws={'label': 'Leakage(pA)'},
                    vmin=0.0, vmax=600)

        # Leave middle subplot blank
        axes[1].axis('off')

        # Plot second heatmap
        sns.heatmap(bottom_leakage, ax=axes[2], cmap=custom_cmap, annot=False, square=False,
                    xticklabels=self.Bottom, yticklabels=[''], cbar=True, cbar_kws={'label': 'Leakage(pA)'},
                    vmin=0.0, vmax=600)


        # Adjust layout to make room for the title
        plt.tight_layout(rect=[0, 0, 1, 0.90])
        return fig, axes
