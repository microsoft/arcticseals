# Seal detection API server and notebook
This code shows how to run the seals detection as an API server and how to use this server in an Jupyter notebook. 


## Download the model
Copy the folder `/ai4edevfs/models/seals-detection-ir-n-large-86.0` to the `models` directory of the SealDetectionAPI folder. 
This models folder will be copied to the docker image as `/app/models`. Now adjust the path to the model in 
`detection\_api/runserver.py` to point to the correct path, e.g.
`/app/models/seals-detection-ir-n-large-86.0/fasterrcnn_07281142_0.8598245413189538`.


## Build the docker image
In order to build the docker image, please go to the `src` directory of the arcticseals repo, i.e.
`arcticseals/src`, and execute

```
sudo docker build -t sealapi -f SealDetectionAPI/Dockerfile .
```

If you build the docker image from any other folder, you will receive an error as the relative paths in the Dockerfile
are not correct anymore. The command will copy everything required to run the API to the docker image, including the model. 
Now you can run the image from anywhere on your machine by executing

```
sudo nvidia-docker run -it --ipc=host -p 8081:80 sealapi
```

The flag `--ipc=host` is added for improved performance. The `-it` flag allows to kill the server using the Ctrl+c shortcut. 
Once started, the server will be available at port 8081. You can change this port by replacing 8081 by any number in the
command above. 

If you want to debug the server, you can run 

```
sudo nvidia-docker run -it --ipc=host -p 8081:80 --entrypoint /bin/bash sealapi
```

This will start the docker image, but executes /bin/bash instead of the startup script `/startup.sh`.

## Testing and calling the service

Testing locally, the end point for detection is available at

```
http://localhost:8081/v1/detection_api/detect
```

Please refer to the notebook `demo.ipynb` for an usage example.
