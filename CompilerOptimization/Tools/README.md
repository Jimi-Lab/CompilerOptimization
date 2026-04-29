# Tools

This directory contains local analyzer/tool environments. The paper GitHub
repository should track local wrappers, Dockerfiles, build notes, run scripts,
and small documentation, but should not vendor full upstream tool source trees
or downloaded binary archives.

If a third-party tool source file was locally modified, prefer one of these
forms:

- a small patch under a tracked `patches/` directory;
- a forked upstream repository referenced by URL and commit in
  `TOOLS_MANIFEST.md`;
- a Dockerfile/build script that applies the patch reproducibly.

Full tool source trees and image artifacts should be preserved in the external
workspace snapshot.
