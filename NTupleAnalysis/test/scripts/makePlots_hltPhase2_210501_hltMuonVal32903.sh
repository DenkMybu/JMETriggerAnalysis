#!/bin/bash

set -e

if [ ! -d ${JMEANA_BASE} ]; then
  printf "%s\n" "environment variable JMEANA_BASE does not contain a valid directory: JMEANA_BASE=${JMEANA_BASE}"
  exit 1
fi

tar_output=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tar) tar_output=1; shift;;
  esac
done

inpdir=${JMEANA_BASE}/output_hltPhase2_210428_hltMuonVal
outdir=plots_hltPhase2_210428_hltMuonVal

samples=(
# Phase2HLTTDR_QCD_PtFlat15to3000_14TeV_NoPU
  Phase2HLTTDR_QCD_PtFlat15to3000_14TeV_PU200
# Phase2HLTTDR_VBF_HToInvisible_14TeV_NoPU
  Phase2HLTTDR_VBF_HToInvisible_14TeV_PU200
)

exts=(
  pdf
  png
# root
)

outdirbase=${outdir%%/*}

if [ ${tar_output} -gt 0 ] && [ -f ${outdirbase}.tar.gz ]; then
  printf "%s\n" ">> target output file already exists: ${outdirbase}.tar.gz"
  exit 1
fi

if [ -d ${outdirbase} ]; then
  printf "%s\n" ">> target output directory already exists: ${outdirbase}"
  exit 1
fi

for sample in "${samples[@]}"; do

  outd_i=${outdir}/${sample}

  opts_i="-m 'NoSelection/*"
#  if   [[ ${sample} == *"QCD_"* ]]; then opts_i="-m 'NoSel*/*JetsCorr*' 'NoSel*/*MET_*' 'NoSel*/*/offline*MET*_pt' -s '*MET*GEN*'"
#  elif [[ ${sample} == *"HToInv"* ]]; then opts_i="-m 'NoSel*/*MET_*' 'NoSel*/*/offline*METs*_pt'"
#  fi

  jmePlots.py -k jme_compare ${opts_i} \
    -o ${outd_i}/baseline_vs_75e33 -l ${sample} -e ${exts[*]} -i \
    ${inpdir}/harvesting/HLT_TRKv06p1_TICL/${sample}.root:'TDR':1:1:20 \
    ${inpdir}/harvesting/HLT_75e33/${sample}.root:'cms-sw#32903':2:1:24

  unset outd_i opts_i
done
unset sample

if [ ${tar_output} -gt 0 ] && [ -d ${outdirbase} ]; then
  tar cfz ${outdirbase}.tar.gz ${outdirbase}
  rm -rf ${outdirbase}
fi

unset inpdir outdir samples exts outdirbase tar_output
