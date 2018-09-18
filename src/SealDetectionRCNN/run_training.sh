python train.py train \
--env='fasterrcnn-caffe' \
--plot-every=100 \
--caffe-pretrain  \
--dataset='vott' \
--train_image_dir='/data/seals/seal_data_vott/sealdata_large_IR_N/train/' \
--val_image_dir='/data/seals/seal_data_vott/sealdata_large_IR_N/test/' \
--num_epochs=200 \
--epoch_decay=150 \
--plot_every=20 
# --max_size=5000
#--load_path='checkpoints/fasterrcnn_07101509'
