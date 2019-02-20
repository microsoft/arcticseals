export NGPUS=1
export PYTHONPATH=$(pwd)
python -m torch.distributed.launch --nproc_per_node=$NGPUS tools/test_net.py --config-file "configs/e2e_faster_rcnn_X_101_32x8d_FPN_1x.yaml" DATASETS.TRAIN \(\'vott_seals_large_IR_N_train\',\) DATASETS.TEST \(\"vott_seals_large_IR_N_test\",\) SOLVER.IMS_PER_BATCH 1 SOLVER.BASE_LR 0.005 TEST.IMS_PER_BATCH 1 MODEL.DEVICE cuda
