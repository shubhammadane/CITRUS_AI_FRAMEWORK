from pathlib import Path
from PIL import Image
import hashlib
import csv
from collections import defaultdict

# ============================================================
# CitrusAI-X - Exact Duplicate Image Detection
# ============================================================

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset path
DATASET_PATH = PROJECT_ROOT / "rgb"

# Results directory
RESULTS_PATH = PROJECT_ROOT / "results"
RESULTS_PATH.mkdir(exist_ok=True)

# Output files
REPORT_FILE = RESULTS_PATH / "duplicate_report.csv"
SUMMARY_FILE = RESULTS_PATH / "duplicate_summary.txt"

# Supported image formats
IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".webp"
}


# ============================================================
# Calculate SHA-256 Hash
# ============================================================

def calculate_hash(image_path):
    """
    Calculate SHA-256 hash of the image file.

    Exact duplicate files will normally have the same hash.
    """

    sha256 = hashlib.sha256()

    try:
        with open(image_path, "rb") as file:

            while True:
                data = file.read(1024 * 1024)

                if not data:
                    break

                sha256.update(data)

        return sha256.hexdigest()

    except Exception as error:

        print(f"ERROR reading: {image_path}")
        print(error)

        return None


# ============================================================
# Validate Image
# ============================================================

def validate_image(image_path):
    """
    Check whether the image can be opened successfully.
    """

    try:

        with Image.open(image_path) as image:
            image.verify()

        return True

    except Exception:

        return False


# ============================================================
# Find All Images
# ============================================================

def get_all_images():

    image_files = []

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
# Duplicate Detection
# ============================================================

def detect_duplicates():

    print("=" * 75)
    print("CITRUSAI-X - EXACT DUPLICATE IMAGE DETECTION")
    print("=" * 75)

    print(f"\nDataset Path:")
    print(DATASET_PATH)

    if not DATASET_PATH.exists():

        print("\nERROR: Dataset path does not exist.")

        return

    # --------------------------------------------------------
    # Get images
    # --------------------------------------------------------

    image_files = get_all_images()

    total_images = len(image_files)

    print(f"\nTotal Images Found : {total_images}")

    if total_images == 0:

        print("No images found.")

        return

    print("\nCalculating image hashes...")
    print("Please wait...\n")

    # --------------------------------------------------------
    # Store hash -> image paths
    # --------------------------------------------------------

    hash_groups = defaultdict(list)

    corrupted_images = []

    # --------------------------------------------------------
    # Process images
    # --------------------------------------------------------

    for index, image_path in enumerate(image_files, start=1):

        # Validate image
        if not validate_image(image_path):

            corrupted_images.append(image_path)

            print(
                f"[CORRUPTED] {image_path}"
            )

            continue

        # Calculate hash
        image_hash = calculate_hash(image_path)

        if image_hash is not None:

            hash_groups[image_hash].append(image_path)

        # Progress
        if index % 500 == 0 or index == total_images:

            print(
                f"Processed: {index}/{total_images}"
            )

    # --------------------------------------------------------
    # Find duplicate groups
    # --------------------------------------------------------

    duplicate_groups = {
        image_hash: paths
        for image_hash, paths in hash_groups.items()
        if len(paths) > 1
    }

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    unique_hashes = len(hash_groups)

    duplicate_group_count = len(duplicate_groups)

    duplicate_image_count = sum(
        len(paths)
        for paths in duplicate_groups.values()
    )

    duplicate_extra_count = sum(
        len(paths) - 1
        for paths in duplicate_groups.values()
    )

    unique_images = total_images - duplicate_extra_count

    # --------------------------------------------------------
    # Print Results
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("DUPLICATE DETECTION RESULTS")
    print("=" * 75)

    print(f"\nTotal Images           : {total_images}")

    print(f"Unique Image Files     : {unique_images}")

    print(f"Duplicate Groups       : {duplicate_group_count}")

    print(f"Duplicate Image Files  : {duplicate_image_count}")

    print(f"Extra Duplicate Files  : {duplicate_extra_count}")

    print(f"Corrupted Images       : {len(corrupted_images)}")

    # --------------------------------------------------------
    # Duplicate Percentage
    # --------------------------------------------------------

    if total_images > 0:

        duplicate_percentage = (
            duplicate_extra_count / total_images
        ) * 100

    else:

        duplicate_percentage = 0

    print(
        f"Duplicate Percentage   : "
        f"{duplicate_percentage:.2f}%"
    )

    # --------------------------------------------------------
    # Save CSV Report
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
                "Duplicate_Group",
                "SHA256_Hash",
                "Class",
                "Image_Path"
            ]
        )

        group_number = 1

        for image_hash, paths in sorted(
            duplicate_groups.items()
        ):

            for image_path in paths:

                class_name = image_path.parent.name

                writer.writerow(
                    [
                        group_number,
                        image_hash,
                        class_name,
                        str(image_path)
                    ]
                )

            group_number += 1

    # --------------------------------------------------------
    # Save Summary
    # --------------------------------------------------------

    with open(
        SUMMARY_FILE,
        "w",
        encoding="utf-8"
    ) as summary_file:

        summary_file.write(
            "CITRUSAI-X - EXACT DUPLICATE DETECTION REPORT\n"
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
            f"Unique Images      : {unique_images}\n"
        )

        summary_file.write(
            f"Duplicate Groups   : {duplicate_group_count}\n"
        )

        summary_file.write(
            f"Duplicate Files    : {duplicate_image_count}\n"
        )

        summary_file.write(
            f"Extra Duplicates   : {duplicate_extra_count}\n"
        )

        summary_file.write(
            f"Corrupted Images   : {len(corrupted_images)}\n"
        )

        summary_file.write(
            f"Duplicate Percent  : "
            f"{duplicate_percentage:.2f}%\n"
        )

        summary_file.write("\n")

        # ----------------------------------------------------
        # Duplicate Groups
        # ----------------------------------------------------

        if duplicate_groups:

            summary_file.write(
                "DUPLICATE GROUPS\n"
            )

            summary_file.write(
                "-" * 60 + "\n\n"
            )

            group_number = 1

            for image_hash, paths in sorted(
                duplicate_groups.items()
            ):

                summary_file.write(
                    f"Group {group_number}\n"
                )

                summary_file.write(
                    f"SHA256: {image_hash}\n"
                )

                for image_path in paths:

                    summary_file.write(
                        f"  {image_path}\n"
                    )

                summary_file.write("\n")

                group_number += 1

        else:

            summary_file.write(
                "No exact duplicate images found.\n"
            )

    # --------------------------------------------------------
    # Final Message
    # --------------------------------------------------------

    print("\n")
    print("=" * 75)
    print("DUPLICATE DETECTION COMPLETED")
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
    print("Inspect duplicate groups before making any dataset changes.")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    detect_duplicates()