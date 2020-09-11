#!/bin/bash

#
# recipe to set up local CMSSW area
#
# Notes:
#  - do not use aliases (e.g. cmsrel, cmsenv),
#    so that the recipe can also work in non-interactive shells
#  - do not compile with scram inside this script
#
scramv1 project CMSSW CMSSW_11_1_2_patch3
cd CMSSW_11_1_2_patch3/src
eval `scramv1 runtime -sh`

# updates to use l1t::PFJet with HLT plugins
git cms-merge-topic missirol:devel_hltPhase2_l1tPFJet_1112pa3 -u

# # workaround for PFSimParticle::trackerSurfaceMomentum
# # ref: hatakeyamak:FBaseSimEvent_ProtectAgainstMissingTrackerSurfaceMomentum
git cms-addpkg FastSimulation/Event
git remote add hatakeyamak https://github.com/hatakeyamak/cmssw.git
git fetch hatakeyamak
git diff 0cf67551731c80dc85130e4b8ec73c8f44d53cb0^ 0cf67551731c80dc85130e4b8ec73c8f44d53cb0 | git apply
