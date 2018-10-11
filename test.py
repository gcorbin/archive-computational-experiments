import sys 
import os
import experimentarchiver

projectName = 'kershaw-ap'
command = 'mpirun -n 4 ./kershaw-ap'.split(' ')
archiver = experimentarchiver.ExperimentArchiver(projectName)
archiver.run_and_record(command)