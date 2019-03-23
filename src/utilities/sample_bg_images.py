import random
random.seed(0)
import tqdm
import argparse
import download_file_from_zip
import os
from joblib import Parallel, delayed
import multiprocessing

parser = argparse.ArgumentParser('This script will download a random subset of images from the arcticseals archives. It is possible ' + \
                                'to specify allowed prefixes for the archive and image file names in order to select only images of specific flights etc.')
parser.add_argument('--image_manifest', help='Path to the ImageManifest.csv containing a list of all images and the corresponding archive', required=True)
parser.add_argument("--archive_prefix", help='The name of the archives to consider, e.g. TrainingBackground_Color', type=str, required=True)
parser.add_argument("--file_prefixes", help='Path to text file containing a list of allowed image name prefixes, e.g. the prefix used for images of a specific ' + \
                    'set of flights', type=str, required=True)
parser.add_argument('--output_dir', help='Path to directory where we will save the downloaded images', type=str, required=True)
parser.add_argument('--num_images', help='Number of images to download', type=int, required=True)
args = parser.parse_args()


os.makedirs(args.output_dir, exist_ok=True)
with open(args.image_manifest, 'rt') as fi:
    all_images = fi.read().splitlines()
with open(args.file_prefixes, 'rt') as fi:
    all_file_prefixes = fi.read().splitlines()
selected_images = []
for im in all_images:
    for file_prefix in all_file_prefixes:
        if file_prefix in im and args.archive_prefix in im:
            selected_images.append(im)
random.shuffle(selected_images)


def process_images(i):
    image_name, archive = selected_images[i].split(',')
    if not os.path.isfile(os.path.join(args.output_dir, image_name)):
        download_file_from_zip.download_file('https://lilablobssc.blob.core.windows.net/arcticseals/data/' + archive, image_name, os.path.join(args.output_dir,
                                                                                                                                           image_name))
    open(os.path.join(args.output_dir, image_name[:-4] + '.bboxes.tsv'), 'a').close()
    open(os.path.join(args.output_dir, image_name[:-4] + '.bboxes.labels.tsv'), 'a').close()

#res = Parallel(n_jobs=24)(delayed(process_images)(i) for i in range(args.num_images))
with multiprocessing.Pool(processes=4*6) as pool:
    for _ in tqdm.tqdm(pool.imap_unordered(process_images, range(args.num_images)), total=args.num_images):
        pass
