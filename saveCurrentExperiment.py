#!/usr/bin/python

import sys 
import os
from datetime import date
from subprocess import call
from subprocess import check_output
import configparser
import definePaths as p 

def makeExperimentName (experimentDate, simulationName, experimentNumber):
    return "{0}_{1}_{2:02d}".format(experimentDate, simulationName, experimentNumber)

def readSimulationName(parameterFile):
    config = configparser.ConfigParser()
    config.read(parameterFile)
    return config['vtk']['name'].strip('"')

if __name__ == '__main__': 
    if ( len(sys.argv) < 2) :
        print 'Usage : ', sys.argv[0], ' <project>'
        sys.exit(1)
    projectName = sys.argv[1]
    print 'saving current experiment in project ', projectName
    print 'extracting experiment name...'    
    paths = p.defineProjectPaths(projectName)
    
    experimentDate=date.today().strftime('%Y%m%d')
    
    experimentFiles = p.defineExperimentFiles()
    experimentFilesInProject = p.prependPathToFiles(paths['projectConfig'],experimentFiles)
    
    simulationName = readSimulationName(experimentFilesInProject['parameters'])
    
    experimentNumber = 0
    experimentName =  makeExperimentName(experimentDate,simulationName,experimentNumber)
    while (os.path.isdir(os.path.join(projectName,experimentName) )):
        experimentNumber  = experimentNumber + 1    
        experimentName    = makeExperimentName(experimentDate,simulationName,experimentNumber)
        
    paths.update( p.defineExperimentPaths(projectName,experimentName) )
    
    os.mkdir(paths['experiment'])
    
    print 'extracting git commit hash...'
    os.chdir(paths['git'])
    status = call(['git','diff','--quiet'])
    if (status != 0) :
        print 'There are uncommitted changes in your git repository'
        print 'Make sure that your working directory is clean, before saving an experiment'
        sys.exit(1)
        
    commithash = check_output(['git','rev-parse','master'])
    commitfile = open(experimentFilesInProject['commit'],'w')
    commitfile.write(commithash)
    commitfile.close()
    
    if (not p.checkIfFilesExist(experimentFilesInProject) ) : 
        sys.exit(1)
    
    print 'copying experiment files...'
    experimentFilesInExperiment = p.prependPathToFiles(paths['experiment'],experimentFiles)
    for key in experimentFilesInProject:
        status = call(['cp', experimentFilesInProject[key],experimentFilesInExperiment[key] ])
        if (status != 0):
            print 'could not copy the ', key , 'file' 
            sys.exit()
            
    print 'successfully saved the experiment to' , paths['experiment']
    
    
    
    
    