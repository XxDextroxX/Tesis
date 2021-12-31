import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.parallel
import torch.optim as optim
import torch.utils.data

from torch.autograd import Variable

class RBM():
  def __init__(self, visible_nodes, hidden_nodes, w: torch.tensor = None):
    # self.visible_nodes = visible_nodes
    # self.hidden_nodes = hidden_nodes
    self.w = torch.randn(hidden_nodes, visible_nodes)

    # TODO: check if this is correct
    self.w[:w.size()[0], :w.size()[1]] = w

    # biases
    # P(h|v)
    self.h_bias = torch.randn(1, hidden_nodes)

    # P(v|h)
    self.v_bias = torch.randn(1,  visible_nodes)

  # A sample of probability of activiation nodes H knowing the node V
  def sample_h(self, visible_node):
    # product between [self.h_bias] and [self.w].
    # The transpose is to make them compatible
    wv = torch.mm(visible_node, self.w.t())

    # expand_as is useful to fit the dimension of
    # tensors in order to be able to perform tensor
    # operations
    activation = wv + self.h_bias.expand_as(wv)

    # P(h | v), If h fits the requiriments of v, then the probability
    # of activation should be high
    ph_given_v = torch.sigmoid(activation) # now this is actually the probability

    # Returns as many probabilitys as hidden nodes I have.
    # the second return is a probablity distribution, I don't know why
    # so if later I figure out why I need it I will update this commentary
    return ph_given_v, torch.bernoulli(ph_given_v)

    # A sample of probability of activiation nodes V knowing the node H
  def sample_v(self, hidden_node):
    # product between [self.v_bias] and [self.w].
    # The transpose is to make them compatible but here is not necessary
    # since tensors are compatible
    wh = torch.mm(hidden_node, self.w)

    # expand_as is useful to fit the dimension of
    # tensors in order to be able to perform tensor
    # operations
    activation = wh + self.v_bias.expand_as(wh)

    # P(h | v), If h fits the requiriments of v, then the probability
    # of activation should be high
    pv_given_h = torch.sigmoid(activation) # now this is actually the probability

    # Returns as many probabilitys as hidden nodes I have.
    # the second return is a probablity distribution, I don't know why
    # so if later I figure out why I need it I will update this commentary
    return pv_given_h, torch.bernoulli(pv_given_h)

  # v0 is visible nodes tensor with original ponderation... wait, WTF!!! yeah, yeah, 
  # I know, let me explain it. You have a list of all the value of visible nodes, right?
  # Well, that tensor is v0. Now, what a hell is vk? As you know you'll train your model
  # for k epochs, and vk is the state of v0 after k epochs. Now, ph0 is P(h|v0), that's
  # the original probability of every single visible node in v0, and as you could guess,
  # phk is p(h | vk).
  def train(self, v0, vk, ph0, phk):
    self.w += (torch.mm(v0.t(), ph0) + torch.mm(vk.t(), phk)).t()
    self.v_bias += torch.sum((v0 - vk), 0) # WTF!!! Diosito ya llevame :(
    self.h_bias += torch.sum((ph0 - phk), 0) # ...

  def fit(self, epochs, data):
    for epoch in range(epochs): # 100 epochs
      training_loss = 0.0
      n_observation = 0 # how many records the model observed
      
      for month in range(12):
        vk = torch.FloatTensor([data[month]])
        v0 = torch.FloatTensor([data[month]])
        
        ph0, _ = self.sample_h(v0)
        phk, _ = self.sample_h(vk)

        for k in range(20): # how many iterations in the same record
          # getting nodes that are active according to bernoulli distribution
          _, hk = self.sample_h(vk)
          _, vk = self.sample_v(hk)

          # frizing -1 values 'cause -1 means there is no data
          vk[v0 == -1] = v0[v0 == -1]
        
        phk, _ = self.sample_h(vk)
        self.train(v0, vk, ph0, phk)
        
        loss_value = torch.mean(torch.abs(v0[v0 >= 0] - vk[v0 >= 0]))

        if(loss_value.size() != torch.Size([])):
          training_loss += loss_value
          n_observation += 1.0

      print(f"Epochs: {epoch + 1}, loss: {training_loss / (n_observation if n_observation != 0 else 1)}")
    return vk
