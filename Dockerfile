FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_BREAK_SYSTEM_PACKAGES=1
RUN apt-get update && \
    apt-get install -y \
        git \
        ca-certificates \
        python3 \
        python3-pip \
        libgl1 \
        libglib2.0-0 \
        wget
RUN git clone https://github.com/xinntao/Real-ESRGAN.git
RUN pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
RUN pip install \
        "numpy<2" \
        basicsr \
        facexlib \
        gfpgan \
        opencv-python-headless \
        Pillow \
        tqdm \
        boto3 \
      && \
    pip cache purge && \
    mkdir /opt/input /opt/artifact && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /Real-ESRGAN

RUN python3 setup.py develop
RUN wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights

COPY runner.py /Real-ESRGAN/
COPY docker-entrypoint*.sh /
RUN chmod +x /docker-entrypoint*.sh /

WORKDIR /
CMD ["/bin/bash", "/docker-entrypoint.sh"]