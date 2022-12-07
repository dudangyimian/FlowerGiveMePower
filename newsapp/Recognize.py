from PIL import Image
from torchvision import transforms
import torch

# -*- coding=utf-8 -*-
import socket
import threading
import sys
import os
import struct


def recognize_image(pa):
    
        
    print("start image recognition path before:")
    # print(pa)
    #
    # pa = pa[2:]
    #
    # print(type(pa))
    #
    #
    # pa = os.path.join(os.path.dirname(os.path.abspath(__file__)), pa)
    #
    #
    #
    # print(pa)
    
    model = torch.hub.load('pytorch/vision:v0.10.0', 'alexnet', pretrained=True)
    # filename = 'amazon.png'
    # filename =  input("Which file do you want to test?")
    input_image = Image.open(pa).convert('RGB')
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model
    
    # move the input and model to GPU for speed if available
    if torch.cuda.is_available():
        input_batch = input_batch.to('cuda')
        model.to('cuda')
    
    with torch.no_grad():
        output = model(input_batch)
    # Tensor of shape 1000, with confidence scores over Imagenet's 1000 classes
    print(output[0])
    # The output has unnormalized scores. To get probabilities, you can run a softmax on it.
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    print(type(probabilities))
    print(probabilities)
    
    
    
    with open("imagenet_classes.txt", "r") as f:
        categories = [s.strip() for s in f.readlines()]
    # Show top categories per image
    top5_prob, top5_catid = torch.topk(probabilities, 5)
    for i in range(top5_prob.size(0)):
        print(categories[top5_catid[i]], top5_prob[i].item())
        
    retstr = str(categories[top5_catid[0]]) +"\\"+ str(top5_prob[0].item())

    return retstr



#yangeng@pcvm3-2.instageni.hawaii.edu:/users/yangeng/unreal


def deal_data(conn, addr):
    print('Accept new connection from {0}'.format(addr))
    while True:
        fileinfo_size = struct.calcsize('128sl')  # linux 和 windows 互传 128sl 改为 128sq  机器位数不一样，一个32位一个64位
        buf = conn.recv(fileinfo_size)
        print('收到的字节流：', buf, type(buf))
        if buf:
            print(buf, type(buf))
            filename, filesize = struct.unpack('128sl', buf)
            fn = filename.strip(str.encode('\00'))
            new_filename = os.path.join(str.encode('./'), str.encode('new_') + fn)
            print(new_filename)
            print('file new name is {0}, filesize is {1}'.format(new_filename, filesize))
            recvd_size = 0  # 定义已接收文件的大小
            with open(new_filename, 'wb') as fp:
                print("start receiving...")
                while not recvd_size == filesize:
                    if filesize - recvd_size > 1024:
                        data = conn.recv(1024)
                        recvd_size += len(data)
                    else:
                        data = conn.recv(filesize - recvd_size)
                        recvd_size = filesize

                    fp.write(data)
            print("end receive...")

        result = recognize_image(new_filename)

        conn.send(result.encode())




        conn.close()
        break



def socket_service():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('128.171.8.118', 8192)) #
        s.listen(4)
    except socket.error as msg:
        print(msg)
        sys.exit(1)
    print("Waiting...")
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=deal_data, args=(conn, addr))
        t.start()


if __name__ == '__main__':
    socket_service()



    
    
    