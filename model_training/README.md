# Model Training of Cat Dog Classifier

Training steps for cats-dogs classifier using Elastic Weight Consolidation (EWC) techniques are following:

**Dataset Preparation**

The dataset I use is from [Oxford on kaggle](https://www.kaggle.com/datasets/zippyz/cats-and-dogs-breeds-classification-oxford-dataset/code), and process images with resizing, normalization, and augmentation before creating batch data. However, the class model can predict is only three for each species (cat and dog), I will be continuous to improve the classifier in the future.

| Cats	     | Dogs                      |
| ---------- | ------------------------- |
| Abyssinian | american bulldog          |
| Bengal     | american pit bull terrier |
| Birman     | basset hound              |

**Model Training**

1. Before image preprocesing, I use a pre-train object detector with MoboileNet as backbbone from [kaggle models](https://tfhub.dev/google/openimages_v4/ssd/mobilenet_v2/1) to crop each image to reduce the additional influence of background.
2. Rezie, normalize, and apply augmentation to each image, the training and validation data is `8:2` for cats data splitting, `9:1` for dogs data splitting, testing data is crawled from internet.
3. Build a pre-train model (as known `tranfer learning`) named `MobileNet` with several `Dense` layers with `L2 regularization` and `Dropout layers`, the parameters of pre-train model are feeezed.
4. Train model on cats dataset first as `cats classifier`.
5. Train the cats classifier on the second dogs dataset and apply Elastic Weight Consolidation (EWC) technique to retain the important parameters for cat-breed classification.
6. Save model.

Hyperparameters for cat-breed-classification training:

| Hyperparameters	      | Value |
| --------------------- | ----- |
| Epochs	              | 10    |
| Stop Epochs	          | 3     |
| Optimizer	            | Adam  |
| Initial Learning Rate	| 0.01  |
| Learning Rate Decay	  | Step  |
| Batch Size	          | 16    |

Hyperparameters for dog-breed-classification training:

| Hyperparameters	      | Value                 |
| --------------------- | --------------------- |
| Epochs	              | 10                    |
| Stop Epochs	          | 2                     |
| Optimizer	            | Adam                  |
| Initial Learning Rate	| 5e-3                  |
| Learning Rate Decay	  | cosine_annealing      |
| warmup_iters          | 4                     |
| alpha                 | 0.5                   |
| factor                | 2                     |
| Batch Size	          | 16                    |

**Results**

Here are the training curves for both:

<div>
  <img src="https://github.com/Leohoji/dog-cat-breed-classification-system/blob/main/README_Images/results.png?raw=true" alt="Results" style="width: 800px; height: 800px;"/>
</div>

Final accuracy
| Cats Testing Data	    | Dogs Testing Data	    |
| --------------------- | --------------------- |
| 0.8221	              | 0.9100                |

---  

### Elastic Weight Consolidation (EWC)  

EWC is a technique designed to address **catastrophic forgetting**, enabling neural networks to retain knowledge from previous tasks while learning new ones. Inspired by neuroscience, it mimics **synaptic consolidation**, where important parameters are selectively preserved. The **Fisher Information Matrix** is used to estimate the importance of each weight, and a quadratic penalty term is added to the loss function to prevent significant changes to crucial parameters. This allows for **continual learning** without overwriting past knowledge.  

📌 **Formula:**  
$L(\theta) = L_B(\theta) + \sum_{i} \frac{\lambda}{2} F_i (\theta_i - \theta_{A,i}^*)^2$

🔗 **References**  
📄 [Paper](https://arxiv.org/pdf/1612.00796) | 📖 [Mathematical Proof](https://blog.csdn.net/dhaiuda/article/details/103967676)
