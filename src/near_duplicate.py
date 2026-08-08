from pathlib import Path
from PIL import Image
import imagehash
import csv
from collections import defaultdict

# ============================================================
# CitrusAI-X - Near-Duplicate Image Detection
# ============================================================

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset path
DATASET_PATH = PROJECT_ROOT / "rgb"

# Results directory
RESULTS_PATH = PROJECT_ROOT / "results"
RESULTS_PATH.mkdir(exist_ok=True)

# Output files
REPORT_FILE = RESULTS_PATH / "near_duplicate_report.csv"
SUMMARY_FILE = RESULTS_PATH / "near_duplicate_summary.txt"

# Supported image formats
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}

# ------------------------------------------------------------
# pHash threshold
# ------------------------------------------------------------
# Smaller distance = more visually similar.
#
# 0     = identical perceptual hash
# 1-5   = extremely similar
# 6-10  = potentially similar
# >10   = increasingly different
#
# We start conservatively at 5.
PHASH_THRESHOLD = 5


# ============================================================
# Get all images
# ============================================================

def get_all_images():

    image_files = []

    if not DATASET_PATH.exists():
        return image_files

    for class_directory in sorted(DATASET_PATH.iterdir()):

        if not class_directory.is_dir():
            continue

        for image_file in class_directory.rglob("*"):

            if (
                image_file.is_file()
                and image_file.suffix.lower() in IMAGE_EXTENSIONS
            ):
                image_files.append(image_file)

    return image_files


# ============================================================
# Calculate Perceptual Hash
# ============================================================

def calculate_phash(image_path):

    try:

        with Image.open(image_path) as image:

            image = image.convert("RGB")

            return imagehash.phash(image)

    except Exception as error:

        print(
            f"\nERROR processing: {image_path}"
        )

        print(error)

        return None


# ============================================================
# Main Near-Duplicate Detection
# ============================================================

def detect_near_duplicates():

    print("=" * 75)
    print("CITRUSAI-X - NEAR-DUPLICATE IMAGE DETECTION")
    print("=" * 75)

    print(f"\nDataset Path:")
    print(DATASET_PATH)

    print(f"\npHash Threshold : {PHASH_THRESHOLD}")

    if not DATASET_PATH.exists():

        print("\nERROR: Dataset path does not exist.")

        return

    # --------------------------------------------------------
    # Find images
    # --------------------------------------------------------

    image_files = get_all_images()

    total_images = len(image_files)

    print(f"\nTotal Images Found : {total_images}")

    if total_images == 0:

        print("No images found.")

        return

    # --------------------------------------------------------
    # Calculate hashes
    # --------------------------------------------------------

    print("\nCalculating perceptual hashes...")
    print("Please wait...\n")

    image_hashes = []

    failed_images = []

    for index, image_path in enumerate(
        image_files,
        start=1
    ):

        phash = calculate_phash(image_path)

        if phash is not None:

            image_hashes.append(
                (
                    image_path,
                    phash
                )
            )

        else:

            failed_images.append(image_path)

        if index % 500 == 0 or index == total_images:

            print(
                f"Processed: {index}/{total_images}"
            )

    # --------------------------------------------------------
    # Find similar image pairs
    # --------------------------------------------------------

    print("\nSearching for visually similar images...")

    near_duplicate_pairs = []

    total_hashed = len(image_hashes)

    # Compare hashes pair-by-pair.
    #
    # For 42k images this is potentially expensive,
    # but provides an accurate first research check.
    for i in range(total_hashed):

        path1, hash1 = image_hashes[i]

        for j in range(i + 1, total_hashed):

            path2, hash2 = image_hashes[j]

            distance = hash1 - hash2

            if distance <= PHASH_THRESHOLD:

                class1 = path1.parent.name
                class2 = path2.parent.name

                near_duplicate_pairs.append(
                    {
                        "image_1": str(path1),
                        "class_1": class1,
                        "image_2": str(path2),
                        "class_2": class2,
                        "hamming_distance": distance
                    }
                )

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    pair_count = len(
        near_duplicate_pairs
    )

    print("\n")
    print("=" * 75)
    print("NEAR-DUPLICATE DETECTION RESULTS")
    print("=" * 75)

    print(
        f"\nTotal Images          : {total_images}"
    )

    print(
        f"Successfully Hashed   : {total_hashed}"
    )

    print(
        f"Failed Images         : {len(failed_images)}"
    )

    print(
        f"Similar Image Pairs   : {pair_count}"
    )

    print(
        f"pHash Threshold       : {PHASH_THRESHOLD}"
    )

    # --------------------------------------------------------
    # Save CSV
    # --------------------------------------------------------

    with open(
        REPORT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.writer(csv_file)

        writer.writerow(
            [
                "Image_1",
                "Class_1",
                "Image_2",
                "Class_2",
                "Hamming_Distance"
            ]
        )

        for pair in near_duplicate_pairs:

            writer.writerow(
                [
                    pair["image_1"],
                    pair["class_1"],
                    pair["image_2"],
                    pair["class_2"],
                    pair["hamming_distance"]
                ]
            )

    # --------------------------------------------------------
    # Save Summary
    # --------------------------------------------------------

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as summary_file:

        summary_file.write(
            "CITRUSAI-X - NEAR-DUPLICATE DETECTION REPORT\n"
        )

        summary_file.write(
            "=" * 60 + "\n\n"
        )

        summary_file.write(
            f"Dataset Path       : {DATASET_PATH}\n"
        )

        summary_file.write(
            f"Total Images       : {total_images}\n"
        )

        summary_file.write(
            f"Successfully Hashed: {total_hashed}\n"
        )

        summary_file.write(
            f"Failed Images      : {len(failed_images)}\n"
        )

        summary_file.write(
            f"pHash Threshold    : {PHASH_THRESHOLD}\n"
        )

        summary_file.write(
            f"Similar Pairs      : {pair_count}\n"
        )

        summary_file.write("\n")

        # ----------------------------------------------------
        # Similar pairs
        # ----------------------------------------------------

        if near_duplicate_pairs:

            summary_file.write(
                "NEAR-DUPLICATE PAIRS\n"
            )

            summary_file.write(
                "-" * 60 + "\n\n"
            )

            for number, pair in enumerate(
                near_duplicate_pairs,
                start=1
            ):

                summary_file.write(
                    f"Pair {number}\n"
                )

                summary_file.write(
                    f"Image 1 : {pair['image_1']}\n"
                )

                summary_file.write(
                    f"Class 1 : {pair['class_1']}\n"
                )

                summary_file.write(
                    f"Image 2 : {pair['image_2']}\n"
                )

                summary_file.write(
                    f"Class 2 : {pair['class_2']}\n"
                )

                summary_file.write(
                    f"Hamming Distance : "
                    f"{pair['hamming_distance']}\n"
                )

                summary_file.write("\n")

        else:

            summary_file.write(
                "No near-duplicate pairs detected "
                "using the selected threshold.\n"
            )

    # --------------------------------------------------------
    # Final message
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("NEAR-DUPLICATE DETECTION COMPLETED")
    print("=" * 75)

    print("\nReports saved:")

    print(
        f"CSV     : {REPORT_FILE}"
    )

    print(
        f"Summary : {SUMMARY_FILE}"
    )

    print("\nIMPORTANT:")
    print("No images were deleted or modified.")

    print("\nNext step:")
    print("Inspect the reported similar image pairs manually.")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    detect_near_duplicates()