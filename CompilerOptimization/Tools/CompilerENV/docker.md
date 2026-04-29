1.进入目录
cd /home/jimi/PaperExperiment/CompilerOptimization/Tools/CompilerENV

2.构建镜像
docker build -t compilerenv:llvm14 .

3.启动容器
docker run -it --name CompilerENV compilerenv:llvm14


4.
docker start CompilerENV

docker exec -it CompilerENV /bin/bash

docker stop CompilerENV
