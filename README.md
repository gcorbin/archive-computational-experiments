# archive-computational-experiments
A python tool to archive and reproduce computational experiments.

To reproduce a computational experiment, 
ideally the following prerequisites have to be restored exactly:
- source code
- execution command with all arguments
- parameters (small files that could contain known physical quantities or program options, *.ini files)
- input data (large (binary) files)
- environment (os version and version of all external packages, hardware)

This tool helps to archive and reproduce experiments automatically:

Archiving:
- code: store the git commit hash
- command: store the calling command
- parameters: copy the files
- input data: store a hash for every file
- output data: copy the output (optional)
- environment: **not planned**, as it is beyond the scope of this project

Reproducing:
- check out the version of the code corresponding to the stored commmit hash
- copy the parameter files back
- ensure that the input data files are the same by comparing hashes
- build the executable (if a compiled language is used)
- run the stored command
- compare stored outputs with computed outputs (optional) *not implemented yet*

The following assumptions are made about the experiment setup:
- the code is versioned with git
- for compiled languages, there is a build system (e.g. cmake) in place, such that the entire project can be built with one command
- large input data is archived separately 
