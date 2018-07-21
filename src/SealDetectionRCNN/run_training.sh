python train.py train \
--env='fasterrcnn-caffe' \
--plot-every=100 \
--caffe-pretrain  \
--dataset='vott' \
--train_image_dir='/datadrive/train/' \
--val_image_dir='/datadrive/test/' \
--num_epochs=2000 \
--epoch_decay=1500 \
--plot_every=2 \
--max_size=1920 \
--min_size=1080 
#--load_path='checkpoints/fasterrcnn_07101509'
