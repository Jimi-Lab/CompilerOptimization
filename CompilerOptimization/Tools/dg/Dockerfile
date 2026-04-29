FROM docker.io/ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    wget \
    git \
    build-essential \
    make \
    cmake \
    ninja-build \
    pkg-config \
    python3 \
    python3-pip \
    clang-14 \
    lld-14 \
    llvm-14 \
    llvm-14-dev \
    llvm-14-tools \
    zlib1g-dev \
    autoconf \
    automake \
    libtool \
    bison \
    flex \
    libssl-dev \
    libpcre2-dev \
    libevent-dev \
    libxml2-dev \
    libbz2-dev \
    liblz4-dev \
    libzstd-dev \
    libsnappy-dev \
    libreadline-dev \
    libncurses-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

ENV CC=clang-14
ENV CXX=clang++-14
ENV PATH=/usr/lib/llvm-14/bin:$PATH
ENV LLVM_CONFIG=llvm-config-14

FROM base AS build

ARG DG_RUN_CHECK=0

WORKDIR /opt
COPY CompilerOptimization/Tools/dg/src/dg /opt/dg-src

RUN cmake -S /opt/dg-src -G Ninja -B /opt/dg-build \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=/opt/dg \
    -DCMAKE_C_COMPILER=clang-14 \
    -DCMAKE_CXX_COMPILER=clang++-14 \
    -DLLVM_DIR=/usr/lib/llvm-14/lib/cmake/llvm \
    -DENABLE_FUZZING=OFF

RUN cmake --build /opt/dg-build -j"$(nproc)"
RUN if [ "$DG_RUN_CHECK" = "1" ]; then cmake --build /opt/dg-build --target check; else echo "Skipping DG ctest during image build"; fi
RUN cmake --install /opt/dg-build

FROM base AS release

COPY --from=build /opt/dg /opt/dg
COPY --from=build /opt/dg-build/tools/llvm-* /opt/dg/bin/

ENV PATH=/opt/dg/bin:/opt/dg/tools:$PATH
ENV LD_LIBRARY_PATH=/opt/dg/lib

RUN llvm-config-14 --version
RUN clang-14 --version | head -n 1
RUN command -v llvm-slicer
RUN command -v llvm-pta-dump
RUN command -v llvm-dda-dump
RUN command -v llvm-cda-dump
RUN command -v llvm-cg-dump
RUN command -v llvm-dg-dump

WORKDIR /work
CMD ["/bin/bash"]
