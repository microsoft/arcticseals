import os

import matplotlib
from tqdm import tqdm
import time
import numpy as np

from model import faster_rcnn

from utils.config import opt
from data.dataset import Dataset, TestDataset, inverse_normalize
from model import FasterRCNNVGG16
from torch.autograd import Variable
from torch.utils import data as data_
from trainer import FasterRCNNTrainer
from utils import array_tool as at
from utils.vis_tool import visdom_bbox
from utils.eval_tool import eval_detection_voc
import torch.utils.data
import torch
torch.set_num_threads(1)

# fix for ulimit
# https://github.com/pytorch/pytorch/issues/973#issuecomment-346405667
#import resource

#rlimit = resource.getrlimit(resource.RLIMIT_NOFILE)
#resource.setrlimit(resource.RLIMIT_NOFILE, (20480, rlimit[1]))

matplotlib.use('agg')
import torch.backends.cudnn as cudnn
cudnn.benchmark = True

def eval(dataloader, faster_rcnn, test_num=10000):
    print('Running validation')
    # Each predicted box is organized as :`(y_{min}, x_{min}, y_{max}, x_{max}), 
    # Where y corresponds to the height and x to the width
    pred_bboxes, pred_labels, pred_scores = list(), list(), list()
    gt_bboxes, gt_labels, gt_difficults = list(), list(), list()
    image_ids = list()
    for ii, (imgs, sizes, gt_bboxes_, gt_labels_, gt_difficults_, image_ids_) in tqdm(
                                                     enumerate(dataloader), total=test_num):
        sizes = [sizes[0].detach().numpy().tolist()[0],  sizes[1].detach().numpy().tolist()[0]]
        pred_bboxes_, pred_labels_, pred_scores_ = faster_rcnn.predict(imgs, [sizes])
        # We have to add .copy() here to allow for the loaded image to be released after each iteration
        gt_bboxes += list(gt_bboxes_.numpy().copy())
        gt_labels += list(gt_labels_.numpy().copy())
        gt_difficults += list(gt_difficults_.numpy().copy())
        image_ids += list(image_ids_.numpy().copy())
        pred_bboxes += [pp.copy() for pp in pred_bboxes_]
        pred_labels += [pp.copy() for pp in pred_labels_]
        pred_scores += [pp.copy() for pp in pred_scores_]
        if ii == test_num: break

    result = eval_detection_voc(
        pred_bboxes, pred_labels, pred_scores,
        gt_bboxes, gt_labels, gt_difficults,
        use_07_metric=True)
    
    if opt.validate_only:
        save_path = '{}_detections.npz'.format(opt.load_path)
        np.savez(save_path, pred_bboxes=pred_bboxes, 
                            pred_labels=pred_labels,
                            pred_scores=pred_scores,
                            gt_bboxes=gt_bboxes, 
                            gt_labels=gt_labels, 
                            gt_difficults=gt_difficults,
                            image_ids=image_ids,
                            result=result)
    return result


def train(**kwargs):
    opt._parse(kwargs)

    print('load data')
    dataset = Dataset(opt)
    dataloader = data_.DataLoader(dataset, \
                                  batch_size=1, \
                                  shuffle=True, \
                                  # pin_memory=True,
                                  num_workers=opt.num_workers)
    testset = TestDataset(opt)
    test_dataloader = data_.DataLoader(testset,
                                       batch_size=1,
                                       num_workers=opt.test_num_workers,
                                       shuffle=False, \
                                       pin_memory=True
                                       )

    faster_rcnn = FasterRCNNVGG16(n_fg_class=dataset.get_class_count(), anchor_scales=[1])
    print('model construct completed')

    trainer = FasterRCNNTrainer(faster_rcnn, n_fg_class=dataset.get_class_count())

    if opt.use_cuda:
        trainer = trainer.cuda()

    if opt.load_path:
        old_state = trainer.load(opt.load_path)
        print('load pretrained model from %s' % opt.load_path)

    if opt.validate_only:
        num_eval_images = len(testset)
        eval_result = eval(test_dataloader, faster_rcnn, test_num=num_eval_images)
        print('Evaluation finished, obtained {} using {} out of {} images'.
                format(eval_result, num_eval_images, len(testset)))
        return
    
    if opt.load_path and 'epoch' in old_state.keys():
        starting_epoch = old_state['epoch'] + 1
        print('Model was trained until epoch {}, continuing with epoch {}'.format(old_state['epoch'], starting_epoch))
    else:
        starting_epoch = 0
    
    #trainer.vis.text(dataset.db.label_names, win='labels')
    best_map = 0
    lr_ = opt.lr
    global_step = 0
    for epoch in range(starting_epoch, opt.num_epochs):
        lr_ = opt.lr * (opt.lr_decay ** (epoch // opt.epoch_decay))
        trainer.faster_rcnn.set_lr(lr_)

        print('Starting epoch {} with learning rate {}'.format(epoch, lr_))
        trainer.reset_meters()
        for ii, (img, bbox_, label_, scale) in tqdm(enumerate(dataloader), total=len(dataset)):
            global_step = global_step + 1
            scale = at.scalar(scale)
            if opt.use_cuda:
                img, bbox, label = img.cuda().float(), bbox_.float().cuda(), label_.float().cuda()
            else:
                img, bbox, label = img.float(), bbox_.float(), label_.float()
            img, bbox, label = Variable(img), Variable(bbox), Variable(label)
            losses = trainer.train_step(img, bbox, label, scale)
            
            if (ii + 1) % opt.plot_every == 0:
                if os.path.exists(opt.debug_file):
                    ipdb.set_trace()

                # plot loss
                #trainer.vis.plot_many(trainer.get_meter_data())

                # plot groud truth bboxes
                ori_img_ = inverse_normalize(at.tonumpy(img[0]))
                gt_img = visdom_bbox(ori_img_,
                                     at.tonumpy(bbox_[0]),
                                     at.tonumpy(label_[0]),
                                     label_names=dataset.get_class_names()+['BG'])
                trainer.vis.img('gt_img', gt_img)

                # plot predicti bboxes
                _bboxes, _labels, _scores = trainer.faster_rcnn.predict([ori_img_], visualize=True)
                pred_img = visdom_bbox(ori_img_,
                                       at.tonumpy(_bboxes[0]),
                                       at.tonumpy(_labels[0]).reshape(-1),
                                       at.tonumpy(_scores[0]),
                                       label_names=dataset.get_class_names()+['BG'])
                trainer.vis.img('pred_img', pred_img)

                # rpn confusion matrix(meter)
                #trainer.vis.text(str(trainer.rpn_cm.value().tolist()), win='rpn_cm')
                # roi confusion matrix
                #trainer.vis.img('roi_cm', at.totensor(trainer.roi_cm.conf, False).float())
                
                #print('Current total loss {}'.format(losses[-1].tolist()))
                trainer.vis.plot('train_total_loss', losses[-1].tolist())
                
            if (global_step) % opt.snapshot_every == 0:
                snapshot_path = trainer.save(epoch=epoch)
                print("Snapshotted to {}".format(snapshot_path))

        #snapshot_path = trainer.save(epoch=epoch)
        #print("After epoch {}: snapshotted to {}".format(epoch,snapshot_path))
        
        eval_result = eval(test_dataloader, faster_rcnn, test_num=min(opt.test_num, len(testset)))
        print(eval_result)
        # TODO: this definitely is not good and will bias evaluation
        if eval_result['map'] > best_map:
            best_map = eval_result['map']
            best_path = trainer.save(best_map=eval_result['map'],epoch=epoch)
            print("After epoch {}: snapshotted to {}".format(epoch, best_path))


        trainer.vis.plot('test_map', eval_result['map'])


if __name__ == '__main__':
    import fire

    fire.Fire()

