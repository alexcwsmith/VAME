#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Variational Animal Motion Embedding 0.1 Toolbox
© K. Luxem & P. Bauer, Department of Cellular Neuroscience
Leibniz Institute for Neurobiology, Magdeburg, Germany

https://github.com/LINCellularNeuroscience/VAME
Licensed under GNU General Public License v3.0

The following code is adapted from:

DeepLabCut2.0 Toolbox (deeplabcut.org)
© A. & M. Mathis Labs
https://github.com/AlexEMG/DeepLabCut
Please see AUTHORS for contributors.
https://github.com/AlexEMG/DeepLabCut/blob/master/AUTHORS
Licensed under GNU Lesser General Public License v3.0
"""

import os, yaml
from pathlib import Path
import ruamel.yaml


def create_config_template():
    """
    Creates a template for config.yaml file. This specific order is preserved while saving as yaml file.
    """
    import ruamel.yaml
    yaml_str = """\
# Project name
    Project:
    \n
# Project path and videos
    project_path:
    video_sets:
    \n
# Data
    all_data:
    \n
# Creation of train set:
    savgol_filter:
    savgol_length:
    savgol_order:
    test_fraction:
    \n
# RNN model general hyperparameter:
    num_features:
    batch_size:
    max_epochs:
    model_snapshot:
    model_convergence:
    transition_function:
    beta:
    zdims:
    learning_rate:
    step_size:
    gamma:
    time_window: 
    prediction_decoder:
    prediction_steps:
    \n
# Segmentation:
    load_data:
    snapshot:
    snapshot_epoch:
    median_filter:
    \n
# Video writer:
    lenght_of_motif_video: 
    
# ONLY CHANGE ANYTHING BELOW IF YOU ARE FAMILIAR WITH RNN MODELS
# RNN encoder hyperparamter:
    hidden_size_layer_1:
    hidden_size_layer_2:
    dropout_encoder:
    \n
# RNN reconstruction hyperparameter:
    hidden_size_rec: 
    dropout_rec:
    \n
# RNN prediction hyperparamter:
    hidden_size_pred:
    dropout_pred:
    \n
# RNN loss hyperparameter:
    mse_reconstruction_reduction: 
    mse_prediction_reduction:
    kmeans_loss:
    kmeans_lambda: 
    anneal_function:
    kl_start:
    annealtime:
    scheduler:
    # set scheduler to 0 for manual learning rate descent (decrease lr by factor of gamma after step_size epochs without new best_loss).
    """
    ruamelFile = ruamel.yaml.YAML()
    cfg_file = ruamelFile.load(yaml_str)
    return(cfg_file,ruamelFile)


def read_config(configname):
    """
    Reads structured config file
    """
    ruamelFile = ruamel.yaml.YAML()
    path = Path(configname)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                cfg = ruamelFile.load(f)
        except Exception as err:
            if err.args[2] == "could not determine a constructor for the tag '!!python/tuple'":
                with open(path, 'r') as ymlfile:
                  cfg = yaml.load(ymlfile,Loader=yaml.SafeLoader)
                  write_config(configname,cfg)
    else:
        raise FileNotFoundError ("Config file is not found. Please make sure that the file exists and/or there are no unnecessary spaces in the path of the config file!")
    return(cfg)
    
    
def write_config(configname,cfg):
    """
    Write structured config file.
    """
    with open(configname, 'w') as cf:
        ruamelFile = ruamel.yaml.YAML()
        cfg_file,ruamelFile = create_config_template()
        for key in cfg.keys():
            cfg_file[key]=cfg[key]

        ruamelFile.dump(cfg_file, cf)        
        
        
        
        
        
        
        
