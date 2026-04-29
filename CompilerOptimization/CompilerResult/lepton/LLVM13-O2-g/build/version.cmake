EXECUTE_PROCESS(
     COMMAND /usr/bin/git --git-dir=/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton/.git --work-tree=/home/jimi/PaperExperiment/CompilerOptimization/Target/lepton rev-parse HEAD
     OUTPUT_VARIABLE VERSION
     OUTPUT_STRIP_TRAILING_WHITESPACE
 )
 CONFIGURE_FILE(${SRC} ${DST} @ONLY)
