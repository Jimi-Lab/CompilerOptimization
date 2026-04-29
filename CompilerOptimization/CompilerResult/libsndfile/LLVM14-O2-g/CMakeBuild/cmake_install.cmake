# Install script for directory: /home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/llvm-objdump-14")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-info" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-info")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-info"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-info")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-info" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-info")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-info")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-play" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-play")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-play"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-play")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-play" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-play")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-play")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-convert" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-convert")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-convert"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-convert")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-convert" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-convert")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-convert")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-cmp" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-cmp")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-cmp"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-cmp")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-cmp" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-cmp")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-cmp")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-set" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-set")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-set"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-metadata-set")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-set" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-set")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-set")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-get" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-get")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-get"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-metadata-get")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-get" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-get")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-metadata-get")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-interleave" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-interleave")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-interleave"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-interleave")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-interleave" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-interleave")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-interleave")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-deinterleave" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-deinterleave")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-deinterleave"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-deinterleave")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-deinterleave" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-deinterleave")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-deinterleave")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-concat" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-concat")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-concat"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-concat")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-concat" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-concat")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-concat")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-salvage" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-salvage")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-salvage"
         RPATH "")
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/bin" TYPE EXECUTABLE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile-salvage")
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-salvage" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-salvage")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/llvm-strip-14" "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/bin/sndfile-salvage")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/libsndfile.a")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/include/sndfile.h"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/include/sndfile.hh"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile/SndFileTargets.cmake")
    file(DIFFERENT EXPORT_FILE_CHANGED FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile/SndFileTargets.cmake"
         "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/CMakeFiles/Export/lib/cmake/SndFile/SndFileTargets.cmake")
    if(EXPORT_FILE_CHANGED)
      file(GLOB OLD_CONFIG_FILES "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile/SndFileTargets-*.cmake")
      if(OLD_CONFIG_FILES)
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile/SndFileTargets.cmake\" will be replaced.  Removing files [${OLD_CONFIG_FILES}].")
        file(REMOVE ${OLD_CONFIG_FILES})
      endif()
    endif()
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile" TYPE FILE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/CMakeFiles/Export/lib/cmake/SndFile/SndFileTargets.cmake")
  if("${CMAKE_INSTALL_CONFIG_NAME}" MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile" TYPE FILE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/CMakeFiles/Export/lib/cmake/SndFile/SndFileTargets-debug.cmake")
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile" TYPE FILE RENAME "SndFileConfig.cmake" FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/SndFileConfig2.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/SndFile" TYPE FILE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/SndFileConfigVersion.cmake")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/man/man1" TYPE FILE FILES
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-info.1"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-play.1"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-convert.1"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-cmp.1"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-metadata-get.1"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-concat.1"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-interleave.1"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-salvage.1"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/man/man1" TYPE FILE RENAME "sndfile-metadata-set.1" FILES "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-metadata-get.1")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/man/man1" TYPE FILE RENAME "sndfile-deinterleave.1" FILES "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/man/sndfile-interleave.1")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/doc/libsndfile" TYPE FILE FILES
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/index.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/libsndfile.jpg"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/libsndfile.css"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/print.css"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/api.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/command.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/bugs.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/formats.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/sndfile_info.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/new_file_type_howto.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/win32.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/FAQ.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/lists.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/embedded_files.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/octave.md"
    "/home/jimi/PaperExperiment/CompilerOptimization/Target/libsndfile/docs/tutorial.md"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/pkgconfig" TYPE FILE FILES "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/sndfile.pc")
endif()

if(CMAKE_INSTALL_COMPONENT)
  set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
file(WRITE "/home/jimi/PaperExperiment/CompilerOptimization/CompilerResult/libsndfile/LLVM14-O2-g/CMakeBuild/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
