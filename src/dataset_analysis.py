from pathlib import Path
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CONFIGURATION
# ============================================================

# Dataset location relative to project root
DATASET_DIR = Path("rgb")

# Supported image formats
VALID_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


# ============================================================
# 2. CHECK DATASET PATH
# ============================================================

if not DATASET_DIR.exists():
    print("ERROR: Dataset directory not found!")
    print(f"Expected path: {DATASET_DIR}")
    exit()

print("=" * 70)
print("CITRUS AI FRAMEWORK")
print("DATASET ANALYSIS")
print("=" * 70)

print(f"\nDataset Path: {DATASET_DIR}")


# ============================================================
# 3. FIND CLASSES
# ============================================================

classes = sorted([
    folder.name
    for folder in DATASET_DIR.iterdir()
    if folder.is_dir()
])

print(f"\nNumber of Classes: {len(classes)}")

print("\nClasses:")

for i, class_name in enumerate(classes, start=1):
    print(f"{i}. {class_name}")


# ============================================================
# 4. SCAN ALL IMAGES
# ============================================================

records = []
corrupted_images = []

print("\n" + "=" * 70)
print("SCANNING DATASET")
print("=" * 70)

for class_name in classes:

    class_path = DATASET_DIR / class_name

    class_count = 0

    for image_path in class_path.rglob("*"):

        # Ignore non-image files
        if image_path.suffix.lower() not in VALID_EXTENSIONS:
            continue

        try:

            # Open image and verify it
            with Image.open(image_path) as img:

                width, height = img.size

                records.append({
                    "class": class_name,
                    "image_path": str(image_path),
                    "width": width,
                    "height": height,
                    "format": img.format
                })

                class_count += 1

        except Exception as error:

            corrupted_images.append({
                "path": str(image_path),
                "error": str(error)
            })

    print(f"{class_name:35} : {class_count} images")


# ============================================================
# 5. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(records)


# ============================================================
# 6. DATASET SUMMARY
# ============================================================

total_images = len(df)

print("\n" + "=" * 70)
print("DATASET SUMMARY")
print("=" * 70)

print(f"\nTotal Classes : {len(classes)}")
print(f"Total Images  : {total_images}")
print(f"Corrupted     : {len(corrupted_images)}")


# ============================================================
# 7. CLASS DISTRIBUTION
# ============================================================

class_counts = df["class"].value_counts().sort_index()

print("\n" + "=" * 70)
print("CLASS DISTRIBUTION")
print("=" * 70)

for class_name, count in class_counts.items():

    percentage = (count / total_images) * 100

    print(
        f"{class_name:35} "
        f"{count:6} images "
        f"({percentage:6.2f}%)"
    )


# ============================================================
# 8. IMAGE DIMENSION ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("IMAGE DIMENSION ANALYSIS")
print("=" * 70)

print(f"\nAverage Width  : {df['width'].mean():.2f}")
print(f"Average Height : {df['height'].mean():.2f}")

print(f"Minimum Width  : {df['width'].min()}")
print(f"Maximum Width  : {df['width'].max()}")

print(f"Minimum Height : {df['height'].min()}")
print(f"Maximum Height : {df['height'].max()}")


# ============================================================
# 9. CREATE RESULTS DIRECTORY
# ============================================================

RESULTS_DIR = Path("results")

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 10. SAVE IMAGE METADATA
# ============================================================

df.to_csv(
    RESULTS_DIR / "dataset_metadata.csv",
    index=False
)


# ============================================================
# 11. SAVE CLASS DISTRIBUTION
# ============================================================

summary_df = pd.DataFrame({
    "Class": class_counts.index,
    "Image_Count": class_counts.values
})

summary_df["Percentage"] = (
    summary_df["Image_Count"]
    / total_images
    * 100
)

summary_df.to_csv(
    RESULTS_DIR / "class_distribution.csv",
    index=False
)


# ============================================================
# 12. CLASS DISTRIBUTION GRAPH
# ============================================================

plt.figure(figsize=(14, 8))

plt.bar(
    summary_df["Class"],
    summary_df["Image_Count"]
)

plt.title(
    "Citrus Dataset Class Distribution",
    fontsize=16
)

plt.xlabel(
    "Class",
    fontsize=12
)

plt.ylabel(
    "Number of Images",
    fontsize=12
)

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "class_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 13. SAVE CORRUPTED IMAGE REPORT
# ============================================================

if corrupted_images:

    corrupted_df = pd.DataFrame(corrupted_images)

    corrupted_df.to_csv(
        RESULTS_DIR / "corrupted_images.csv",
        index=False
    )


# ============================================================
# 14. FINAL OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS COMPLETED")
print("=" * 70)

print(f"\nTotal Classes : {len(classes)}")
print(f"Total Images  : {total_images}")
print(f"Corrupted     : {len(corrupted_images)}")

print("\nGenerated files:")

print("1. results/dataset_metadata.csv")
print("2. results/class_distribution.csv")
print("3. results/class_distribution.png")

if corrupted_images:
    print("4. results/corrupted_images.csv")

print("\nDone! Dataset analysis completed successfully.")