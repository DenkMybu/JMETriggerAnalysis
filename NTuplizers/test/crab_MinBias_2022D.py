import sys

from CRABClient.UserUtilities import config
config = config()

config.section_('General')
config.General.requestName = 'MinBias_2022D_raw_v5'
config.General.transferLogs = True
config.General.transferOutputs = True


config.section_('JobType')
config.JobType.allowUndistributedCMSSW = True
config.JobType.psetName = '/afs/cern.ch/user/r/rhaberle/CMSSW_12_4_12/src/JMETriggerAnalysis/NTuplizers/test/jmeTriggerNTuple_cfg_puppiPaths_minBias.py'

config.JobType.maxJobRuntimeMin = 1500
config.JobType.maxMemoryMB = 4000
config.JobType.pluginName = 'Analysis'
config.JobType.inputFiles = ['PFHC_Run3Summer21_MC.db', 'puppiJECs.db', 'JESC_Run3Summer21_MC.db', 'JESC_Run3Winter21_V2_MC.db']
config.JobType.outputFiles = ['out.root']


config.section_('Data')
config.Data.inputDataset = '/MinimumBias/Run2022D-v1/RAW'
config.Data.outLFNDirBase = '/store/user/rhaberle/PuppiTests/data'
config.Data.splitting = 'LumiBased'
config.Data.unitsPerJob = 50


config.Site.storageSite = 'T2_FR_IPHC'
config.Debug.extraJDL = ['+CMS_ALLOW_OVERFLOW=False']
