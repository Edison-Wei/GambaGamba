import os
import shutil
from pathlib import Path

ROOT = Path("dataset_combined")
DATASET_CONTENT = """path: dataset_combined

train: images/train
val: images/val
test: images/test

nc: 52

names:
  [
    '10c','10d','10h','10s',
    '2c','2d','2h','2s',
    '3c','3d','3h','3s',
    '4c','4d','4h','4s',
    '5c','5d','5h','5s',
    '6c','6d','6h','6s',
    '7c','7d','7h','7s',
    '8c','8d','8h','8s',
    '9c','9d','9h','9s',
    'Ac','Ad','Ah','As',
    'Jc','Jd','Jh','Js',
    'Kc','Kd','Kh','Ks',
    'Qc','Qd','Qh','Qs'
  ]
"""

def merge_datasets(force = False):
    dataset_combined = Path(ROOT)
    if dataset_combined.exists() or not force:
        return
    
    print("Merging Real and Simulated Dataset")

    for split in ["train", "val", "test"]:
        (ROOT / "images" / split).mkdir(parents=True, exist_ok=True)
        (ROOT / "labels" / split).mkdir(parents=True, exist_ok=True)

    sim_map = {
        "train": "train",
        "valid": "val",
        "test": "test"
    }

    for src_split, dst_split in sim_map.items():

        # img_dir = Path("archive") / src_split / "images"
        # lbl_dir = Path("archive") / src_split / "labels"
        img_dir = Path(f"archive/{src_split}/images")
        lbl_dir = Path(f"archive/{src_split}/labels")

        for img_file in img_dir.glob("*.jpg"):

            shutil.copy(
                img_file,
                ROOT / "images" / dst_split / f"sim_{img_file.name}"
            )

            label_file = lbl_dir / (img_file.stem + ".txt")

            if label_file.exists():

                shutil.copy(
                    label_file,
                    ROOT / "labels" / dst_split / f"sim_{label_file.name}"
                )

    img_dir = Path("dataset_real/Images/Images")
    lbl_dir = Path("dataset_real/YOLO_Annotations/YOLO_Annotations")

    all_images = sorted(list(img_dir.glob("*.jpg")))

    # Place all the real playing card dataset into test
    for img_file in all_images:
        shutil.copy(
            img_file,
            ROOT / "images" / "test" / f"real_{img_file.name}"
        )

        label_file = lbl_dir / (img_file.stem + ".txt")

        if label_file.exists():

            shutil.copy(
                label_file,
                ROOT / "labels" / "test" / f"real_{label_file.name}"
            )

    ## Uncomment the following to have a split dataset
    # n = len(all_images)
    # train_end = int(0.8 * n)
    # val_end = int(0.9 * n)

    # splits = {
    #     "train": all_images[:train_end],
    #     "val": all_images[train_end:val_end],
    #     "test": all_images[val_end:]
    # }

    # for split, images in splits.items():

    #     for img_file in images:

    #         shutil.copy(
    #             img_file,
    #             ROOT / "images" / split / f"real_{img_file.name}"
    #         )

    #         label_file = lbl_dir / (img_file.stem + ".txt")

    #         if label_file.exists():

    #             shutil.copy(
    #                 label_file,
    #                 ROOT / "labels" / split / f"real_{label_file.name}"
    #             )

    print("Dataset merged successfully.")

    print("Remove Joker Images and Labels")

    label_root = Path("dataset_combined/labels")

    for txt in label_root.rglob("*.txt"):

        lines_out = []

        with open(txt) as f:
            for line in f:

                cls = int(line.split()[0])

                if cls == 52:
                    continue

                lines_out.append(line)

        with open(txt, "w") as f:
            f.writelines(lines_out)

    dataset_combined_yaml = Path(f"{ROOT}/data.yaml")
    with open(dataset_combined_yaml, "w", encoding="utf-8") as file:
        file.write(DATASET_CONTENT)

    print("Complete Merge and Removal")

if __name__ == "__main__":
    merge_datasets()