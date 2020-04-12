#!/bin/bash

set -e

if [ ! -d ${JMEANA_BASE} ]; then
  exit 1
fi

inpdir=${JMEANA_BASE}/output_200410_v01/harvesting
outdir=plots_phase2_200410_compareFiles

samples=(
 Phase2HLTTDR_QCD_Pt_15to3000_Flat_14TeV_PU200
 Phase2HLTTDR_VBF_HToInvisible_14TeV_NoPU
 Phase2HLTTDR_VBF_HToInvisible_14TeV_PU200
)

if [ ! -f ${outdir%%/*}.tar.gz ]; then

  for sample in "${samples[@]}"; do

    outd_i=${outdir}/${sample}

    jmePlots_compareFiles.py -u -o ${outd_i} -l ${sample} -e pdf root -i \
     ${inpdir}/hltPhase2_TRKv02/${sample}.root:'TRK v02':2:1:20 \
     ${inpdir}/hltPhase2_TRKv06/${sample}.root:'TRK v06':4:1:24 \

    jmePlots_compareFilesAndObjs.py -u -o ${outd_i}/objs -l ${sample} -e pdf root -i \
     ${inpdir}/hltPhase2_TRKv02/${sample}.root:'TRK v02':2:1:20 \
     ${inpdir}/hltPhase2_TRKv06/${sample}.root:'TRK v06':4:1:24 \

    unset -v outd_i
  done
  unset -v sample

  tar cfz ${outdir%%/*}.tar.gz ${outdir%%/*}
  rm -rf ${outdir%%/*}
fi

unset -v inpdir outdir samples
