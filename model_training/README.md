# Model Training of Cat Dog Classification System

In this file, I will introduce how to train or import deep neural nework model to classify the breed of cat or dog from users' image uploaded.

There are two steps:
1. Object detection model import

2. Cats classifier and dog classifier trianing

Hyperparameters for cat-breed-classification training:

| Hyperparameters	      | Value |
| --------------------- | ----- |
| Epochs	              | 5     |
| Fine-Tune Ratio	      | 0.15  |
| Fine-Tune Epochs      |	5     |
| Optimizer	            | Adam  |
| Initial Learning Rate	| 0.001 |
| Learning Rate Decay	  | Step  |
| Batch Size	          | 32    |

Hyperparameters for dog-breed-classification training:

| Hyperparameters	      | Value                 |
| --------------------- | --------------------- |
| Epochs	              | 10                    |
| Fine-Tune Ratio	      | None                  |
| Fine-Tune Epochs      |	0                     |
| Optimizer	            | Adam                  |
| Initial Learning Rate	| 0.001                 |
| Learning Rate Decay	  | ReduceLROnPlateau API |
| Batch Size	          | 32                    |
