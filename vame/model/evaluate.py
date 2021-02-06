#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Variational Animal Motion Embedding 0.1 Toolbox
© K. Luxem & P. Bauer, Department of Cellular Neuroscience
Leibniz Institute for Neurobiology, Magdeburg, Germany

https://github.com/LINCellularNeuroscience/VAME
Licensed under GNU General Public License v3.0
"""

import os
import torch
import numpy as np
from pathlib import Path
from matplotlib import pyplot as plt
import torch.utils.data as Data

from vame.util.auxiliary import read_config
from vame.model.rnn_vae import RNN_VAE
from vame.model.dataloader import SEQUENCE_DATASET
    

def plot_reconstruction(filepath, test_loader, seq_len_half, model, model_name, 
                        FUTURE_DECODER, FUTURE_STEPS, suffix=None):
    x = test_loader.__iter__().next()
    x = x.permute(0,2,1)
    data = x[:,:seq_len_half,:].type('torch.FloatTensor').cuda()
    data_fut = x[:,seq_len_half:seq_len_half+FUTURE_STEPS,:].type('torch.FloatTensor').cuda()
    if FUTURE_DECODER:
        x_tilde, future, latent, mu, logvar = model(data)
        
        fut_orig = data_fut.cpu()
        fut_orig = fut_orig.data.numpy()
        fut = future.cpu()
        fut = fut.detach().numpy()
    
    else:
        x_tilde, latent, mu, logvar = model(data)

    data_orig = data.cpu()
    data_orig = data_orig.data.numpy()
    data_tilde = x_tilde.cpu()
    data_tilde = data_tilde.detach().numpy()
    
    if FUTURE_DECODER:
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.suptitle('Reconstruction and future prediction of input sequence')
        ax1.plot(data_orig[1,...], color='k', label='Sequence Data')
        ax1.plot(data_tilde[1,...], color='r', linestyle='dashed', label='Sequence Reconstruction')
        ax2.plot(fut_orig[1,...], color='k')
        ax2.plot(fut[1,...], color='r', linestyle='dashed')
        if suffix:
            fig.savefig(filepath+'evaluate/'+'Future_Reconstruction' + model_name + '_' + suffix + '.png') 
        elif not suffix:
            fig.savefig(filepath+'evaluate/'+'Future_Reconstruction' + model_name + '.png') 

    else:
        fig, ax1 = plt.subplots(1, 1)
        fig.suptitle('Reconstruction of input sequence')
        ax1.plot(data_orig[1,...], color='k', label='Sequence Data')
        ax1.plot(data_tilde[1,...], color='r', linestyle='dashed', label='Sequence Reconstruction') 

        fig.savefig(filepath+'evaluate/'+'Reconstruction_'+model_name+'.png')
    
    
def plot_loss(cfg, filepath, model_name):
    train_loss = np.load(cfg['project_path']+'/'+'model/model_losses'+'/train_losses_'+model_name+'.npy')
    test_loss = np.load(cfg['project_path']+'/'+'model/model_losses'+'/test_losses_'+model_name+'.npy')
    mse_loss_train = np.load(cfg['project_path']+'/'+'model/model_losses'+'/mse_train_losses_'+model_name+'.npy')
    mse_loss_test = np.load(cfg['project_path']+'/'+'model/model_losses'+'/mse_test_losses_'+model_name+'.npy')
    km_loss = np.load(cfg['project_path']+'/'+'model/model_losses'+'/kmeans_losses_'+model_name+'.npy', allow_pickle=True)
    kl_loss = np.load(cfg['project_path']+'/'+'model/model_losses'+'/kl_losses_'+model_name+'.npy')
    fut_loss = np.load(cfg['project_path']+'/'+'model/model_losses'+'/fut_losses_'+model_name+'.npy')
    
    km_losses = []
    for i in range(len(km_loss)):
        km = km_loss[i].cpu().detach().numpy()
        km_losses.append(km)
    
    fig, (ax1) = plt.subplots(1, 1)
    fig.suptitle('Losses of our Model')
    ax1.set(xlabel='Epochs', ylabel='loss [log-scale]')
    ax1.set_yscale("log")
    ax1.plot(train_loss, label='Train-Loss')
    ax1.plot(test_loss, label='Test-Loss')
    ax1.plot(mse_loss_train, label='MSE-Train-Loss')
    ax1.plot(mse_loss_test, label='MSE-Test-Loss')
    ax1.plot(km_losses, label='KMeans-Loss')
    ax1.plot(kl_loss, label='KL-Loss')
    ax1.plot(fut_loss, label='Prediction-Loss')
    ax1.legend(loc='lower left')
    fig.savefig(filepath+'evaluate/'+'MSE-and-KL-Loss'+model_name+'.png')
    
    
def eval_temporal(cfg, use_gpu, model_name, suffix=None):
    
    SEED = 19
    ZDIMS = cfg['zdims']
    FUTURE_DECODER = cfg['prediction_decoder']
    TEMPORAL_WINDOW = cfg['time_window']*2
    FUTURE_STEPS = cfg['prediction_steps']
    NUM_FEATURES = cfg['num_features']
    TEST_BATCH_SIZE = 64
    PROJECT_PATH = cfg['project_path']
    hidden_size_layer_1 = cfg['hidden_size_layer_1']
    hidden_size_layer_2 = cfg['hidden_size_layer_2']
    hidden_size_rec = cfg['hidden_size_rec']
    hidden_size_pred = cfg['hidden_size_pred']
    dropout_encoder = cfg['dropout_encoder']
    dropout_rec = cfg['dropout_rec']
    dropout_pred = cfg['dropout_pred']
    
    filepath = PROJECT_PATH+'model/'

    seq_len_half = int(TEMPORAL_WINDOW/2)
    if use_gpu:
        torch.cuda.manual_seed(SEED)
        model = RNN_VAE(TEMPORAL_WINDOW,ZDIMS,NUM_FEATURES,FUTURE_DECODER,FUTURE_STEPS, hidden_size_layer_1, 
                        hidden_size_layer_2, hidden_size_rec, hidden_size_pred, dropout_encoder, 
                        dropout_rec, dropout_pred).cuda()
    else:
        model = RNN_VAE(TEMPORAL_WINDOW,ZDIMS,NUM_FEATURES,FUTURE_DECODER,FUTURE_STEPS)
        
    model.load_state_dict(torch.load(cfg['project_path']+'/'+'model/best_model/'+model_name+'_'+cfg['Project']+'.pkl'))
    model.eval() #toggle evaluation mode
    
    testset = SEQUENCE_DATASET(cfg['project_path']+'data/train/', data='test_seq.npy', train=False, temporal_window=TEMPORAL_WINDOW)
    test_loader = Data.DataLoader(testset, batch_size=TEST_BATCH_SIZE, shuffle=True, drop_last=True)    
     
    plot_reconstruction(filepath, test_loader, seq_len_half, model, model_name, FUTURE_DECODER, FUTURE_STEPS, suffix=suffix)
    plot_loss(cfg, filepath, model_name)
     
    
    
def evaluate_model(config, model_name, suffix=None):
    """
        Evaluation of testset
    """
    config_file = Path(config).resolve()
    cfg = read_config(config_file)
    
    if not os.path.exists(cfg['project_path']+'model/evaluate/'):
        os.mkdir(cfg['project_path']+'/'+'model/evaluate/')
            
    use_gpu = torch.cuda.is_available()
    if use_gpu:
        print("Using CUDA")
        print('GPU active:',torch.cuda.is_available())
        print('GPU used:',torch.cuda.get_device_name(0)) 
    else:
        print("CUDA is not working!")
      
    print("\n\nEvaluation of %s model. \n" %model_name)   
    eval_temporal(cfg, use_gpu, model_name, suffix=suffix)

    print("You can find the results of the evaluation in '/Your-VAME-Project-Apr30-2020/model/evaluate/' \n"
          "OPTIONS:\n" 
          "- vame.behavior_segmentation() to identify behavioral motifs.\n"
          "- re-run the model for further fine tuning. Check again with vame.evaluate_model()")
    
    
    
    
    
