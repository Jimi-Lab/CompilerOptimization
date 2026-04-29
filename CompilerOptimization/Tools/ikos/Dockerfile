# ============================================================
# IKOS Static Analysis Environment (Paper-Reproducible)
# OS    : Ubuntu 22.04 LTS
# LLVM  : 14.x
# IKOS  : v3.5
# Usage : Analyze LLVM bitcode (*.bc)
# ============================================================

FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /opt

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    cmake \
    git \
    python3 \
    python3-venv \
    python3-pip \
    python3-pygments \
    python3-distutils \
    libgmp-dev \
    libboost-dev \
    libboost-filesystem-dev \
    libboost-thread-dev \
    libboost-test-dev \
    libsqlite3-dev \
    libz-dev \
    libedit-dev \
    libtbb-dev \
    llvm-14 \
    llvm-14-dev \
    llvm-14-tools \
    clang-14 \
    vim \
    file \
 && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch v3.5 https://github.com/NASA-SW-VnV/ikos.git /opt/ikos-src \
 && cd /opt/ikos-src \
 && mkdir -p build \
 && cd build \
 && CC=clang-14 CXX=clang++-14 cmake \
      -DCMAKE_INSTALL_PREFIX=/opt/ikos \
      -DCMAKE_BUILD_TYPE=Release \
      -DLLVM_CONFIG_EXECUTABLE=/usr/lib/llvm-14/bin/llvm-config \
      .. \
 && make -j"$(nproc)" \
 && make install \
 && mkdir -p /opt/ikos/lib/python3/dist-packages/ikos \
 && cp -a /opt/ikos-src/analyzer/python/ikos/. /opt/ikos/lib/python3/dist-packages/ikos/ \
 && cp -a /opt/ikos-src/build/analyzer/python/ikos/settings /opt/ikos/lib/python3/dist-packages/ikos/ \
 && mkdir -p /opt/ikos/share/ikos \
 && ln -sfn /opt/ikos/lib/python3/dist-packages /opt/ikos/share/ikos/python

ENV IKOS_HOME=/opt/ikos
ENV PATH="${IKOS_HOME}/bin:/usr/lib/llvm-14/bin:${PATH}"
ENV PYTHONPATH="${IKOS_HOME}/lib/python3/dist-packages"

WORKDIR /work
ENTRYPOINT ["/bin/bash"]
