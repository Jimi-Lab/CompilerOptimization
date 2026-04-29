#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/source/smack" && pwd)"
IMAGE_TAG="${1:-smackers/smack-llvm13-useable:latest}"
BASE_IMAGE="${BASE_IMAGE:-smackers/smack:latest-full}"
CTX="$(mktemp -d)"

cleanup() {
  rm -rf "${CTX}"
}
trap cleanup EXIT

mkdir -p "${CTX}/lib/smack" "${CTX}/lib/utils" "${CTX}/include/smack"
cp "${ROOT}/lib/smack/SmackInstGenerator.cpp" "${CTX}/lib/smack/SmackInstGenerator.cpp"
cp "${ROOT}/lib/utils/SimplifyExtractValue.cpp" "${CTX}/lib/utils/SimplifyExtractValue.cpp"
cp "${ROOT}/include/smack/SmackInstGenerator.h" "${CTX}/include/smack/SmackInstGenerator.h"

cat > "${CTX}/Dockerfile" <<EOF
FROM ${BASE_IMAGE}

COPY --chown=user:user lib/smack/SmackInstGenerator.cpp /home/user/smack/lib/smack/SmackInstGenerator.cpp
COPY --chown=user:user lib/utils/SimplifyExtractValue.cpp /home/user/smack/lib/utils/SimplifyExtractValue.cpp
COPY --chown=user:user include/smack/SmackInstGenerator.h /home/user/smack/include/smack/SmackInstGenerator.h

USER root
RUN sed -i '/\\/useArrayTheory/d' /home/user/smack/share/smack/top.py /usr/local/share/smack/top.py
RUN python3 -c "from pathlib import Path; old=\"f.write(error.decode('utf-8'))\"; new=\"f.write(error.decode('utf-8') if isinstance(error, bytes) else error)\"; [p.write_text(p.read_text().replace(old, new)) for p in [Path('/home/user/smack/share/smack/svcomp/utils.py'), Path('/usr/local/share/smack/svcomp/utils.py')]]"

USER user
RUN cmake --build /home/user/smack/build -j2 --target llvm2bpl

USER root
RUN cp /home/user/smack/build/llvm2bpl /usr/local/bin/llvm2bpl
USER user
EOF

docker build -t "${IMAGE_TAG}" "${CTX}"
echo "Built ${IMAGE_TAG}"
