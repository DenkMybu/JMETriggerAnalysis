#!/bin/bash -e
hltGetConfiguration /dev/CMSSW_12_4_0/GRun \
   --globaltag 124X_dataRun3_v15 \
   --data \
   --unprescale \
   --output minimal \
   --max-events 100 \
   --eras Run3 --l1-emulator uGT --l1 L1Menu_Collisions2022_v1_4_0-d1_xml \
   --path HLTriggerF*,Status*,MC_* \
   --input /store/data/Run2022D/MinimumBias/RAW/v1/000/357/503/00000/45227074-eca3-492b-b55b-c9da0be23ef5.root \
 > tmp_test_minBias.py

edmConfigDump tmp_test_minBias.py > "${CMSSW_BASE}"/src/JMETriggerAnalysis/Common/python/configs/HLT_dev_CMSSW_12_4_0_GRun_era2022D_MinnBias_configDump.py
#rm -f tmp.py
