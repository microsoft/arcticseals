import os
import glob
import numpy as np

from .util import read_image
import PIL

from utils.config import opt


class VottBboxDataset:
    """Bounding box dataset loader for VOTT / CNTK Faster RCNN format

    The index corresponds to each image.

    When queried by an index, if :obj:`return_difficult == False`,
    this dataset returns a corresponding
    :obj:`img, bbox, label`, a tuple of an image, bounding boxes and labels.
    This is the default behaviour.
    If :obj:`return_difficult == True`, this dataset returns corresponding
    :obj:`img, bbox, label, difficult`. :obj:`difficult` is a boolean array
    that indicates whether bounding boxes are labeled as difficult or not.

    The bounding boxes are packed into a two dimensional tensor of shape
    :math:`(R, 4)`, where :math:`R` is the number of bounding boxes in
    the image. The second axis represents attributes of the bounding box.
    They are :math:`(y_{min}, x_{min}, y_{max}, x_{max})`, where the
    four attributes are coordinates of the top left and the bottom right
    vertices.

    The labels are packed into a one dimensional tensor of shape :math:`(R,)`.
    :math:`R` is the number of bounding boxes in the image.
    The class name of the label :math:`l` is :math:`l` th element of
    :obj:`VOC_BBOX_LABEL_NAMES`.

    The array :obj:`difficult` is a one dimensional boolean array of shape
    :math:`(R,)`. :math:`R` is the number of bounding boxes in the image.
    If :obj:`use_difficult` is :obj:`False`, this array is
    a boolean array with all :obj:`False`.

    The type of the image, the bounding boxes and the labels are as follows.

    * :obj:`img.dtype == numpy.float32`
    * :obj:`bbox.dtype == numpy.float32`
    * :obj:`label.dtype == numpy.int32`
    * :obj:`difficult.dtype == numpy.bool`

    Args:
        data_dir (string): Path to the root of the training data. 
            i.e. "/data/image/voc/VOCdevkit/VOC2007/"
        root (string): path to folder, which contains train_val_images
        ann_file (string): path to file, which contains the bounding box 
            annotations

    """
    
    def __init__(self, root):
        self.root = root
        print('Loading images from folder ' + root)
        # set up the filenames and annotations
        old_dir = os.getcwd()
        os.chdir(root)
        self.impaths = sorted(glob.glob('*.JPG'))
        print('Found {} images'.format(len(self.impaths)))
        self.image_ids = list(range(len(self.impaths)))
        
        # This loop reads the bboxes and corresponding labels and assigns them
        # the correct image. Kind of slow at the moment...
        self.bboxes = [[] for _ in self.image_ids]
        self.labels = [[] for _ in self.image_ids]
        self.class_names = []
        for image_id, impath in enumerate(self.impaths):
            bbox_labels = np.loadtxt(os.path.splitext(impath)[0] + '.bboxes.labels.tsv', dtype=str)
            # BBox coords are stored in the format
            # x_min (of width axis) y_min (of height axis), x_max, y_max
            # Coordinate system starts in top left corner
            bbox_coords = np.loadtxt(os.path.splitext(impath)[0] + '.bboxes.tsv', dtype=np.int32)
            if len(bbox_coords.shape) == 1:
                bbox_coords = bbox_coords[None,:]
            if bbox_labels.size == 1:
                bbox_labels = bbox_labels[None]
            assert len(bbox_coords) == len(bbox_labels)
            for i in range(len(bbox_coords)):
                if bbox_labels[i] not in self.class_names:
                    self.class_names.append(bbox_labels[i])
                bb = bbox_coords[i]
                # In this framework, we need ('ymin', 'xmin', 'ymax', 'xmax') format
                self.bboxes[image_id].append([bb[1],bb[0],bb[3],bb[2]])
                self.labels[image_id].append(self.class_names.index(bbox_labels[i]))
        
        self.classes = list(range(len(self.class_names)))
        # print out some stats
        print("The dataset has {} images containing {} classes".format(
                  len(self.image_ids),
                  len(self.classes)))
        os.chdir(old_dir)
        
        # To make sure we loaded the bboxes correctly:        
        self.validate_bboxes()
        print("All checks passed")
            

    def __len__(self):
        return len(self.image_ids)
        
    def validate_bboxes(self):
        import traceback
        import sys
        from tqdm import tqdm
        try:
            for idx in tqdm(range(len(self.image_ids))):
                img_file = os.path.join(self.root, self.impaths[idx])
                width,height = PIL.Image.open(img_file).size
                for bbox in self.bboxes[idx]:
                    assert bbox[1] <= width 
                    assert bbox[3] <= width
                    assert bbox[0] <= height
                    assert bbox[2] <= height
                    assert bbox[3] > bbox[1]
                    assert bbox[2] > bbox[0]
                    # Make sure all are greater equal 0
                    assert np.all(np.array(bbox) >= 0)
        except:
            extype, value, tb = sys.exc_info()
            traceback.print_exc()
            import ipdb
            ipdb.post_mortem(tb)
            
    def get_class_count(self):
        return np.max(self.classes).tolist() + 1

    def get_example(self, i):
        """Returns the i-th example.

        Returns a color image and bounding boxes. The image is in CHW format.
        The returned image is RGB.

        Args:
            i (int): The index of the example.

        Returns:
            tuple of an image in CHW format, bounding boxes in 
            ('ymin', 'xmin', 'ymax', 'xmax')  format, label as int32
            starting from 0 and difficult_flag.

        """
        img_file = os.path.join(self.root, self.impaths[i])
        img = read_image(img_file, color=True)
        
        bboxes = np.array(self.bboxes[i])
        labels = np.array(self.labels[i])
        difficulties = np.array([0 for _ in labels])
        image_id = np.array([self.image_ids[i]])
        
        return img, bboxes, labels, difficulties, image_id

    __getitem__ = get_example
    
    def get_class_names(self):
        return self.class_names
