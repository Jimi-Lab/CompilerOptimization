# 1) 拉取镜像
docker pull svftools/svf:latest

# 2) 进入容器（挂载 leveldb 源码目录 + 结果目录）

docker run -it \
  --name svf \
  -v /home/jimi/PaperExperiment/CompilerOptimization/Target/leveldb:/work/leveldb \
  -v /home/jimi/PaperExperiment/CompilerOptimization/Result/leveldb/SVF:/work/result \
  -w /work/leveldb \
  svftools/svf:latest /bin/bash


# 3) 反复进入svf docker

docker start svf

docker exec -it svf /bin/bash

docker stop svf