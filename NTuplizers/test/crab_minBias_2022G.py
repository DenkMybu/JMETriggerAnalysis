import sys
from CRABClient.UserUtilities import config
config = config()

config.section_('General')
config.General.requestName = 'minBias_2022G_ntuples_v4'
config.General.transferLogs = True
config.General.transferOutputs = True


config.section_('JobType')
config.JobType.allowUndistributedCMSSW = True
config.JobType.psetName = '/afs/cern.ch/user/r/rhaberle/CMSSW_12_4_12/src/JMETriggerAnalysis/NTuplizers/test/jmeTriggerNTuple_cfg_puppiPaths_minBias_2022G.py'
#config.JobType.maxJobRuntimeMin = 1500
#config.JobType.maxMemoryMB = 4000
config.JobType.pluginName = 'Analysis'
config.JobType.inputFiles = ['PFHC_Run3Summer21_MC.db', 'puppiJECs.db', 'JESC_Run3Summer21_MC.db', 'JESC_Run3Winter21_V2_MC.db']
#config.JobType.outputFiles = ['out.root']


config.section_('Data')
config.Data.inputDataset = '/MinimumBias/Run2022G-PromptReco-v1/MINIAOD'
config.Data.secondaryInputDataset = '/MinimumBias/Run2022G-v1/RAW'
config.Data.outLFNDirBase = '/store/user/rhaberle/PuppiJets/2022G'
config.Data.splitting = 'LumiBased'
#config.Data.splitting = 'Automatic'
config.Data.unitsPerJob = 10
#config.Data.unitsPerJob = 50
#config.Data.totalUnits = 10000000
config.Data.Publication = False

config.Site.storageSite = 'T2_FR_IPHC'
#config.Debug.extraJDL = ['+CMS_ALLOW_OVERFLOW=False']
