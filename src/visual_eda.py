from pathlib import Path
from PIL import Image
import matplotlib.pyplot as plt
import random

# ============================================================
# CitrusAI-X - Visual Exploratory Data Analysis
# ============================================================

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset path
DATASET_PATH = PROJECT_ROOT / "rgb"

# Results directory
RESULTS_PATH = PROJECT_ROOT / "results"
RESULTS_PATH.mkdir(exist_ok=True)

# Number of sample images per class
SAMPLES_PER_CLASS = 5

# Supported image extensions
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

# Reproducible random selection
random.seed(42)


def get_image_files(class_path):
    """
    Return all supported image files from a class directory.
    """
    return [
        file
        for file in class_path.iterdir()
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS
    ]


def create_visual_eda():
    """
    Create a visual grid containing sample images
    from all dataset classes.
    """

    if not DATASET_PATH.exists():
        print("ERROR: Dataset path not found!")
        print(f"Expected path: {DATASET_PATH}")
        return

    # Get class directories
    class_directories = sorted(
        [
            directory
            for directory in DATASET_PATH.iterdir()
            if directory.is_dir()
        ]
    )

    if not class_directories:
        print("ERROR: No class directories found!")
        return

    print("=" * 70)
    print("CITRUSAI-X - VISUAL EXPLORATORY DATA ANALYSIS")
    print("=" * 70)

    print(f"\nDataset Path : {DATASET_PATH}")
    print(f"Number of Classes : {len(class_directories)}")

    # --------------------------------------------------------
    # Create figure
    # --------------------------------------------------------

    rows = len(class_directories)
    columns = SAMPLES_PER_CLASS

    fig, axes = plt.subplots(
        rows,
        columns,
        figsize=(18, rows * 3.2)
    )

    # Handle case of one row
    if rows == 1:
        axes = [axes]

    # --------------------------------------------------------
    # Process every class
    # --------------------------------------------------------

    for row, class_directory in enumerate(class_directories):

        class_name = class_directory.name

        image_files = get_image_files(class_directory)

        print(f"\n{class_name}")
        print(f"Total images : {len(image_files)}")

        if len(image_files) == 0:
            print("WARNING: No images found.")

            for column in range(columns):
                axes[row][column].axis("off")

            continue

        # Select random samples
        number_of_samples = min(
            SAMPLES_PER_CLASS,
            len(image_files)
        )

        selected_images = random.sample(
            image_files,
            number_of_samples
        )

        # ----------------------------------------------------
        # Display selected images
        # ----------------------------------------------------

        for column in range(columns):

            ax = axes[row][column]
            ax.axis("off")

            if column >= len(selected_images):
                continue

            image_path = selected_images[column]

            try:
                image = Image.open(image_path).convert("RGB")

                ax.imshow(image)

                ax.set_title(
                    f"{class_name}\n{image_path.name}",
                    fontsize=8
                )

            except Exception as error:

                ax.text(
                    0.5,
                    0.5,
                    "Image Error",
                    ha="center",
                    va="center"
                )

                print(
                    f"Could not open {image_path}: {error}"
                )

    # --------------------------------------------------------
    # Figure title
    # --------------------------------------------------------

    fig.suptitle(
        "CitrusAI-X - Visual Exploratory Data Analysis\n"
        "Sample Images from All Citrus Classes",
        fontsize=18,
        fontweight="bold"
    )

    plt.tight_layout(
        rect=[0, 0, 1, 0.97]
    )

    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    output_file = RESULTS_PATH / "visual_eda_samples.png"

    plt.savefig(
        output_file,
        dpi=200,
        bbox_inches="tight"
    )

    plt.show()

    print("\n" + "=" * 70)
    print("VISUAL EDA COMPLETED")
    print("=" * 70)

    print(f"\nOutput saved to:")
    print(output_file)

    print("\nNext analysis:")
    print("1. Check image quality")
    print("2. Check background variation")
    print("3. Check lighting variation")
    print("4. Check disease symptom visibility")
    print("5. Check possible duplicate images")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    create_visual_eda()