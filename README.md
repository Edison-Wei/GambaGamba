Gamba Gamba

Dataset used:
- https://www.kaggle.com/datasets/andy8744/playing-cards-object-detection-dataset/data
    - Split train = 70%, test = 20%, valid = 10%
- https://www.kaggle.com/datasets/jaypradipshah/the-complete-playing-card-dataset


I have a dataset of playing cards with a background image. There is 20000 images contained in the dataset and they are already split like so train = 70%, test = 20%, valid = 10%. The split data are structured as so:
dataloader.py
archive
- test
- - images
- - labels
- train
- - images
- - labels
- validate
- - images
- - labels
Each label .txt file is title "999838767_jpg.rf.f7a78b555a5b739af690f68404b16452.txt" and has a structure like:
30 0.5564903846153846 0.14543269230769232 0.04447115384615385 0.09735576923076923
46 0.6586538461538461 0.17548076923076922 0.06009615384615385 0.09615384615384616
15 0.7307692307692307 0.22115384615384615 0.06971153846153846 0.08774038461538461
15 0.7920673076923077 0.6430288461538461 0.06971153846153846 0.0889423076923077
Each image .jpg file is a coloured image RGB and a 416x416, this is the file name "999838767_jpg.rf.f7a78b555a5b739af690f68404b16452.jpg"

I want to use the YoloV11 model by ultralytics, they require a 640 dimension image.

Can you write me a pytorch Datasets and Dataloader class to transform the image for training?