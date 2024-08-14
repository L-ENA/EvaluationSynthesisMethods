# EvaluationSynthesisMethods
Code to help analysis and synthesis of evaluation reports. The colab notebook files in this repository contain the methods described in our paper (preprint): 

In our paper, we describe methods to extract data and synthesise information for 64 outcomes from 631 evaluation reports published by UNICEF. The code in this repository was used to automate part of the work.

The requirements.txt file can be used to initiate a conda environment with the necessary packages to run code locally as script or as jupyter notebook. When using colab, you can install dependencies listed in the first cell.

The notebook 'EvaluationSynthesisMethods.ipynb' contains scripts and methods (each cell can be run as a python script outside the notebook) to do the following:  
- Extract text from PDFs
- Attempt the parsing of sections using regular expressions (with varying success)
- Facilitate creation of a train/test dataset to identify sentences of classes of interest to our analysis
- Automatic language detection and translation to English due to the dataset containing non-english evaluations
- CUstom methods to transfer UNICEF's EISI database data into RIS files and SWIFT-Review batch queries

The notebook 'Paper_UNICEF_Lena_multi_class_label_trainer.ipynb' contains code to train, evaluate, downstream predict, and post-process sentences using the SPECTER transformed model. It was developed and used within Colab only.


