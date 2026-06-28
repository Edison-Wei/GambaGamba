import torch

from pathlib import Path
from ultralytics import YOLO

from merge_datasets import merge_datasets


def train():

    model = YOLO("yolov8n.pt")

    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
        print("Using CPU")

    model.to(device)

    model.train(
        data="dataset_combined/data.yaml",
        epochs=10,
        imgsz=640,
        batch=16,
        workers=4,
        cache=True,
        patience=20,
        project="runs",
        name="playing_cards_yolov8n",
    )

def evaluation():
    model = YOLO("runs/detect/train/weights/best.pt")

    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon GPU (MPS)")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
        print("Using CPU")

    model.to(device)

    metrics = model.val(
        data="dataset_combined/data.yaml",
        imgsz=640,
        batch=16,
        split="val"
    )

    print(f"mAP50: {metrics.box.map50:.4f}")
    print(f"mAP50-95: {metrics.box.map:.4f}")
    print(f"Precision: {metrics.box.mp:.4f}")
    print(f"Recall: {metrics.box.mr:.4f}")



if __name__ == "__main__":

    merge_datasets()

    train()

    evaluation()