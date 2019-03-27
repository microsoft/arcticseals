FROM mcr.microsoft.com/aiforearth/base-py:1.1

RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         cuda-toolkit-9-2 && \
     rm -rf /var/lib/apt/lists/*

#RUN conda install -n ai4e_py_api numpy pyyaml scipy ipython mkl mkl-include tqdm cupy scikit-image matplotlib && \
#    conda install -n ai4e_py_api -y -c conda-forge visdom fire && \
#    conda install -n ai4e_py_api pytorch torchvision cuda92 -c pytorch && \
#    conda clean -ya
RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api numpy pandas scipy tqdm visdom fire cupy scikit-image matplotlib \
    && conda install -y -c pytorch -n ai4e_py_api pytorch torchvision cuda92 \
    && conda install -y -c kmdouglass -n ai4e_py_api tifffile \
    && conda clean -ya
RUN pip install torchnet

# PIL will be installed with pytorch

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
# Copy your API code
COPY ./SealDetectionAPI/detection_api /app/detection_api/
COPY ./SealDetectionRCNN /app/SealDetectionRCNN
COPY ./SealDetectionAPI/models /app/models
COPY ./SealDetectionAPI/supervisord.conf /etc/supervisord.conf
COPY ./SealDetectionAPI/seals_api_key.txt /app/detection_api/seals_api_key.txt
# startup.sh is a helper script
COPY ./SealDetectionAPI/startup.sh /
RUN chmod +x /startup.sh

COPY ./SealDetectionAPI/LocalForwarder.config /lf/

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY= \
    LOCALAPPDATA=/app_insights_data \
    OCAGENT_TRACE_EXPORTER_ENDPOINT=localhost:55678

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_PyTorch_Example \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=AI4E_PyTorch_Example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 \
    SERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/detection_api

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
ENTRYPOINT [ "/startup.sh" ]
