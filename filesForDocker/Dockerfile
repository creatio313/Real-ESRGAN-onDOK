FROM nvidia/cuda:12.8.1-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    PIP_BREAK_SYSTEM_PACKAGES=1

# 必要ツールのインストール。setup.py向けにpython3-setuptoolsを取得
RUN apt-get update && \
    apt-get install -y --no-install-recommends\
        git \
        ca-certificates \
        python3 \
        python3-pip \
        python3-setuptools \
        libgl1 \
        libglib2.0-0 \
        wget && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/xinntao/Real-ESRGAN.git

RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

# Real-ESRGAN互換のため、numpyをバージョンダウン
RUN pip install \
        basicsr \
        boto3 \
        facexlib \
        gfpgan \
        "numpy<2" \
        opencv-python-headless \
        Pillow \
        tqdm \
      && \
    pip cache purge && \
    mkdir /opt/input /opt/artifact

WORKDIR /Real-ESRGAN

RUN python3 setup.py develop

# 最新PyTorchで動かすためのパッチあて
RUN sed -i 's/from torchvision.transforms.functional_tensor import rgb_to_grayscale/from torchvision.transforms.functional import rgb_to_grayscale/' /usr/local/lib/python3.12/dist-packages/basicsr/data/degradations.py || true

RUN wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P weights

COPY inference_realesrgan.py /Real-ESRGAN/inference_realesrgan.py
COPY runner*.py /Real-ESRGAN/
COPY docker-entrypoint*.sh /
RUN chmod +x /docker-entrypoint.sh

WORKDIR /
ENTRYPOINT [ "/docker-entrypoint.sh" ]