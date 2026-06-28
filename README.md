# Gamba Vision
> **This project is for educational purpose not intended to be used in a real environment**

A real-time computer vision and probability engine designed for Blackjack. The system automatically detects and identifies playing cards, tracks the ongoing game state, and computes live win/loss probabilities by combining card counting (KO System) with optimal Blackjack basic strategy.

The initial approach for this project was to use a single computer vision model (such as RESNET50, fasterRCNNN, or YOLO8n) fine-tuned to detect and identify all 52 playing card classifications. 

However, this paper from Stanford [Blackjack Card Counting](https://cs231n.stanford.edu/2024/papers/blackjack-card-counting.pdf) showed that "separating the two components", Detection and Identification, yielded much better results. Their study used the YOLO8n as the detection and RESNET50 as the identifier. While the Stanford study paired YOLOv8n for detection with ResNet50 for identification, this project aims to extend and build upon their findings by upgrading the identification layer to a pretrained, EfficientNetV2 model.

All model training, optimization, and real-time inference testing are conducted locally on an Apple MacBook Air (M4, 16GB) using Apple Silicon hardware acceleration (mps backend in PyTorch).


## What This Project Does

This project is designed for the simulated environment created within `play_game.py` with pygame.

1. Detects every visible playing card in a video frame using a YOLOv8n object detector.
2. Classifies each detected card into one of 52 classes (rank + suit) using an EfficientNetV2 classifier.
3. Tracks game state — dealer hand, player hands, other visible hands, shoe penetration, and bet amounts — across frames.
4. Computes probabilities for the current hand using the KO (Knock-Out) card counting system combined with Blackjack basic strategy.
5. Acts on those probabilities by recommending (and optionally automating, via simulated mouse input) hit / stand / double / split decisions and bet sizing.

## Dataset

To train the vision classification model, images from the two datasets were used.
Datasets used to train the classification model
- https://www.kaggle.com/datasets/andy8744/playing-cards-object-detection-dataset/data
- https://www.kaggle.com/datasets/jaypradipshah/the-complete-playing-card-dataset

Merged the datasets into one `dataset_combined` file from the `merge_datasets.py`. As well, removed all JOKER cards found.



