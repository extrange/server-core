# MinerU 4 API server image, based on the official docker/global/Dockerfile:
# https://github.com/opendatalab/MinerU/blob/master/docker/global/Dockerfile
#
# The vLLM base image covers Volta, Turing, Ampere, Ada Lovelace, Hopper and
# Blackwell GPUs (7.0 <= compute capability <= 12.1). The default image uses
# CUDA 13.0; switch to the cu129 image below when the host driver requires it.
FROM vllm/vllm-openai:v0.21.0
# FROM vllm/vllm-openai:v0.21.0-cu129

# libgl is required by OpenCV, which MinerU uses for document rendering.
RUN apt-get update && \
    apt-get install -y \
        libgl1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install MinerU 4 with Torch; reuse the vLLM already bundled in the base image.
RUN python3 -m pip install -U 'mineru[torch]>=4.0,<5' --break-system-packages && \
    python3 -m pip cache purge

# Keep build-time model downloads and runtime selection aligned, including
# builds on a machine without a GPU.
ENV MINERU_MODEL_SMALL_BACKEND=torch \
    MINERU_MODEL_VLM_ENGINE=vllm

# Download the Torch bundle and original VLM weights so the container can run
# offline with MINERU_MODEL_SOURCE=local.
RUN /bin/bash -c "mineru-kit models download --tier standard --small-backend torch --vlm-engine vllm -s huggingface"

# Allow the image to run a command directly, defaulting to local model files.
ENTRYPOINT ["/bin/bash", "-c", "export MINERU_MODEL_SOURCE=local && exec \"$@\"", "--"]
