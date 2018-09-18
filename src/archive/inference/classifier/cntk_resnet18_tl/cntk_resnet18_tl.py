from __future__ import print_function
import glob
import os
import argparse
import numpy as np
from PIL import Image
from shutil import copyfile
import sys
import tarfile
import time

# Load the right urlretrieve based on python version
try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

# Import CNTK and helpers
import cntk as C
import cntk.io.transforms as xforms

################################################
################################################
# general settings

# With Fast mode we train the model for fewer epochs and results have low accuracy but is good enough for 
# development.
isFast = False
force_retraining = True

################################################
################################################

# Ensures that a given path exists
def ensure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


# Downloads a resource if it doesn't exist already
def download_unless_exists(url, filename, max_retries=3):
    '''Download the file unless it already exists, with retry. Throws if all retries fail.'''
    if os.path.exists(filename):
        print('Reusing locally cached: ', filename)
    else:
        print('Starting download of {} to {}'.format(url, filename))
        retry_cnt = 0
        while True:
            try:
                urlretrieve(url, filename)
                print('Download completed.')
                return
            except:
                retry_cnt += 1
                if retry_cnt == max_retries:
                    print('Exceeded maximum retry count, aborting.')
                    raise
                print('Failed to download, retrying.')
                time.sleep(np.random.randint(1,10))


# Downloads the pre-trained model
def download_model(model_root):
    ensure_exists(model_root)
    resnet18_model_uri = 'https://www.cntk.ai/Models/ResNet/ResNet_18.model'
    resnet18_model_local = os.path.join(model_root, 'ResNet_18.model')
    download_unless_exists(resnet18_model_uri, resnet18_model_local)

    return resnet18_model_local


# Creates a minibatch source for training or testing
def create_mb_source(map_file, image_dims, num_classes, randomize=True):
    transforms = [xforms.scale(width=image_dims[2], height=image_dims[1], channels=image_dims[0], interpolations='linear')]
    return C.io.MinibatchSource(C.io.ImageDeserializer(map_file, C.io.StreamDefs(
            features=C.io.StreamDef(field='image', transforms=transforms),
            labels=C.io.StreamDef(field='label', shape=num_classes))),
            randomize=randomize)


# Creates the network model for transfer learning
def create_model(model_details, num_classes, input_features, new_prediction_node_name='prediction', freeze=False):
    # Load the pretrained classification net and find nodes
    base_model = C.load_model(model_details['model_file'])
    feature_node = C.logging.find_by_name(base_model, model_details['feature_node_name'])
    last_node = C.logging.find_by_name(base_model, model_details['last_hidden_node_name'])

    # Clone the desired layers with fixed weights
    cloned_layers = C.combine([last_node.owner]).clone(
        C.CloneMethod.freeze if freeze else C.CloneMethod.clone,
        {feature_node: C.placeholder(name='features')})

    # Add new dense layer for class prediction
    feat_norm = input_features - C.Constant(114)
    cloned_out = cloned_layers(feat_norm)
    z = C.layers.Dense(num_classes, activation=None, name=new_prediction_node_name) (cloned_out)

    return z


# Trains a transfer learning model
def train_model(model_details, num_classes, train_map_file,
                learning_params, max_images=-1):
    num_epochs = learning_params['max_epochs']
    epoch_size = sum(1 for line in open(train_map_file))
    if max_images > 0:
        epoch_size = min(epoch_size, max_images)
    minibatch_size = learning_params['mb_size']

    # Create the minibatch source and input variables
    minibatch_source = create_mb_source(train_map_file, model_details['image_dims'], num_classes)
    image_input = C.input_variable(model_details['image_dims'])
    label_input = C.input_variable(num_classes)

    # Define mapping from reader streams to network inputs
    input_map = {
        image_input: minibatch_source['features'],
        label_input: minibatch_source['labels']
    }

    # Instantiate the transfer learning model and loss function
    tl_model = create_model(model_details, num_classes, image_input, freeze=learning_params['freeze_weights'])
    ce = C.cross_entropy_with_softmax(tl_model, label_input)
    pe = C.classification_error(tl_model, label_input)

    # Instantiate the trainer object
    lr_schedule = C.learning_parameter_schedule(learning_params['lr_per_mb'])
    mm_schedule = C.momentum_schedule(learning_params['momentum_per_mb'])
    learner = C.momentum_sgd(tl_model.parameters, lr_schedule, mm_schedule,
                           l2_regularization_weight=learning_params['l2_reg_weight'])
    trainer = C.Trainer(tl_model, (ce, pe), learner)

    # Get minibatches of images and perform model training
    print("Training transfer learning model for {0} epochs (epoch_size = {1}).".format(num_epochs, epoch_size))
    C.logging.log_number_of_parameters(tl_model)
    progress_printer = C.logging.ProgressPrinter(tag='Training', num_epochs=num_epochs)
    for epoch in range(num_epochs):       # loop over epochs
        sample_count = 0
        while sample_count < epoch_size:  # loop over minibatches in the epoch
            data = minibatch_source.next_minibatch(min(minibatch_size, epoch_size - sample_count), input_map=input_map)
            trainer.train_minibatch(data)                                    # update model with it
            sample_count += trainer.previous_minibatch_sample_count          # count samples processed so far
            progress_printer.update_with_trainer(trainer, with_metric=True)  # log progress
            if sample_count % (100 * minibatch_size) == 0:
                print ("Processed {0} samples".format(sample_count))

        progress_printer.epoch_summary(with_metric=True)

    return tl_model


# Evaluates a single image using the re-trained model
def eval_single_image(loaded_model, image_path, image_dims):
    # load and format image (resize, RGB -> BGR, CHW -> HWC)
    try:
        img = Image.open(image_path)

        if image_path.endswith("png"):
            temp = Image.new("RGB", img.size, (255, 255, 255))
            temp.paste(img, img)
            img = temp
        resized = img.resize((image_dims[2], image_dims[1]), Image.ANTIALIAS)
        bgr_image = np.asarray(resized, dtype=np.float32)[..., [2, 1, 0]]
        hwc_format = np.ascontiguousarray(np.rollaxis(bgr_image, 2))

        # compute model output
        arguments = {loaded_model.arguments[0]: [hwc_format]}
        output = loaded_model.eval(arguments)

        # return softmax probabilities
        sm = C.softmax(output[0])

        return sm.eval()
    
    except FileNotFoundError:
        print("Could not open (skipping file): ", image_path)
        
        return ['None']


# Evaluates an image set using the provided model
def eval_test_images(loaded_model, output_file, test_map_file, image_dims, max_images=-1, column_offset=0):
    num_images = sum(1 for line in open(test_map_file))
    if max_images > 0:
        num_images = min(num_images, max_images)
    if isFast:
        num_images = min(num_images, 300) #We will run through fewer images for test run

    print("Evaluating model output node '{0}' for {1} images.".format('prediction', num_images))

    pred_count = 0
    correct_count = 0
    np.seterr(over='raise')
    with open(output_file, 'wb') as results_file:
        with open(test_map_file, "r") as input_file:
            for line in input_file:
                tokens = line.rstrip().split('\t')
                img_file = tokens[0 + column_offset]
                probs = eval_single_image(loaded_model, img_file, image_dims)

                if probs[0]=='None':
                    print("Eval not possible: ", img_file)
                    continue

                pred_count += 1
                true_label = int(tokens[1 + column_offset])
                predicted_label = np.argmax(probs)
                if predicted_label == true_label:
                    correct_count += 1

                #np.savetxt(results_file, probs[np.newaxis], fmt="%.3f")
                if pred_count % 100 == 0:
                    print("Processed {0} samples ({1:.2%} correct)".format(pred_count,
                                                                           (float(correct_count) / pred_count)))
                if pred_count >= num_images:
                    break
    print ("{0} of {1} prediction were correct".format(correct_count, pred_count))
    return correct_count, pred_count, (float(correct_count) / pred_count)

python_version = sys.version_info.major

# Create the map file used by CNTK training & testing for a given folder
def create_map_file_from_folder(root_folder, class_mapping, include_unknown=False, valid_extensions=['.jpg', '.jpeg', '.png']):
    map_file_name = os.path.join(root_folder, "map.txt")

    map_file = None

    if python_version == 3:
        map_file = open(map_file_name , 'w', encoding='utf-8')
    else:
        map_file = open(map_file_name , 'w')

    for class_id in range(0, len(class_mapping)):
        folder = os.path.join(root_folder, class_mapping[class_id])
        if os.path.exists(folder):
            for entry in os.listdir(folder):
                filename = os.path.abspath(os.path.join(folder, entry))
                if os.path.isfile(filename) and os.path.splitext(filename)[1].lower() in valid_extensions:
                    try:
                        map_file.write("{0}\t{1}\n".format(filename, class_id))
                    except UnicodeEncodeError:
                        continue

    if include_unknown:
        for entry in os.listdir(root_folder):
            filename = os.path.abspath(os.path.join(root_folder, entry))
            if os.path.isfile(filename) and os.path.splitext(filename)[1].lower() in valid_extensions:
                try:
                    map_file.write("{0}\t-1\n".format(filename))
                except UnicodeEncodeError:
                    continue

    map_file.close()

    return map_file_name

# Create the class mapping used by CNTK training & testing for a given folder
def create_class_mapping_from_folder(root_folder):
    classes = []
    for _, directories, _ in os.walk(root_folder):
        for directory in directories:
            classes.append(directory)

    return np.asarray(classes)

if __name__=='__main__':
    # Default Paths relative to current python file.
    abs_path   = os.path.dirname(".")
    data_path  = os.path.join(abs_path, 'seal_data')
    
    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('-datadir', '--datadir', help='Data directory where the seals dataset is located', required=False, default=data_path)
    parser.add_argument('-outputdir', '--outputdir', help='Output directory for checkpoints and models', required=False, default=None)
    parser.add_argument('-logdir', '--logdir', help='Log file', required=False, default=None)
    parser.add_argument('-n', '--num_epochs', help='Total number of epochs to train', type=int, required=False, default='30')
    parser.add_argument('-m', '--minibatch_size', help='Minibatch size', type=int, required=False, default='50')
    parser.add_argument('-device', '--device', type=int, help="Force to run the script on a specified device", required=False, default=None)
    
    args = vars(parser.parse_args())

    if args['datadir'] is not None:
        data_path = args['datadir']
    if args['outputdir'] is not None:
        model_path = args['outputdir'] + "/models"
    else:
        model_path = os.path.join(data_path, "models")
    if args['logdir'] is not None:
        log_dir = args['logdir']
    if args['device'] is not None:
        if args['device'] == -1:
            C.device.try_set_default_device(C.device.cpu())
        else:
            C.device.try_set_default_device(C.device.gpu(args['device']))

    if not os.path.isdir(data_path):
        raise RuntimeError("Directory %s does not exist" % data_path)

    training_images_folder = os.path.join(data_path, 'images/Train')
    testing_images_folder = os.path.join(data_path, 'images/Test')

    class_mapping = create_class_mapping_from_folder(training_images_folder)
    train_map = create_map_file_from_folder(training_images_folder, class_mapping)
    test_map = create_map_file_from_folder(testing_images_folder, class_mapping)

    resnet_pretrained_model = download_model(model_root=model_path)

    # Define base model location and characteristics
    base_model = {
        'model_file': os.path.join(model_path, 'ResNet_18.model'),
        'feature_node_name': 'features',
        'last_hidden_node_name': 'z.x',
        # Channel Depth x Height x Width
        'image_dims': (3, 224, 224)
    }

    # Print out all layers in the model
    print('Loading {} and printing all layers:'.format(base_model['model_file']))
    node_outputs = C.logging.get_node_outputs(C.load_model(base_model['model_file']))
    for l in node_outputs: print("  {0} {1}".format(l.name, l.shape))
    np.random.seed(123)


    max_training_epochs = args['num_epochs']
    if isFast:
        max_training_epochs = 2
        print('Warning: number of epochs was overriden by isFast setting to ', max_training_epochs)
        
    learning_params = {
        'max_epochs': max_training_epochs,
        'mb_size': args['minibatch_size'],
        'lr_per_mb': [0.2]*10 + [0.1],
        'momentum_per_mb': 0.9,
        'l2_reg_weight': 0.0005,
        'freeze_weights': False
    }

    seals_model = {
        'model_file': os.path.join(model_path, 'ResNet18_Seals_TL.model'),
        'results_file': os.path.join(model_path, 'ResNet18_Seals_TL_Predictions.txt'),
        'num_classes': 2
    }

    # Train only if no model exists yet or if force_retraining is set to True
    if os.path.exists(seals_model['model_file']) and not force_retraining:
        print("Loading existing model from %s" % seals_model['model_file'])
        trained_model = C.load_model(seals_model['model_file'])
    else:
        print("Transfer learning...")
        trained_model = train_model(base_model,
                                    seals_model['num_classes'], train_map,
                                    learning_params)
        trained_model.save(seals_model['model_file'])
        print("Stored trained model at %s" % seals_model['model_file'])

    # evaluate test images
    print('True class, Predicted class, Prediction details, Image File')
    with open(test_map, 'r') as input_file:
        for line in input_file:
            tokens = line.rstrip().split('\t')
            img_file = tokens[0]
            true_label = int(tokens[1])
            probs = eval_single_image(trained_model, img_file, base_model['image_dims'])

            if probs[0]=='None':
                continue
            class_probs = np.column_stack((probs, class_mapping)).tolist()
            class_probs.sort(key=lambda x: float(x[0]), reverse=True)
            prediction_details = ' '.join(['%s:%.3f' % (class_probs[i][1], float(class_probs[i][0])) \
                                    for i in range(0, seals_model['num_classes'])])
            prediction = class_probs[0][1]
            true_class_name = class_mapping[true_label] if true_label >= 0 else 'unknown'
            print('%s, %s, %s, %s' % (true_class_name, prediction, prediction_details, img_file))