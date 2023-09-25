#!/bin/bash -e
hltGetConfiguration /dev/CMSSW_12_4_0/GRun \
   --globaltag 124X_dataRun3_v15 \
   --data \
   --unprescale \
   --output minimal \
   --max-events 100 \
   --eras Run3 --l1-emulator uGT --l1 L1Menu_Collisions2022_v1_4_0-d1_xml \
   --path HLTriggerF*,HLT_PFJet*,HLT_PFJetAve*,Status*,MC_* \
   --input /store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/090c78ea-c171-420a-a080-1d12cedac27b.root \
 > tmp_test1.py

edmConfigDump tmp_test1.py > "${CMSSW_BASE}"/src/JMETriggerAnalysis/Common/python/configs/HLT_dev_CMSSW_12_4_0_GRun_era2022D_JetMET_configDump.py
#rm -f tmp.py
