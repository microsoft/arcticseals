export PYTHONPATH=$(pwd)
python tools/train_net.py --config-file "configs/e2e_faster_rcnn_X_101_32x8d_FPN_1x.yaml" DATASETS.TRAIN \(\'vott_seals_large_IR_N_train\',\) DATASETS.TEST \(\"vott_seals_large_IR_N_test\",\) SOLVER.IMS_PER_BATCH 1 SOLVER.BASE_LR 0.00125 TEST.IMS_PER_BATCH 1 SOLVER.STEPS \(16000,18000\) SOLVER.MAX_ITER 20000
