from mmdet.apis import init_detector, inference_detector
import mmcv
import argparse
import numpy as np
import os

image_dir = "/home/ubuntu/webserver/outputImages"
output_dir = "/home/ubuntu/webserver/coordinates"
excel_dir = "/home/ubuntu/webserver/excel"

if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
if not os.path.isdir(excel_dir):
    os.mkdir(excel_dir)

config_file = '/home/ubuntu/webserver/pythonFiles/config.py'
checkpoint_file = '/home/ubuntu/webserver/epoch_21.pth'
model = init_detector(config_file, checkpoint_file, device='cuda:0')

def save_npy(result, image_id, output_dir):
    bbox_result, segm_result = result
    bboxes = np.vstack(bbox_result)
    labels = [
            np.full(bbox.shape[0], i, dtype=np.int32)
            for i, bbox in enumerate(bbox_result)
        ]
    labels = np.concatenate(labels)
    np.save(os.path.join(output_dir, image_id + '.npy'), bboxes)
    np.save(os.path.join(output_dir, image_id + '_labels.npy'), labels)
    
for root, dirs, files in os.walk(image_dir):
    for f in files:
        result = inference_detector(model, os.path.join(root, f))
        image_id = os.path.basename(f)
        image_id = image_id[:image_id.find('.')]

        save_npy(result, image_id, output_dir)
        
os.system('/home/ubuntu/anaconda3/envs/pytorch_p36/bin/python /home/ubuntu/webserver/pythonFiles/image_to_text.py')
