import os
import sys
import torch
import numpy as np
import pandas as pd
import torch.nn as nn
import torch.utils.data
import matplotlib.pyplot as plt

from coconet import CocoNet, device
from utils import *

N = 6  # Number of attributes
M = 32  # Two measures worth of sixteenth notes
batch_size = 24
EPOCHS = 30000

if __name__ == '__main__':

    all_scores = []
    files = os.listdir('features')

    for f in files:

        if '.h5' in f:
            mat = pd.read_hdf('features/' + f)
            all_scores.append(mat.to_numpy())

    # Cut the data into two measure chunks
    train_data = []
    for score in all_scores:
        cut = 0
        while cut < score.shape[1]-M:
            train_data.append(score[:, cut:cut+M])
            cut += M

    train_data = np.array(train_data).astype(int)

    max_num = -np.inf
    min_num = np.inf

    for i in train_data:
        if i.max() > max_num:
            max_num = int(i.max())
        if i.min() < min_num:
            min_num = int(i.min())

    # Train the model
    model = CocoNet()
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.00005)
    losses = []

    model.train()
    B = 24

    for i in range(EPOCHS):

        # Generate random mask (but exclude chords)
        C = np.random.randint(2, size=(B, N, M))
        for i in range(len(C)):
            C[i][0] = np.ones(len(C[i][0]))

        # Batch is of shape (B, N, M), entries are integers in [0, R)
        indices = np.random.choice(train_data.shape[0], size=B)
        batch = train_data[indices]

        # Targets is of shape (B*N*M)
        targets = batch.reshape(-1)
        targets = torch.tensor(targets)

        x = torch.tensor(batch).type(torch.FloatTensor)

        C2 = torch.tensor(C).type(torch.FloatTensor)
        out = model(x, C2)
        out = out.view(B*N*M, R)
        loss = loss_fn(out, targets)
        losses.append(loss.item())
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        # adjust learning rate
        if i % 5000 == 0:
            for g in optimizer.param_groups:
                g['lr'] *= .75

    torch.save(model.state_dict(), 'coconet_model.pt')
    plt.plot(losses)
    plt.show()
