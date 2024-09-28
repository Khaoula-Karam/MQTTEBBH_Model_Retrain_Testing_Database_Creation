# MQTTEBBH Model Retrain, Testing, and Database Creation

**Presented for the Award of the Degree of:**
- **Master in Big Data and Cloud Computing**

**Title:**
- _Towards Predictive Analytics Algorithms for Attack Prediction in IoT Platforms_

**Author:**
- Karam Khaoula (karamkhaoula.officiel@gmail.com)

**Supervision and Contribution:**
- Prof. N. Rafalia, Faculty of Science, Kenitra (Advisor)
- Abderrahmane Aqachtoul (abderrahmanaqachtoul@gmail.com)
- Prof. M. Bakhouya, International University of Rabat (Internship Advisor)


---

## Download the `rockyou.txt` File

The file `rockyou.txt` is a common password list used for testing purposes. Due to its size, it is not included in this repository.

You can download the `rockyou.txt` file from the Kaggle dataset:

- [Common Password List - rockyou.txt](https://www.kaggle.com/datasets/wjburns/common-password-list-rockyoutxt)

Once you have downloaded the file, place it in the root folder of this repository to use it with the provided scripts and notebooks.

---

## Project Overview

This repository forms an integral part of the work presented for the **Master's Degree in Big Data and Cloud Computing** at the International University of Rabat. It contributes to the research and development outlined in the thesis titled "_Towards Predictive Analytics Algorithms for Attack Prediction in IoT Platforms_."

The project focuses on:
1. Retraining machine learning (ML) and deep learning (DL) models for IoT attack prediction.
2. Evaluating the models’ performance in predicting attacks in MQTT-based IoT environments.
3. Creating a structured database to support further research and development of attack prediction systems.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Repository Contents](#repository-contents)
- [Key Steps and Workflows](#key-steps-and-workflows)
  - [1. Data Preparation](#1-data-preparation)
  - [2. Model Retraining](#2-model-retraining)
  - [3. Testing Capabilities](#3-testing-capabilities)
  - [4. Database Creation](#4-database-creation)
- [How to Use this Repository](#how-to-use-this-repository)
- [Installation and Setup](#installation-and-setup)
- [Acknowledgments](#acknowledgments)

---

## Repository Contents

- **`.ipynb` files**: Notebooks containing the retraining, testing, and evaluation of models.
- **`.csv` files**: Datasets used for model training and evaluation.
- **Python Scripts**: Code for creating databases, capturing data, and running ML/DL model tests.

---

## Key Steps and Workflows

### 1. Data Preparation
This project involves preparing and structuring data from IoT environments, particularly MQTT data. The data is captured and labeled to ensure that the models can accurately learn and improve over time.

Key files related to this step:
- `combined_captured_data.csv`: Contains the raw data captured from IoT environments.
- `combined_script_attacks.py`: Scripts used for performing attacks and capturing data.

### 2. Model Retraining
We retrain existing ML and DL models to enhance their prediction accuracy. The retraining process involves using a combination of the captured data and existing models (e.g., LightGBM, KNN, etc.).

Key files related to this step:
- `Re-train best_lgb.ipynb`: Notebook that handles the retraining of the LightGBM model using the updated dataset.
- `Create_new_data_combined.ipynb`: A notebook used to combine new data with the existing data for model retraining.

### 3. Testing Capabilities
After retraining, we thoroughly test the models to evaluate their performance. Various metrics such as accuracy, precision, recall, and F1-score are used to determine how well the models perform in different attack scenarios.

Key files related to this step:
- `Test_capabilities.ipynb`: A notebook for testing the retrained models on various datasets and attack scenarios.

### 4. Database Creation
This part of the project focuses on organizing and storing the captured data and model outputs into a structured database. This database will serve as a foundation for future analyses and comparisons of different models and configurations.

Key files related to this step:
- `combined_captured_data_MQTT_final.csv`: The final dataset combining different sources of captured data for training and validation.

---

## How to Use this Repository

### Clone the Repository:
```bash
git clone https://github.com/Khaoula-Karam/MQTTEBBH_Model_Retrain_Testing_Database_Creation.git
cd MQTTEBBH_Model_Retrain_Testing_Database_Creation
