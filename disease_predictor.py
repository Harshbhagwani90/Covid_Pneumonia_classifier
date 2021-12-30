# -*- coding: utf-8 -*-
"""DISEASE_PREDICTOR.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BLMkYzlLRBz2uIJV8qj2ROLjavq1z_UZ
"""

!unzip '/content/disease_dataset.zip'

"""Dataloader"""

import matplotlib.pyplot as plt
import numpy as np

import torch
import torchvision
import torchvision.transforms as transforms

transform_train = transforms.Compose([
    transforms.RandomResizedCrop(256), 
    transforms.ToTensor(),
    transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5)),
    ])

transform_test = transforms.Compose([
    transforms.RandomResizedCrop(256), 
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,)),
    ])

pip install split-folders

import splitfolders

splitfolders.ratio('disease_dataset',output='dataset',ratio=(0.7,0.3))

trainset=torchvision.datasets.ImageFolder(root='/content/dataset/train',transform=transform_train)

testset=torchvision.datasets.ImageFolder(root='/content/dataset/val',transform=transform_test)

batch_size = 10

trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,shuffle=True)

testloader=torch.utils.data.DataLoader(testset, batch_size=batch_size,shuffle=True)

def imshow(img, title):
    npimg = img.numpy() / 2 + 0.5
    plt.figure(figsize=(batch_size, 1))
    plt.axis('off')
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.title(title)
    plt.show()

def show_batch_images(dataloader):
    images, labels = next(iter(dataloader))
    img = torchvision.utils.make_grid(images)
    imshow(img, title=[str(x.item()) for x in labels])

images, labels = next(iter(trainloader))

print(images.shape)

for i in range(batch_size):
    show_batch_images(trainloader)

"""Model_resnetxt"""

from torchvision import models

import torch

resnetxt= models.resnext50_32x4d(pretrained=True)

print(resnetxt)

for param in resnetxt.parameters():
    param.requires_grad = False

num_classes=3

in_features = resnetxt.fc.in_features
resnetxt.fc = torch.nn.Linear(in_features, num_classes)

resnetxt = resnetxt
loss_fn = torch.nn.CrossEntropyLoss()
opt = torch.optim.Adam(resnetxt.parameters(), lr=3e-4)

import copy

max_epochs=20

def evaluation(dataloader, model):
    total, correct = 0, 0
    for data in dataloader:
        inputs, labels = data
        # inputs, labels = inputs.to(device), labels.to(device)
        outputs = model(inputs)
        _, pred = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (pred == labels).sum().item()
    return 100 * correct / total

def show_images(images, labels, preds):
    preds=preds.detach()
    plt.figure(figsize=(20,20))
    for i, image in enumerate(images):
        plt.subplot(1,20,i+1, xticks=[], yticks=[])
        image = image.numpy().transpose((1,2,0))
        mean = np.array([0.5])
        std = np.array([0.5])
        image = image * std + mean
        image = np.clip(image, 0., 1.)
        plt.imshow(image)
        print(classes[int(np.argmax(preds[i].numpy()))],end=' ' )
        plt.xlabel(f'{classes[int(labels[i].numpy())]}')
    plt.tight_layout()
    plt.show()

classes=['Normal','covid','pneumonia']

loss_epoch_arr = []
min_loss = 1000

for epoch in range(max_epochs):

    for i, data in enumerate(trainloader, 0):

        inputs, labels = data
        # inputs, labels = inputs.to(device), labels.to(device)

        opt.zero_grad()

        outputs = resnetxt(inputs)
        loss = loss_fn(outputs, labels)
        loss.backward()
        opt.step()
        
        if min_loss > loss.item():
            min_loss = loss.item()
            best_model = copy.deepcopy(resnetxt.state_dict())
            # print('Min loss %0.2f' % min_loss)
        
        if i % 100 == 0:
            print('Iteration: %d, Loss: %0.2f' % (i,loss.item()))
            show_images(inputs,labels,outputs)
            
        del inputs, labels, outputs
        torch.cuda.empty_cache()
        
    loss_epoch_arr.append(loss.item())
        
    print('Epoch: %d/%d, Test acc: %0.2f, Train acc: %0.2f' % (
        epoch, max_epochs, 
        evaluation(testloader, resnetxt), evaluation(trainloader, resnetxt)))
    
    
plt.plot(loss_epoch_arr)
plt.show()

"""FORMAT :
1. predicted values 
2. image
3. real values
"""

resnetxt.load_state_dict(best_model)
print(evaluation(trainloader, resnetxt), evaluation(testloader, resnetxt))

for i,data in enumerate(trainloader,0):
    inputs,labels=data
    outputs = resnetxt(inputs)
    print(i)
    show_images(inputs,labels,outputs)

"""Test result after training:"""

for i,data in enumerate(testloader,0):
    inputs,labels=data
    outputs = resnetxt(inputs)
    if i%2==0:
        print(i)
        show_images(inputs,labels,outputs)

print('Overall accuracy on test data',evaluation(testloader, resnetxt))