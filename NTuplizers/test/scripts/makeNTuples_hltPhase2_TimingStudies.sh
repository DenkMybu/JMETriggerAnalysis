#!/bin/bash -e

if [ $# -ne 1 ]; then
  printf "\n%s\n\n" ">> argument missing - specify path to output directory"
  exit 1
fi

NEVT=1000
ODIR=${1}

if [ -d ${ODIR} ]; then
  printf "%s\n" "output directory already exists: ${ODIR}"
  exit 1
fi

declare -A samplesMap

# VBF H(125)->Invisible
#samplesMap["Phase2HLTTDR_VBF_HToInvisible_14TeV_NoPU"]="/VBF_HToInvisible_M125_TuneCUETP8M1_14TeV_powheg_pythia8/Phase2HLTTDRSummer20ReRECOMiniAOD-NoPU_111X_mcRun4_realistic_T15_v1-v1/FEVT"
#samplesMap["Phase2HLTTDR_VBF_HToInvisible_14TeV_PU140"]="/VBF_HToInvisible_M125_TuneCUETP8M1_14TeV_powheg_pythia8/Phase2HLTTDRSummer20ReRECOMiniAOD-PU140_111X_mcRun4_realistic_T15_v1_ext1-v2/FEVT"
samplesMap["Phase2HLTTDR_VBF_HToInvisible_14TeV_PU200"]="/VBF_HToInvisible_M125_14TeV_powheg_pythia8_TuneCP5/Phase2HLTTDRSummer20ReRECOMiniAOD-PU200_111X_mcRun4_realistic_T15_v1-v1/FEVT"

recoKeys=(
  HLT_75e33_TrkPtX1p00_HGCEnX1p00
)

# additional options for bdriver
opts=""

for recoKey in "${recoKeys[@]}"; do
  python ${CMSSW_BASE}/src/JMETriggerAnalysis/NTuplizers/test/jmeTriggerNTuple_cfg.py dumpPython=.tmp_${recoKey}_cfg.py numThreads=1 reco=${recoKey} 

  for sampleKey in ${!samplesMap[@]}; do
    sampleName=${samplesMap[${sampleKey}]}

    # number of events per sample
    numEvents=${NEVT}
    if [[ ${sampleKey} == *MinBias* ]]; then
      numEvents=2000000
    fi
    
    # Note: You can automatically run the jobs after creating them by using --submit option of bdriver
    bdriver -c .tmp_${recoKey}_cfg.py --customize-cfg -m ${numEvents} -n 1000 --cpus 1 --memory 2G --time 01:00:00 ${opts} --batch-system htc \
      -d ${sampleName} -p 0 -o ${ODIR}/${recoKey}/${sampleKey} \
      --final-output /eos/user/t/tchatzis/MTDtiming_samples/${recoKey}/${sampleKey} \
      --customise-commands \
       '# output [TFileService]' \
       "if hasattr(process, 'TFileService'):" \
       '  process.TFileService.fileName = opts.output' 
     
    unset numEvents sampleName
  done
  unset sampleKey

  rm -f .tmp_${recoKey}_cfg.py
done
unset recoKey opts recoKeys samplesMap NEVT ODIR
