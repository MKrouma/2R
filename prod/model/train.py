""" docstring
"""

# import
import os
import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.cluster import DBSCAN
from IPython.display import display

# read dataset
def load_dataset(accidents_csv) :
    """ load dataset

    Args : 
        - accidents_csv (str) : data in db/shared absolute or relative path;

    return : 
        - accidents_df (DataFrame) : dataframe of accidents in doi & coi.
    """

    # load
    accidents_df = pd.read_csv(accidents_csv, index_col=[0])

    # display
    display(accidents_df.sample(2))
    return accidents_df

def train_model(dataset:pd.DataFrame, hyperparam:dict, model_name:str = "DBSCAN") :
    """ train model

    Args :
        - dataset (DataFrame): load_dataset();
        - hyperparam (Dict) : dict of model hyperparameters
        - model_name (Str) : "DBSCAN", scale it for others cases.
    """

    # define model
    if model_name == "DBSCAN" :

        # model hyperparameters
        eps = hyperparam["eps"]
        min_samples = hyperparam["min_samples"]
        metric = hyperparam["metric"]

        # model
        db = DBSCAN(eps=eps, min_samples=min_samples, metric=metric)
        db.fit(dataset)

        # number of clusters
        n_clusters = len(np.unique(db.labels_))
        print(f"Number of clusters created : {n_clusters}")



if __name__ == "__main__" :
    # load dataset
    accidents_csv = "../../db/shared/accidents_2R_75.csv"
    accidents_df = load_dataset(accidents_csv)

    # train model
    model_name = "DBSCAN"
    hyperparam = {
        "eps" : 0.005, 
        "min_samples" : 6, 
        "metric" : "manhattan"
    }
    train_model(accidents_df, hyperparam, model_name)
    


