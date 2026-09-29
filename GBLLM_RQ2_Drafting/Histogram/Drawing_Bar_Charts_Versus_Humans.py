import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


METHODS = ['Instruction', 'ICL', 'RAG', 'COT', 'SBLLM', 'GBLLM']
METRICS = ['NC', 'NO', 'NH', 'FH']


def load_plot_data(dataset_path):
    df = pd.read_csv(dataset_path)
    required_columns = {'dataset', 'method', *METRICS}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing columns in {dataset_path}: {', '.join(sorted(missing_columns))}"
        )

    duplicated = df.duplicated(subset=['dataset', 'method'], keep=False)
    if duplicated.any():
        duplicate_pairs = df.loc[duplicated, ['dataset', 'method']].to_dict('records')
        raise ValueError(f"Duplicate dataset/method rows: {duplicate_pairs}")

    indexed = df.set_index(['dataset', 'method'])
    plot_data = {}
    for dataset in ('PIE_Cpp', 'PIE_Py'):
        missing_methods = [method for method in METHODS if (dataset, method) not in indexed.index]
        if missing_methods:
            raise ValueError(
                f"Missing methods for {dataset}: {', '.join(missing_methods)}"
            )
        plot_data[dataset] = {
            metric: [float(indexed.loc[(dataset, method), metric]) for method in METHODS]
            for metric in METRICS
        }
    return plot_data


def plot_example_chart(dataset_path, output_path=None):
    plot_data = load_plot_data(dataset_path)
    categories = METHODS
    PIE_Cpp_NC = plot_data['PIE_Cpp']['NC']
    PIE_Cpp_NO = plot_data['PIE_Cpp']['NO']
    PIE_Cpp_NH = plot_data['PIE_Cpp']['NH']
    PIE_Cpp_FH = plot_data['PIE_Cpp']['FH']
    PIE_Py_NC = plot_data['PIE_Py']['NC']
    PIE_Py_NO = plot_data['PIE_Py']['NO']
    PIE_Py_NH = plot_data['PIE_Py']['NH']
    PIE_Py_FH = plot_data['PIE_Py']['FH']


    x = np.arange(len(categories))
    width = 0.2

    # fig, ax = plt.subplots(figsize=(11, 4))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 3.7), sharey=True)

    # Plot four groups of bars (Subplot 1)
    ax1.bar(x - 1.5*width, PIE_Cpp_NC, width, label='NC', color='#FE7E0D', hatch='\\\\\\\\')
    ax1.bar(x - 0.5*width, PIE_Cpp_NO, width, label='NO', color='#1BA1E2', hatch='||||')
    ax1.bar(x + 0.5*width, PIE_Cpp_NH, width, label='NH', color='#8C564B', hatch='*')
    ax1.bar(x + 1.5*width, PIE_Cpp_FH, width, label='FH', color='#66CC66', hatch='/////')

    # Plot four groups of bars (Subplot 2)
    ax2.bar(x - 1.5*width, PIE_Py_NC, width, label='NC', color='#FE7E0D', hatch='\\\\\\\\')
    ax2.bar(x - 0.5*width, PIE_Py_NO, width, label='NO', color='#1BA1E2', hatch='||||')
    ax2.bar(x + 0.5*width, PIE_Py_NH, width, label='NH', color='#8C564B', hatch='*')
    ax2.bar(x + 1.5*width, PIE_Py_FH, width, label='FH', color='#66CC66', hatch='/////')
    

    # Coordinates and style settings
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=15)
    ax1.set_ylim(0, 70)
    ax1.set_ylabel('Percentage (%)', fontsize=15)
    ax1.yaxis.grid(True, linestyle='--', alpha=0.5)

    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, fontsize=15)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.5)


    # Configure spines (borders)
    ax1.spines['top'].set_visible(True)
    ax1.spines['bottom'].set_visible(True)
    ax1.spines['left'].set_visible(True)
    ax1.spines['right'].set_visible(False)

    ax2.spines['top'].set_visible(True)
    ax2.spines['bottom'].set_visible(True)
    ax2.spines['left'].set_visible(False)
    ax2.spines['right'].set_visible(True)


    # 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
    # ax.legend(frameon=False, fontsize=10, loc='upper right')
    ax1.legend(frameon=False, loc='best')
    # ax2.legend(frameon=False, loc='upper left')
    ax2.legend(frameon=False, loc='best')


    plt.tight_layout(rect=[0, 0.05, 1, 1]) 


    # Place subplot descriptions at the bottom of the entire figure
    fig.text(0.25, 0.02,
             '(a) The proportion of different optimization level on C++ (O3).',
             ha='center', fontsize=14)
    fig.text(0.75, 0.02,
             '(b) The proportion of different optimization level on Python.',
             ha='center', fontsize=14)
    

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
    else:
        plt.show()


def parse_args():
    parser = argparse.ArgumentParser(description="Draw the RQ2 optimization-level chart.")
    parser.add_argument(
        "--dataset-path",
        required=True,
        help="CSV with columns: dataset, method, NC, NO, NH, FH.",
    )
    parser.add_argument(
        "--output-path",
        help="Optional output image path. If omitted, display the plot interactively.",
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    dataset_path = Path(args.dataset_path).expanduser()
    if not dataset_path.is_file():
        raise FileNotFoundError(f"RQ2 histogram CSV not found: {dataset_path}")
    plot_example_chart(dataset_path, args.output_path)
