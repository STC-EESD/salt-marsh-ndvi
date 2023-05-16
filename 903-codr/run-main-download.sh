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

##################################################
myRscript=${codeDIR}/main-download.R
stdoutFile=${outputDIR}/stdout.R.`basename ${myRscript} .R`
stderrFile=${outputDIR}/stderr.R.`basename ${myRscript} .R`
${RBinDIR}/R --no-save --args ${dataDIR} ${codeDIR} ${outputDIR} ${googleDriveFolder} < ${myRscript} > ${stdoutFile} 2> ${stderrFile}

##################################################
exit