import math
import sys
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data

from torch.autograd import Variable

class RBM():
  def __init__(self, nv, nh, w: torch.tensor = None):
    # self.nv = nv
    # self.nh = nh
    self.w = torch.randn(nh, nv)
    self.vk = None # visible nodes after K iterations (you need to train the model first)

    # TODO: check if this is correct
    if w is not None:
      self.w[:w.size()[0], :w.size()[1]] = w

    # biases
    # P(h|v)
    self.a = torch.randn(1, nh)

    # P(v|h)
    self.b = torch.randn(1, nv)

  # A sample of probability of activiation nodes H knowing the node V
  def sample_h(self, x):
    # product between [self.h_bias] and [self.w].
    # The transpose is to make them compatible
    wx = torch.mm(x, self.w.t())

    # expand_as is useful to fit the dimension of
    # tensors in order to be able to perform tensor
    # operations
    activation = wx + self.a.expand_as(wx)

    # P(h | v), If h fits the requiriments of v, then the probability
    # of activation should be high
    p_h_given_v = torch.sigmoid(activation) # now this is actually the probability

    # Returns as many probabilitys as hidden nodes I have.
    # the second return is a probablity distribution, I don't know why
    # so if later I figure out why I need it I will update this commentary
    return p_h_given_v, torch.bernoulli(p_h_given_v)

    # A sample of probability of activiation nodes V knowing the node H
  def sample_v(self, y):
    # product between [self.v_bias] and [self.w].
    # The transpose is to make them compatible but here is not necessary
    # since tensors are compatible
    wy = torch.mm(y, self.w)

    # expand_as is useful to fit the dimension of
    # tensors in order to be able to perform tensor
    # operations
    activation = wy + self.b.expand_as(wy)

    # P(h | v), If h fits the requiriments of v, then the probability
    # of activation should be high
    p_v_given_h = torch.sigmoid(activation) # now this is actually the probability

    # Returns as many probabilitys as hidden nodes I have.
    # the second return is a probablity distribution, I don't know why
    # so if later I figure out why I need it I will update this commentary
    return p_v_given_h, torch.bernoulli(p_v_given_h)

  # v0 is visible nodes tensor with original ponderation... wait, WTF!!! yeah, yeah, 
  # I know, let me explain it. You have a list of all the value of visible nodes, right?
  # Well, that tensor is v0. Now, what a hell is vk? As you know you'll train your model
  # for k epochs, and vk is the state of v0 after k epochs. Now, ph0 is P(h|v0), that's
  # the original probability of every single visible node in v0, and as you could guess,
  # phk is p(h | vk).
  def train(self, v0, vk, ph0, phk):
    self.w += (torch.mm(v0.t(), ph0) - torch.mm(vk.t(), phk)).t()
    self.b += torch.sum((v0 - vk), 0) # WTF!!! Diosito ya llevame :(
    self.a += torch.sum((ph0 - phk), 0)

  def predict(self, time: torch.Tensor):
    ''' 
    Predicts the list of words that balance the system for the [time]
    selected record in the training dataset
    '''
    assert self.vk is not None
    vk = time.reshape([1, torch.tensor(time.size()).item()])
    _,hk = self.sample_h(vk)
    _,vk = self.sample_v(hk)

    return vk


  def fit(self, epochs, data: torch.Tensor):
    '''
    Trains an energy based model in order to recommend words. You need to know that
    visible nodes correspond to words and hidden ones are no dependent on any parameter
    of the dataset, it's just like the question about "how many hidden layers should my
    artificial deep neural network have?", so it depends on how much abstraction do you 
    want in your model, looking for a balance between performance and accuracy
    '''
    rows = 12 * 31 * 24

    for epoch in range(epochs):
        training_loss = 0
        mse_loss = 0
        s = 0.
        for time_dim in range(rows):
            vk = data[time_dim].reshape([1, torch.tensor(data[time_dim].size()).item()])
            v0 = data[time_dim].reshape([1, torch.tensor(data[time_dim].size()).item()])
            ph0,_ = self.sample_h(v0)
            for k in range(1):
                _,hk = self.sample_h(vk)
                _,vk = self.sample_v(hk)
                vk[v0 < 0] = v0[v0 < 0]
            phk,_ = self.sample_h(vk)
            self.train(v0, vk, ph0, phk)
            loss = torch.mean(torch.abs(v0[v0>=0] - vk[v0>=0]))

            if loss.isnan():
              continue

            training_loss += loss
            mse_loss += torch.pow(training_loss, 2)

            s += 1.
            print(f"Training epoch {epoch} [", end="", flush=True)

            for i in range(49):
              if(int((time_dim / rows * 100) / 2) > i):
                print("=", end="", flush=True)
              else:
                print("-", end="", flush=True)

            print(f"]", end="\r", flush=True)
        print("\nLoss (MAE): "+str(training_loss/s))
        print("Loss (MSE): "+str(mse_loss/s))
        # cleaning up the buffer
        sys.stdout.flush()

    self.vk = vk
    return vk
