1.进入目录
cd /home/jimi/PaperExperiment/CompilerOptimization/Tools/ikos

2.清理旧容器/旧镜像（避免继续用旧版本）
docker rm -f ikos 2>/dev/null || true
docker rmi ikos:3.5-llvm14 2>/dev/null || true

3.重建镜像（必须 --no-cache）
docker build --no-cache -t ikos:3.5-llvm14 .

4.启动容器
docker run -it --name ikos -v /home/jimi/PaperExperiment:/work/PaperExperiment ikos:3.5-llvm14

5.容器内验证（必须通过）
which ikos
python3 -c "import ikos, ikos.analyzer; print('IKOS Python OK')"
ikos --help | head -n 20

6.重复进入容器
docker start ikos
docker exec -it ikos /bin/bash
docker stop ikos