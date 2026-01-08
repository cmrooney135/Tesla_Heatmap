from Cable import Cable
import re
import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import seaborn as sns

class Tesla(Cable):
    #region order of channels 
    Top = [
        "F1","R1","F2","R2","F3","R3","F4","R4",
        "F5","R5","F6","R6","F7","R7","F8","R8",
        "F9","R9","F10","R10","F11","R11","F12","R12",
        "F13","R13","F14","R14","F15","R15","F16","R16",

        "F17","R17","F18","R18","F19","R19","F20","R20",
        "F21","R21","F22","R22","F23","R23","F24","R24",
        "F25","R25","F26","R26","F27","R27","F28","R28",
        "F29","R29","F30","R30","F31","R31","F32","R32",
    ]



    TopS = [
        "FS1","RS1","FS2","RS2",
        "FS3","RS3","FS4","RS4",
        "RS5","FS5","FS6","RS6",
        "FS7","RS7","FS8","RS8",
        "FS9","RS9","FS10","RS10",
        "FS11","RS11","FS12","RS12",
        "FS13","RS13","FS14","RS14",
        "FS15","RS15","FS16","RS16",

        "FS17","RS17","FS18","RS18",
        "FS19","RS19","FS20","RS20",
        "FS21","RS21","FS22","RS22",
        "FS23","RS23","FS24","RS24",
        "FS25","RS25","FS26","RS26",
        "FS27","RS27","FS28","RS28",
        "FS29","RS29","FS30","RS30",
        "FS31","RS31","FS32","RS32"
    ]


    Bottom = [
        "R64","F64","R63","F63","R62","F62","R61","F61",
        "R60","F60","R59","F59","R58","F58","R57","F57",
        "R56","F56","R55","F55","R54","F54","R53","F53",
        "R52","F52","R51","F51","R50","F50","R49","F49",
        
        "R48","F48","R47","F47","R46","F46","R45","F45",
        "R44","F44","R43","F43","R42","F42","R41","F41",
        "R40","F40","R39","F39","R38","F38","R37","F37",
        "R36","F36","R35","F35","R34","F34","R33","F33",

    ]

    BottomS = [
        "RS64", "FS64", "RS63", "FS63",
        "RS62", "FS62", "RS61", "FS61",
        "RS60", "FS60", "RS59", "FS59",
        "RS58", "FS58", "RS57", "FS57",
        "RS56", "FS56", "RS55", "FS55",
        "RS54", "FS54", "RS53", "FS53",
        "RS52", "FS52", "RS51", "FS51",
        "RS50", "FS50", "RS49", "FS49",
        
        "RS48", "FS48", "RS47", "FS47",
        "RS46", "FS46", "RS45", "FS45",
        "RS44", "FS44", "RS43", "FS43",
        "RS42", "FS42", "RS41", "FS41",
        "RS40", "FS40", "RS39", "FS39",
        "RS38", "FS38", "RS37", "FS37",
        "RS36", "FS36", "RS35", "FS35",
        "RS34", "FS34", "RS33", "FS33"

    ]
    #endregion

    order = Top + TopS + BottomS + Bottom

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
    
    def create_matrix(self, matrix_type): 
        if(matrix_type == "leakage"):
            df = self.leakage.copy()
            print("\ndf for LEAKAGE: ")
            print(df)
        elif(matrix_type == "1s"):
            df = self.leakage_1s.copy()
            print("\ndf for 1s: ")
            print(df)
    
        df_idx = (
            df.drop_duplicates(subset="Channel", keep="first")
            .set_index("Channel")
        )
        ordered = df_idx.reindex(self.order)
        ordered = ordered.reset_index()
        ordered["Leakage"] = ordered["Measured_pA"].fillna(0)
        ordered["Leakage"] = ordered["Leakage"].astype(float)
        return ordered
    def split_top_bottom(self, matrix_type):

        ordered = self.create_matrix(matrix_type)

        # Lengths
        top_len     = len(self.Top)
        topS_len    = len(self.TopS)
        bottomS_len = len(self.BottomS)
        bottom_len  = len(self.Bottom)

        leakage = ordered["Leakage"].to_numpy()

        # Cumulative indices
        i0 = 0
        i1 = i0 + top_len
        i2 = i1 + topS_len
        i3 = i2 + bottomS_len
        i4 = i3 + bottom_len  # should equal len(leakage)

        # Optional sanity check
        if i4 != len(leakage):
            raise ValueError(
                f"Expected {i4} rows from channel lists, got {len(leakage)} in ordered. "
                "Ensure ordered is filtered/reordered to exactly Top+TopS+BottomS+Bottom."
            )

        # Proper slices
        top_leakage      = leakage[i0:i1]
        topS_leakage     = leakage[i1:i2]
        bottomS_leakage  = leakage[i2:i3]
        bottom_leakage   = leakage[i3:i4]


        return top_leakage, topS_leakage, bottomS_leakage, bottom_leakage
    
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


        print(ordered.head)
        """draw the damn heat map using matplotlib"""
        print("drawing tesla heatmap")
        top_leakage, topS_leakage, bottomS_leakage, bottom_leakage = self.split_top_bottom(matrix_type)


        top_leakage = top_leakage.reshape(1, -1)  
        bottom_leakage = bottom_leakage.reshape(1, -1)
        topS_leakage = topS_leakage.reshape(1, -1)  
        bottomS_leakage = bottomS_leakage.reshape(1, -1)
        
        fig, axes = plt.subplots(
            nrows=5,
            ncols=1,
            figsize=(24, 8),
            gridspec_kw={
                'height_ratios': [1.0, 0.25, 0.15, 0.25, 1.0]
            }
        )
        
        fig.suptitle(
            f'Heatmap for cable with SN: {self.serial_number}',
            fontsize=20
        )
        
        sns.heatmap(
            top_leakage,
            ax=axes[0],
            cmap=custom_cmap,
            annot=False,
            square=False,
            xticklabels=self.Top,
            yticklabels=['Top'],
            cbar=True,
            cbar_kws={'label': 'Leakage (pA)'},
            vmin=0.0,
            vmax=1000
        )
        
        sns.heatmap(
            topS_leakage,
            ax=axes[1],
            cmap=custom_cmap,
            annot=False,
            square=False,
            xticklabels=self.TopS,   # shared X visually
            yticklabels=['TopS'],
            cbar=True,
            cbar_kws={'label': 'Leakage (pA)'},
            vmin=0.0,
            vmax=1000
        )
        
        axes[2].axis('off')
        
        sns.heatmap(
            bottomS_leakage,
            ax=axes[3],
            cmap=custom_cmap,
            annot=False,
            square=False,
            xticklabels=self.BottomS,
            yticklabels=['BottomS'],
            cbar=True,
            cbar_kws={'label': 'Leakage(pA)'},
            vmin=0.0,
            vmax=1000
        )
        
        sns.heatmap(
            bottom_leakage,
            ax=axes[4],
            cmap=custom_cmap,
            annot=False,
            square=False,
            xticklabels=self.Bottom,
            yticklabels=['Bottom'],
            cbar=True,
            cbar_kws={'label': 'Leakage (pA)'},
            vmin=0.0,
            vmax=1000
        )

        axes[0].xaxis.tick_top()
        axes[0].xaxis.set_label_position('top')

        axes[1].xaxis.tick_bottom()
        axes[1].xaxis.set_label_position('bottom')

        axes[2].xaxis.tick_bottom()
        axes[2].xaxis.set_label_position('bottom')

        axes[3].xaxis.tick_top()
        axes[3].xaxis.set_label_position('top')


        for ax in [axes[0], axes[1], axes[3], axes[4]]:
            ax.set_ylabel('')
            ax.tick_params(axis='y', rotation=0)
            ax.tick_params(axis='x', labelrotation=90)


        plt.tight_layout(rect=[0, 0, 1, 0.92])

        return fig, axes




