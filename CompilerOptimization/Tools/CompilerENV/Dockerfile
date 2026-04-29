# ============================================================
# CompilerENV: Reproducible LLVM14 compilation base
# OS    : Ubuntu 22.04 LTS
# LLVM  : 14.x
# ============================================================

FROM ubuntu:22.04

ARG LLVM_VERSION=14

ENV DEBIAN_FRONTEND=noninteractive
ENV LLVM_VERSION=${LLVM_VERSION}
WORKDIR /work

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    build-essential \
    cmake \
    ninja-build \
    make \
    python3 \
    python3-pip \
    pkg-config \
    clang-${LLVM_VERSION} \
    lld-${LLVM_VERSION} \
    llvm-${LLVM_VERSION} \
    llvm-${LLVM_VERSION}-dev \
    llvm-${LLVM_VERSION}-tools \
    libsnappy-dev \
    libpthread-stubs0-dev \
 && rm -rf /var/lib/apt/lists/*

# 提供无后缀命令，避免脚本因 clang/llvm-link 不存在而失败
RUN ln -sf /usr/bin/clang-${LLVM_VERSION} /usr/local/bin/clang \
 && ln -sf /usr/bin/clang++-${LLVM_VERSION} /usr/local/bin/clang++ \
 && ln -sf /usr/bin/llvm-link-${LLVM_VERSION} /usr/local/bin/llvm-link \
 && ln -sf /usr/bin/llvm-dis-${LLVM_VERSION} /usr/local/bin/llvm-dis \
 && ln -sf /usr/bin/opt-${LLVM_VERSION} /usr/local/bin/opt \
 && ln -sf /usr/bin/llvm-ar-${LLVM_VERSION} /usr/local/bin/llvm-ar \
 && ln -sf /usr/bin/llvm-ranlib-${LLVM_VERSION} /usr/local/bin/llvm-ranlib \
 && ln -sf /usr/bin/llvm-nm-${LLVM_VERSION} /usr/local/bin/llvm-nm \
 && ln -sf /usr/bin/llvm-config-${LLVM_VERSION} /usr/local/bin/llvm-config

# 固定工具链（注意都用 -14 后缀，避免版本漂移）
ENV PATH=/usr/local/bin:/usr/lib/llvm-${LLVM_VERSION}/bin:${PATH} \
    CC=clang \
    CXX=clang++ \
    AR=llvm-ar \
    RANLIB=llvm-ranlib \
    NM=llvm-nm \
    LD=ld.lld-${LLVM_VERSION} \
    LLVM_LINK=llvm-link \
    LLVM_DIS=llvm-dis

# 构建期自检，确保进入容器即有完整编译链
RUN clang --version \
 && clang++ --version \
 && llvm-link --version \
 && llvm-dis --version \
 && cmake --version


WORKDIR /work
ENTRYPOINT ["/bin/bash"]