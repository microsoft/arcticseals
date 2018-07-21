import argparse
import glob
import numpy as np
import os
from PIL import Image, ImageDraw


boxs_suffix = '.bboxes.tsv'
labels_suffix = '.bboxes.labels.tsv'


def draw_bboxes(image, boxes, labels, show_labels, thickness=1):
    """
    Draw bounding boxes on top of an image
    Args:
        image : PIL image to be modified
        boxes: An (N, 4) array of boxes to draw, where N is the number of boxes.
        classes: An (N, 1) array of labels corresponding to each bounding box.
    Returns:
        An array of the same shape as 'image' with bounding boxes and classes drawn
    """
    draw = ImageDraw.Draw(image)

    for i in range(len(boxes)):
        xmin, ymin, xmax, ymax = boxes[i]
        c = labels[i]

        if show_labels:
            draw.text((xmin + 15, ymin + 15), str(c))

        color = 'blue' if c == 'organic' else 'green'

        for j in range(thickness):
            draw.rectangle(((xmin + j, ymin + j), (xmax + j, ymax + j)), outline=color)
    return image


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', default='../pilot_images_and_annotations/test', help='Path to directory containing jpeg images')
    parser.add_argument('-o', '--output_dir', default='../pilot_images_and_annotations/test_bb', help='Path to directory to place the images with bounding boxes marked')
    parser.add_argument('-l', '--show_labels', action='store_true', help='If text annotations are shown on each bounding box')
    args = parser.parse_args()

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)

    image_paths = sorted(glob.glob(os.path.join(args.input_dir, '*.jpg')))

    boxes_fnames = [os.path.basename(image_path).split('.')[0] + boxs_suffix for image_path in image_paths]
    labels_fnames = [os.path.basename(image_path).split('.')[0] + labels_suffix for image_path in image_paths]

    for image_path, boxes_fname, labels_fname in zip(image_paths, boxes_fnames, labels_fnames):
        image = Image.open(image_path)
        boxes = np.loadtxt(os.path.join(args.input_dir, boxes_fname), dtype=int)
        labels = np.loadtxt(os.path.join(args.input_dir, labels_fname), dtype=str)
        image_annotated = draw_bboxes(image, boxes, labels, args.show_labels)
        image_annotated.save(os.path.join(args.output_dir, '{}.bb.jpg'.format(os.path.basename(image_path).split('.')[0])))
