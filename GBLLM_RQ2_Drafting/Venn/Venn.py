import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from venn import venn


def main(dataset_path, output_path=None):
    datasets = ('PIE_Cpp', 'PIE_Py')
    methods = ('direct', 'rag', 'cot', 'sbllm', 'GBLLM')
    total_data_dict = {
        dataset: {method: set() for method in methods}
        for dataset in datasets
    }

    df = pd.read_csv(dataset_path)
    required_columns = {'dataset', 'method', 'case_id'}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing columns in {dataset_path}: {', '.join(sorted(missing_columns))}"
        )

    for (dataset, method), group in df.groupby(['dataset', 'method']):
        if dataset not in total_data_dict:
            raise ValueError(f"Unknown dataset '{dataset}' in {dataset_path}")
        if method not in total_data_dict[dataset]:
            raise ValueError(f"Unknown method '{method}' in {dataset_path}")
        total_data_dict[dataset][method] = set(group['case_id'].tolist())

    # Create figure and two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

    # Plot the first Venn diagram on the first subplot - Key: add ax=ax1 parameter
    venn(total_data_dict["PIE_Cpp"], ax=ax1)  # Explicitly specify drawing on ax1
    # Plot the second Venn diagram on the second subplot - Key: add ax=ax2 parameter
    venn(total_data_dict["PIE_Py"], ax=ax2)  # Explicitly specify drawing on ax2


    # Key point: transform=ax.transAxes indicates using "Axes Coordinate System" (0~1)
    # Add text at the five corners
    five_corner_positions = [     (0.06, 0.7),  # Top left
                        (0.92, 0.7),  # Top right
                        (0.2, 0.06),  # Bottom left
                        (0.80, 0.06),  # Bottom right
                        (0.51, 0.95)    # Top center
                    ]

    # Description text for the five corners
    five_corner_labels = [  "Instruct",
                        "COT", 
                        "GBLLM",
                        "SBLLM",
                        "RAG"
                    ]
    for (x, y), label in zip(five_corner_positions, five_corner_labels):
        ax1.text(x, y, label, transform=ax1.transAxes, ha="center", va="center", fontsize=17, fontweight="bold")
        ax2.text(x, y, label, transform=ax2.transAxes, ha="center", va="center", fontsize=17, fontweight="bold")



    # Set titles
    # ax1.set_title("Experiment Group A", fontsize=14, fontweight='bold')
    # ax2.set_title("Experiment Group B", fontsize=14, fontweight='bold')


    # Add subtitles
    ax1.text(0.5, -0.02, "(a) C++ (O3).", 
            transform=ax1.transAxes, 
            ha='center', 
            fontsize=20, 
            )
    # Add subtitles
    ax2.text(0.5, -0.02, "(b) Python.", 
            transform=ax2.transAxes, 
            ha='center', 
            fontsize=20, 
            )


    # Remove legends
    ax1.legend_.remove()  
    ax2.legend_.remove()  

    # Adjust layout
    plt.tight_layout()
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()


def parse_args():
    parser = argparse.ArgumentParser(description="Draw the RQ2 Venn plots.")
    parser.add_argument(
        "--dataset-path",
        required=True,
        help="CSV with columns: dataset, method, case_id.",
    )
    parser.add_argument(
        "--output-path",
        help="Optional output image path. If omitted, display the plot interactively.",
    )
    return parser.parse_args()


# #################################################################################################################################################❌
if __name__ == '__main__':
    args = parse_args()
    dataset_path = Path(args.dataset_path).expanduser()
    if not dataset_path.is_file():
        raise FileNotFoundError(f"RQ2 Venn CSV not found: {dataset_path}")
    main(dataset_path, args.output_path)
