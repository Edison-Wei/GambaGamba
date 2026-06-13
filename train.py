# import os
import torch
# import torchvision
# from torch.utils.data import Dataset, DataLoader, ConcatDataset
# from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
# from PIL import Image

from pathlib import Path
from ultralytics import YOLO

from merge_datasets import merge_datasets, ROOT

# os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# torch.set_float32_matmul_precision("high")

# class PlayingCardDataset(Dataset):
#     def __init__(self, img_dir, label_dir, transforms=None):
#         self.img_dir = img_dir
#         self.label_dir = label_dir
#         self.transforms = transforms
#         self.imgs = [img for img in os.listdir(img_dir) if img.endswith('.jpg')]

#     def __getitem__(self, idx):
#         img_name = self.imgs[idx]
#         img_path = os.path.join(self.img_dir, img_name)
        
#         # Load image
#         img = Image.open(img_path).convert("RGB")
#         W, H = img.size
        
#         # Corresponding label path
#         label_name = img_name.replace('.jpg', '.txt')
#         label_path = os.path.join(self.label_dir, label_name)
        
#         boxes = []
#         labels = []

#         if os.path.exists(label_path):
#             with open(label_path, 'r') as f:
#                 for line in f.readlines():
#                     parts = line.strip().split()
#                     if len(parts) != 5:
#                         continue
                        
#                     class_id, x_center, y_center, w, h = map(float, parts)
#                     class_id = int(class_id)
                    
#                     # Explicitly remove Jokers (Class 52)
#                     if class_id == 52:
#                         continue
                        
#                     # Convert YOLO normalized (center) to Absolute Pascal VOC (min/max)
#                     x_min = (x_center - w/2) * W
#                     y_min = (y_center - h/2) * H
#                     x_max = (x_center + w/2) * W
#                     y_max = (y_center + h/2) * H
                    
#                     boxes.append([x_min, y_min, x_max, y_max])
#                     # Shift classes by 1 because Class 0 must be the background in PyTorch
#                     labels.append(class_id + 1)

#         boxes = torch.as_tensor(boxes, dtype=torch.float32) if boxes else torch.zeros((0, 4), dtype=torch.float32)
#         labels = torch.as_tensor(labels, dtype=torch.int64) if labels else torch.zeros((0,), dtype=torch.int64)
        
#         target = {"boxes": boxes, "labels": labels}
        
#         if self.transforms:
#             img = self.transforms(img)
            
#         return img, target

#     def __len__(self):
#         return len(self.imgs)

# def get_model(num_classes):
#     model = ultralytics.YOLO("yolo8n.pt")



#     model = torchvision.models.detection.fasterrcnn_mobilenet_v3_large_fpn(weights="DEFAULT")
#     # model = torchvision.models.detection.fasterrcnn_resnet50_fpn(weights="DEFAULT")
#     in_features = model.roi_heads.box_predictor.cls_score.in_features
#     model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
#     return model

# def collate_fn(batch):
#     return tuple(zip(*batch))

# if __name__ == "__main__":
#     if torch.backends.mps.is_available():
#         device = torch.device("mps")
#         print("Using Apple Silicon GPU (MPS)")
#     elif torch.cuda.is_available():
#         device = torch.device("cuda")
#     else:
#         device = torch.device("cpu")
#         print("Using CPU")
    
#     # 52 cards + 1 background
#     num_classes = 53 
    
#     transforms = torchvision.transforms.Compose([
#         torchvision.transforms.Resize((620,620)),
#         torchvision.transforms.ToTensor(),
#     ])

#     dataset_simulated = PlayingCardDataset(
#         img_dir='archive/train/images',
#         label_dir='archive/train/labels',
#         transforms=transforms
#     )

#     dataset_real = PlayingCardDataset(
#         img_dir='dataset_real/Images/Images',
#         label_dir='dataset_real/YOLO_Annotations/YOLO_Annotations',
#         transforms=transforms
#     )

#     combined_dataset = ConcatDataset([dataset_simulated, dataset_real])

#     data_loader = DataLoader(
#         combined_dataset, 
#         batch_size=8,
#         num_workers=4,
#         persistent_workers=True,
#         shuffle=True, 
#         collate_fn=collate_fn
#     )

#     print(f"Total training images combined: {len(combined_dataset)}")
    
#     model = get_model(num_classes).to(device)
#     params = [p for p in model.parameters() if p.requires_grad]
#     optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
    
#     epochs = 10
#     for epoch in range(epochs):
#         model.train()
#         epoch_loss = 0
#         current_it = 0
#         for images, targets in data_loader:
#             images = list(image.to(device) for image in images)
#             targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            
#             loss_dict = model(images, targets)
#             losses = sum(loss for loss in loss_dict.values())
            
#             optimizer.zero_grad()
#             losses.backward()
#             optimizer.step()
            
#             epoch_loss += losses.item()
#             current_it += 1
#             if current_it % 100 == 0:
#                 print(f"Epoch {current_it}/{len(data_loader)}")
            
#         print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss/len(data_loader)}")
        
#     torch.save(model.state_dict(), "models/faster_rcnn_cards.pth")
#     print("Model saved to models/faster_rcnn_cards.pth")

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

    # merge_datasets()

    # train()

    evaluation()