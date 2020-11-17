import torch
import numpy as np
import torch.nn as nn
import torch.utils.data

N = 3
M = 32
hidden = 32

if torch.cuda.is_available():
    device = 'cuda:0'
else:
    device = 'cpu'

class Unit(nn.Module):

    def __init__(self):
        super(Unit, self).__init__()
        self.conv1 = nn.Conv2d(hidden, hidden, 3, padding=1)
        self.batchnorm1 = nn.BatchNorm2d(hidden)
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv2d(hidden, hidden, 3, padding=1)
        self.batchnorm2 = nn.BatchNorm2d(hidden)
        self.relu2 = nn.ReLU()


    def forward(self, x):
        y = x
        y = self.conv1(y)
        y = self.batchnorm1(y)
        y = self.relu1(y)
        y = self.conv2(y)
        y = self.batchnorm2(y)
        y = y + x
        y = self.relu2(y)
        return y

class CocoNet(nn.Module):

    def __init__(self, R):

        super(CocoNet, self).__init__()
        self.R = R
        self.conv = nn.Conv2d(2*N, hidden, 3, padding=1)
        self.batchnorm = nn.BatchNorm2d(hidden)
        self.relu = nn.ReLU()
        self.unit1 = Unit()
        self.unit2 = Unit()
        self.unit3 = Unit()
        self.unit4 = Unit()
        self.unit5 = Unit()
        self.unit6 = Unit()
        self.unit7 = Unit()
        self.unit8 = Unit()
        self.unit9 = Unit()
        self.unit10 = Unit()
        self.unit11 = Unit()
        self.unit12 = Unit()
        self.unit13 = Unit()
        self.unit14 = Unit()
        self.unit15 = Unit()
        self.unit16 = Unit()
        self.affine = nn.Linear(hidden*M*R, N*M*R)

    def forward(self, x, C):

        B = x.shape[0]
        R = self.R

        tiled_C = C.view(B, N, M, 1)
        tiled_C = tiled_C.repeat(1, 1, 1, R)

        y = torch.cat((tiled_C*x, tiled_C), dim=1)

        y = self.conv(y)
        y = self.batchnorm(y)
        y = self.relu(y)
        y = self.unit1(y)
        y = self.unit2(y)
        y = self.unit3(y)
        y = self.unit4(y)
        y = self.unit5(y)
        y = self.unit6(y)
        y = self.unit7(y)
        y = self.unit8(y)
        y = self.unit9(y)
        y = self.unit10(y)
        y = self.unit11(y)
        y = self.unit12(y)
        y = self.unit13(y)
        y = self.unit14(y)
        y = self.unit15(y)
        y = self.unit16(y)

        y = y.view(B, hidden*M*R)
        y = self.affine(y)

        y = y.view(B, N, M, R)

        return y

    def pred(self, y, C):
        R = self.R
        compressed = y.reshape(-1)
        x = np.zeros((N*M, R))
        r = np.arange(N*M)
        x[r, compressed] = 1
        x = x.reshape(N, M, R)

        x = torch.tensor(x).type(torch.FloatTensor).to(device)
        x = x.view(1, N, M, R)
        C2 = torch.tensor(C).type(torch.FloatTensor).view(1, N, M).to(device)

        with torch.no_grad():
            out = self.forward(x, C2).view(N, M, R).cpu().numpy()
            out = out.transpose(2, 0, 1)

            probs = np.exp(out) / np.exp(out).sum(axis=0)
            cum_probs = np.cumsum(probs, axis=0)
            u = np.random.rand(N, M)

            return np.argmax(cum_probs > u, axis=0)
