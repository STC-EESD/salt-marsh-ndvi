#!/bin/bash

currentDIR=`pwd`
   codeDIR=${currentDIR}/code
 outputDIR=${currentDIR//github/gittmp}/output

parentDIR=`dirname ${currentDIR}`
  dataDIR=${parentDIR}/000-data

if [ ! -d ${outputDIR} ]; then
    mkdir -p ${outputDIR}
fi

cp -r ${codeDIR} ${outputDIR}
cp    $0         ${outputDIR}/code

##################################################
source ${HOME}/.gee_environment_variables
if [[ "${OSTYPE}" =~ .*"linux".* ]]; then
  # cp ${HOME}/.gee_environment_variables ${outputDIR}/code/gee_environment_variables.txt
  pythonBinDIR=${GEE_ENV_DIR}/bin
  RBinDIR=${pythonBinDIR}
else
  pythonBinDIR=`which python`
  pythonBinDIR=${pythonBinDIR//\/python/}
  RBinDIR=`which R`
  RBinDIR=${RBinDIR//\/R/}
fi

##################################################
googleDriveFolder=earthengine/elijah
# Defining the year(s) for analysis (comma seperated string, with no whitespace ex: "2019,2021" )
years="2019,2021"

myPythonScript=${codeDIR}/main-earthengine.py
stdoutFile=${outputDIR}/stdout.py.`basename ${myPythonScript} .py`
stderrFile=${outputDIR}/stderr.py.`basename ${myPythonScript} .py`
${pythonBinDIR}/python ${myPythonScript} ${dataDIR} ${codeDIR} ${outputDIR} ${googleDriveFolder} ${years} > ${stdoutFile} 2> ${stderrFile}

##################################################
exit

