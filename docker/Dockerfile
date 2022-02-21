FROM condaforge/mambaforge:4.10.3-6 as build

ARG DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,id=apt-build,target=/var/cache/apt \
    apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        git && \
    rm -rf /var/lib/apt/lists/*

# Install conda requirements
COPY ai-dataset-SIGNATURE_SUPERDATABASE/conda.yaml conda.yaml

RUN --mount=type=cache,target=/opt/conda/pkgs \
    sed -i -e 's/SIGNATURE_SUPERDATABASE/base/g' conda.yaml && \
    mamba env update --name base --file conda.yaml && mamba clean -ya

ENV PATH /opt/conda/bin:$PATH

ENTRYPOINT [ "/bin/bash" ]
