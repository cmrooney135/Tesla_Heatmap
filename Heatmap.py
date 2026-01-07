import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from matplotlib.colors import LinearSegmentedColormap
Top = ['']
TopS = ['']

Bottom = ['']
BottomS = ['']

Top = Top + TopS
Bottom = BottomS + Bottom 


colors = [
    (0, 0, 1),       # deep blue
    (0.3, 0.3, 1),   # intermediate blue
    (0.6, 0.6, 1),   # light blue
    (1, 1, 1),       # white
    (1, 0.6, 0.6),   # light red
    (1, 0.3, 0.3),   # intermediate red
    (1, 0, 0)        # full red
]



nodes = [0.0, 1.0/6.0, 2.0/6.0, 3.0/6.0, 4.0/6.0, 5.0/6.0, 1.0]
custom_cmap = LinearSegmentedColormap.from_list("custom_red_extended", list(zip(nodes, colors)))

def display_matrix(cable):
    matrix = np.array(cable.matrix, dtype=np.float64)
    print(matrix)
    matrix1 = matrix[0].reshape(1, -1)  
    matrix2 = matrix[1].reshape(1, -1)
    sn = cable.serial_number

    fig, axes = plt.subplots(3, 1, figsize=(24, 8), 
                             gridspec_kw={'height_ratios': [1, 0.1, 1]})
    fig.suptitle(f'Heatmap for cable with SN: {sn}', fontsize=20)

    # Plot first heatmap with color bar
    
# Plot first heatmap
    sns.heatmap(matrix1, ax=axes[0], cmap=custom_cmap, annot=False, square=False,
                xticklabels=Top, yticklabels=[''], cbar=True, cbar_kws={'label': 'Intensity'},
                vmin=0.0, vmax=6.0)

    # Leave middle subplot blank
    axes[1].axis('off')

    # Plot second heatmap
    sns.heatmap(matrix2, ax=axes[2], cmap=custom_cmap, annot=False, square=False,
                xticklabels=Bottom, yticklabels=[''], cbar=True, cbar_kws={'label': 'Intensity'},
                vmin=0.0, vmax=6.0)


    # Adjust layout to make room for the title
    plt.tight_layout(rect=[0, 0, 1, 0.90])
    st.pyplot(plt)