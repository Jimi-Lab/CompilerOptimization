#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/ikos" && pwd)"
IMAGE_TAG="${1:-ikos:3.5-llvm14-o2g}"
BASE_IMAGE="ikos:3.5-llvm14"
CTX="$(mktemp -d)"

cleanup() {
  rm -rf "${CTX}"
}
trap cleanup EXIT

mkdir -p "${CTX}/frontend/llvm/src/import" "${CTX}/frontend/llvm/src"
cp "${ROOT}/frontend/llvm/src/import/function.cpp" \
  "${CTX}/frontend/llvm/src/import/function.cpp"
cp "${ROOT}/frontend/llvm/src/import/function.hpp" \
  "${CTX}/frontend/llvm/src/import/function.hpp"
cp "${ROOT}/frontend/llvm/src/ikos_pp.cpp" \
  "${CTX}/frontend/llvm/src/ikos_pp.cpp"

cat > "${CTX}/Dockerfile" <<EOF
FROM ${BASE_IMAGE}

COPY frontend/llvm/src/import/function.cpp /opt/ikos-src/frontend/llvm/src/import/function.cpp
COPY frontend/llvm/src/import/function.hpp /opt/ikos-src/frontend/llvm/src/import/function.hpp
COPY frontend/llvm/src/ikos_pp.cpp /opt/ikos-src/frontend/llvm/src/ikos_pp.cpp

RUN apt-get update && apt-get install -y --no-install-recommends python3-venv \
 && rm -rf /var/lib/apt/lists/*

RUN cmake --build /opt/ikos-src/build -j2 --target install

ENV IKOS_HOME=/opt/ikos
ENV PATH="\${IKOS_HOME}/bin:/usr/lib/llvm-14/bin:\${PATH}"
ENV PYTHONPATH="\${IKOS_HOME}/lib/python3/dist-packages"

WORKDIR /work
ENTRYPOINT ["/bin/bash"]
EOF

docker build -t "${IMAGE_TAG}" "${CTX}"
echo "Built ${IMAGE_TAG}"
