import os
import fnmatch

from CondCore.CondDB.CondDB_cfi import CondDB as _CondDB

###
### command-line arguments
###
import FWCore.ParameterSet.VarParsing as vpo
opts = vpo.VarParsing('analysis')

# options to control puppi tuning at different regions
opts.register('skipEvents', 0,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.int,
              'number of events to be skipped')

opts.register('dumpPython', 'config.py',
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.string,
              'path to python file with content of cms.Process')

opts.register('numThreads', 1,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.int,
              'number of threads')

opts.register('numStreams', 0,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.int,
              'number of streams')

opts.register('lumis', None,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.string,
              'path to .json with list of luminosity sections')

opts.register('wantSummary', False,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.bool,
              'show cmsRun summary at job completion')

opts.register('globalTag', None,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.string,
              'argument of process.GlobalTag.globaltag')

opts.register('reco', 'HLT_Run3TRK',
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.string,
              'keyword to define HLT reconstruction')

opts.register('output', 'out_minBias.root',
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.string,
              'path to output ROOT file')

opts.register('keepPFPuppi', False,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.bool,
              'keep full collection of PFlow and PFPuppi candidates')
opts.register('useMixedTrk', False,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.bool,
              'use  full + pixel tracks in PF')
opts.register('verbosity', 1,
              vpo.VarParsing.multiplicity.singleton,
              vpo.VarParsing.varType.int,
              'level of output verbosity')

#opts.register('printSummaries', False,
#              vpo.VarParsing.multiplicity.singleton,
#              vpo.VarParsing.varType.bool,
#              'show summaries from HLT services')

opts.parseArguments()

###
### HLT configuration
###
if opts.reco == 'HLT_oldJECs':
  from JMETriggerAnalysis.Common.configs.HLT_dev_CMSSW_12_4_0_GRun_configDump import cms, process
  update_jmeCalibs = False

elif opts.reco == 'HLT_Run3TRK':
  #from JMETriggerAnalysis.Common.configs.HLT_dev_CMSSW_12_4_0_GRun_postEE_configDump import cms, process

  #for DATA 2022 D
  from JMETriggerAnalysis.Common.configs.HLT_dev_CMSSW_12_4_0_GRun_era2022D_MinnBias_configDump import cms, process

  #for JetMET 2022 D
  #from JMETriggerAnalysis.Common.configs.HLT_dev_CMSSW_12_4_0_GRun_era2022D_JetMET_configDump import cms, process

  #for MC with PU mixing
  #from JMETriggerAnalysis.Common.configs.HLT_dev_CMSSW_12_4_0_GRun_postEE_configDump_mixPU import cms, process
  #update_jmeCalibs = True

  #for DATA put False
  update_jmeCalibs = False  

else:
  raise RuntimeError('keyword "reco = '+opts.reco+'" not recognised')

# remove cms.OutputModule objects from HLT config-dump
for _modname in process.outputModules_():
    _mod = getattr(process, _modname)
    if type(_mod) == cms.OutputModule:
       process.__delattr__(_modname)
       if opts.verbosity > 0:
          print('> removed cms.OutputModule:', _modname)

# remove cms.EndPath objects from HLT config-dump
for _modname in process.endpaths_():
    _mod = getattr(process, _modname)
    if type(_mod) == cms.EndPath:
       process.__delattr__(_modname)
       if opts.verbosity > 0:
          print('> removed cms.EndPath:', _modname)

# remove selected cms.Path objects from HLT config-dump
print('-'*108)
print('{:<99} | {:<4} |'.format('cms.Path', 'keep'))
print('-'*108)

# list of patterns to determine paths to keep
keepPaths = [
  'MC_*Jets*',
  'MC_*MET*',
  'MC_*AK8Calo*',
  'HLT_PFJet*_v*',
  'HLT_AK4PFJet*_v*',
  'HLT_AK8PFJet*_v*',
  'HLT_PFHT*_v*',
  'HLT_PFMET*_PFMHT*_v*',
]



vetoPaths = [
  'HLT_*ForPPRef_v*',
  'AlCa_*'
]

# list of paths that are kept
listOfPaths = []

for _modname in sorted(process.paths_()):
    _keepPath = False
    for _tmpPatt in keepPaths:
      _keepPath = fnmatch.fnmatch(_modname, _tmpPatt)
      if _keepPath: break

    if _keepPath:
      for _tmpPatt in vetoPaths:
        if fnmatch.fnmatch(_modname, _tmpPatt):
          _keepPath = False
          break

    if _keepPath:
      print('{:<99} | {:<4} |'.format(_modname, '+'))
      listOfPaths.append(_modname)
      continue
    _mod = getattr(process, _modname)
    if type(_mod) == cms.Path:
      process.__delattr__(_modname)
      print('{:<99} | {:<4} |'.format(_modname, ''))
print('-'*108)

# remove FastTimerService
if hasattr(process, 'FastTimerService'):
  del process.FastTimerService

# remove MessageLogger
#if hasattr(process, 'MessageLogger'):
#  del process.MessageLogger

###
### customisations
###

## customised JME collections
from JMETriggerAnalysis.Common.customise_hlt_puppi import *
#process = addPaths_MC_JMECalo(process)
#process = addPaths_MC_JMEPFCluster(process)
#process = addPaths_MC_JMEPF(process)
#process = addPaths_MC_JMEPFCHS(process)
#[process,listOfPaths] = addPaths_MC_JMEPFPuppi(process, listOfPaths)







if update_jmeCalibs:
  ## ES modules for PF-Hadron Calibrations
  process.pfhcESSource = cms.ESSource('PoolDBESSource',
    #_CondDB.clone(connect = 'sqlite_file:PFHC_Run3Winter21_HLT_V3.db'),
    _CondDB.clone(connect = 'sqlite_file:PFHC_Run3Summer21_MC.db'),
    toGet = cms.VPSet(
      cms.PSet(
        record = cms.string('PFCalibrationRcd'),
        tag = cms.string('PFCalibration_CMSSW_12_4_0_pre3_HLT_112X_mcRun3_2022'),
        label = cms.untracked.string('HLT'),
      ),
    ),
  )
  process.pfhcESPrefer = cms.ESPrefer('PoolDBESSource', 'pfhcESSource')
  #process.hltParticleFlow.calibrationsLabel = '' # standard label for Offline-PFHC in GT

  ## ES modules for HLT JECs
  process.jescESSource = cms.ESSource('PoolDBESSource',
    #_CondDB.clone(connect = 'sqlite_file:JESC_Run3Winter21_V2_MC.db'),
    _CondDB.clone(connect = 'sqlite_file:JESC_Run3Summer21_MC.db'),
    toGet = cms.VPSet(
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK4CaloHLT'),
        label = cms.untracked.string('AK4CaloHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK4PFClusterHLT'),
        label = cms.untracked.string('AK4PFClusterHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK4PFHLT'),
        label = cms.untracked.string('AK4PFHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK4PFHLT'),#!!
        label = cms.untracked.string('AK4PFchsHLT'),
      ),
      #cms.PSet(
      #  record = cms.string('JetCorrectionsRecord'),
      #  tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK4PFPuppiHLT'),
      #  label = cms.untracked.string('AK4PFPuppiHLT'),
      #),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK8CaloHLT'),
        label = cms.untracked.string('AK8CaloHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK8PFClusterHLT'),
        label = cms.untracked.string('AK8PFClusterHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK8PFHLT'),
        label = cms.untracked.string('AK8PFHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK8PFHLT'),#!!
        label = cms.untracked.string('AK8PFchsHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK8PFPuppiHLT'),
        label = cms.untracked.string('AK8PFPuppiHLT'),
      ),
    ),
  )
  process.jescESPrefer = cms.ESPrefer('PoolDBESSource', 'jescESSource')

  # -- adding fast puppi jecs separately
  
  process.puppijescESSource = cms.ESSource('PoolDBESSource', # Nominal, Offline, FixedDist
    _CondDB.clone(connect = 'sqlite_file:puppiJECs.db'),
    toGet = cms.VPSet(
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Summer21_MC_AK4PFPuppiHLT'),
        label = cms.untracked.string('AK4PFPuppiHLT'),
      ),
    ),
  )
  process.puppijescESPrefer = cms.ESPrefer('PoolDBESSource', 'puppijescESSource')
  
else:
  ## ES modules for HLT JECs
  process.jescESSource = cms.ESSource('PoolDBESSource',
    _CondDB.clone(connect = 'sqlite_file:JESC_Run3Winter21_V2_MC.db'),
    toGet = cms.VPSet(
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Winter21_V2_MC_AK4PFClusterHLT'),
        label = cms.untracked.string('AK4PFClusterHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Winter21_V2_MC_AK4PFHLT'),#!!
        label = cms.untracked.string('AK4PFchsHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Winter21_V2_MC_AK4PFPuppiHLT'),
        label = cms.untracked.string('AK4PFPuppiHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Winter21_V2_MC_AK8PFClusterHLT'),
        label = cms.untracked.string('AK8PFClusterHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Winter21_V2_MC_AK8PFHLT'),#!!
        label = cms.untracked.string('AK8PFchsHLT'),
      ),
      cms.PSet(
        record = cms.string('JetCorrectionsRecord'),
        tag = cms.string('JetCorrectorParametersCollection_Run3Winter21_V2_MC_AK8PFPuppiHLT'),
        label = cms.untracked.string('AK8PFPuppiHLT'),
      ),
    ),
  )
  process.jescESPrefer = cms.ESPrefer('PoolDBESSource', 'jescESSource')

## ECAL UL calibrations
process.GlobalTag.toGet = cms.VPSet(
 cms.PSet(record = cms.string("EcalLaserAlphasRcd"),
 tag = cms.string("EcalLaserAlphas_UL_Run1_Run2_2018_lastIOV_movedTo1"),
 connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS")
 ),
 cms.PSet(record = cms.string("EcalIntercalibConstantsRcd"),
 tag = cms.string("EcalIntercalibConstants_UL_Run1_Run2_2018_lastIOV_movedTo1"),
 connect = cms.string("frontier://FrontierProd/CMS_CONDITIONS")
 ),)

## Output NTuple

process.TFileService = cms.Service('TFileService', fileName = cms.string(opts.output))


process.JMETriggerNTuple = cms.EDAnalyzer('JMETriggerNTuple',
  TTreeName = cms.string('Events'),
  TriggerResults = cms.InputTag('TriggerResults'),
  TriggerResultsFilterOR = cms.vstring(),
  TriggerResultsFilterAND = cms.vstring(),
  TriggerResultsCollections = cms.vstring(
    sorted(list(set([(_tmp[:_tmp.rfind('_v')] if '_v' in _tmp else _tmp) for _tmp in listOfPaths])))
  ),
  outputBranchesToBeDropped = cms.vstring(),

  HepMCProduct = cms.InputTag('generatorSmeared'),
  GenEventInfoProduct = cms.InputTag('generator'),
  PileupSummaryInfo = cms.InputTag('addPileupInfo'),

  doubles = cms.PSet(

    hltFixedGridRhoFastjetAllCalo = cms.InputTag('hltFixedGridRhoFastjetAllCalo'),
    hltFixedGridRhoFastjetAllPFCluster = cms.InputTag('hltFixedGridRhoFastjetAllPFCluster'),
    hltFixedGridRhoFastjetAll = cms.InputTag('hltFixedGridRhoFastjetAll'),
    #offlineFixedGridRhoFastjetAll = cms.InputTag('fixedGridRhoFastjetAll::RECO'),

    hltPixelClustersMultiplicity = cms.InputTag('hltPixelClustersMultiplicity'),
    
  ),

  vdoubles = cms.PSet(
  ),

  recoVertexCollections = cms.PSet(

    hltPixelVertices = cms.InputTag('hltPixelVertices'),
    hltTrimmedPixelVertices = cms.InputTag('hltTrimmedPixelVertices'),
    hltVerticesPF = cms.InputTag('hltVerticesPF'),
    #offlinePrimaryVertices = cms.InputTag('offlineSlimmedPrimaryVertices'),
  ),

  recoPFCandidateCollections = cms.PSet(
  ),

  recoGenJetCollections = cms.PSet(

    ak4GenJetsNoNu = cms.InputTag('ak4GenJetsNoNu::HLT'),
    ak8GenJetsNoNu = cms.InputTag('ak8GenJetsNoNu::HLT'),
  ),

  recoCaloJetCollections = cms.PSet(

    #hltAK4CaloJets = cms.InputTag('hltAK4CaloJets'),
    #hltAK4CaloJetsCorrected = cms.InputTag('hltAK4CaloJetsCorrected'),

    #hltAK8CaloJets = cms.InputTag('hltAK8CaloJets'),
    #hltAK8CaloJetsCorrected = cms.InputTag('hltAK8CaloJetsCorrected'),
  ),

  recoPFClusterJetCollections = cms.PSet(

    #hltAK4PFClusterJets = cms.InputTag('hltAK4PFClusterJets'),
    #hltAK4PFClusterJetsCorrected = cms.InputTag('hltAK4PFClusterJetsCorrected'),

    #hltAK8PFClusterJets = cms.InputTag('hltAK8PFClusterJets'),
    #hltAK8PFClusterJetsCorrected = cms.InputTag('hltAK8PFClusterJetsCorrected'),
  ),

  recoPFJetCollections = cms.PSet(

    #hltAK4PFJets = cms.InputTag('hltAK4PFJets'),
    hltAK4PFJetsCorrected = cms.InputTag('hltAK4PFJetsCorrected'),

    #hltAK4PFCHSJets = cms.InputTag('hltAK4PFCHSJets'),
    #hltAK4PFCHSJetsCorrected = cms.InputTag('hltAK4PFCHSJetsCorrected'),

    #hltAK4PFPuppiJets = cms.InputTag('hltAK4PFPuppiJets'),
    hltAK4PFPuppiJetsCorrected = cms.InputTag('hltAK4PFPuppiJetsCorrected'),

    #hltAK8PFJets = cms.InputTag('hltAK8PFJets'),
    #hltAK8PFJetsCorrected = cms.InputTag('hltAK8PFJetsCorrected'),

    #hltAK8PFCHSJets = cms.InputTag('hltAK8PFCHSJets'),
    #hltAK8PFCHSJetsCorrected = cms.InputTag('hltAK8PFCHSJetsCorrected'),

    #hltAK8PFPuppiJets = cms.InputTag('hltAK8PFPuppiJets'),
    #hltAK8PFPuppiJetsCorrected = cms.InputTag('hltAK8PFPuppiJetsCorrected'),
  ),

  patJetCollections = cms.PSet(

    #offlineAK4PFCHSJetsCorrected = cms.InputTag('slimmedJets'),
    offlineAK4PFPuppiJetsCorrected = cms.InputTag('slimmedJetsPuppi'),
    #offlineAK8PFPuppiJetsCorrected = cms.InputTag('slimmedJetsAK8'),
  ),

  recoGenMETCollections = cms.PSet(

    genMETCalo = cms.InputTag('genMetCalo::HLT'),
    genMETTrue = cms.InputTag('genMetTrue::HLT'),
  ),

  recoCaloMETCollections = cms.PSet(

    #hltCaloMET = cms.InputTag('hltMet'),
    #hltCaloMETTypeOne = cms.InputTag('hltCaloMETTypeOne'),
  ),

  recoPFClusterMETCollections = cms.PSet(

    #hltPFClusterMET = cms.InputTag('hltPFClusterMET'),
    #hltPFClusterMETTypeOne = cms.InputTag('hltPFClusterMETTypeOne'),
  ),

  
  recoPFMETCollections = cms.PSet(

    hltPFMET = cms.InputTag('hltPFMETProducer'),
    #hltPFMETTypeOne = cms.InputTag('hltPFMETTypeOne'),

    #hltPFCHSMET = cms.InputTag('hltPFCHSMET'),
    #hltPFCHSMETTypeOne = cms.InputTag('hltPFCHSMETTypeOne'),

    #hltPFPuppiMET = cms.InputTag('hltPFPuppiMET'),

    hltPFPuppiMETTypeOne = cms.InputTag('hltPFPuppiMETTypeOne'),
  ),
  

  patMETCollections = cms.PSet(

    offlinePFMET = cms.InputTag('slimmedMETs'),
    offlinePFPuppiMET = cms.InputTag('slimmedMETsPuppi'),
  ),
)

if opts.keepPFPuppi:
  process.hltPFPuppi.puppiDiagnostics = True
  process.JMETriggerNTuple.vdoubles = cms.PSet(
    hltPFPuppi_PuppiRawAlphas = cms.InputTag('hltPFPuppi:PuppiRawAlphas'),
    hltPFPuppi_PuppiAlphas = cms.InputTag('hltPFPuppi:PuppiAlphas'),
    hltPFPuppi_PuppiAlphasMed = cms.InputTag('hltPFPuppi:PuppiAlphasMed'),
    hltPFPuppi_PuppiAlphasRms = cms.InputTag('hltPFPuppi:PuppiAlphasRms')
  )
  process.JMETriggerNTuple.recoPFCandidateCollections = cms.PSet(
    hltParticleFlow = cms.InputTag('hltParticleFlow'),
    hltPFPuppi = cms.InputTag('hltPFPuppi'),
  )

process.analysisNTupleEndPath = cms.EndPath(process.JMETriggerNTuple)
process.schedule.append(process.analysisNTupleEndPath)


###
### Customisation for "mixed" tracking (full + pixel tracks in PF) 
###
if opts.useMixedTrk:
  from HLTrigger.Configuration.customizeHLTforMixedPF import customizeHLTForMixedPF
  process = customizeHLTForMixedPF(process)

#if opts.printSummaries:
#   process.FastTimerService.printEventSummary = False
#   process.FastTimerService.printRunSummary = False
#   process.FastTimerService.printJobSummary = True
#   process.ThroughputService.printEventSummary = False

###
### standard options
###

# max number of events to be processed
#process.maxEvents.input = opts.maxEvents
process.maxEvents.input = 1000

# number of events to be skipped
process.source.skipEvents = cms.untracked.uint32(opts.skipEvents)

# multi-threading settings
process.options.numberOfThreads = max(opts.numThreads, 1)
process.options.numberOfStreams = max(opts.numStreams, 0)

# show cmsRun summary at job completion
process.options.wantSummary = cms.untracked.bool(opts.wantSummary)

## update process.GlobalTag.globaltag
if opts.globalTag is not None:
   #from Configuration.AlCa.GlobalTag import GlobalTag
   #process.GlobalTag = GlobalTag(process.GlobalTag, opts.globalTag, '')
   process.GlobalTag.globaltag = cms.string(opts.globalTag)

# select luminosity sections from .json file
if opts.lumis is not None:
   import FWCore.PythonUtilities.LumiList as LumiList
   process.source.lumisToProcess = LumiList.LumiList(filename = opts.lumis).getVLuminosityBlockRange()

# input EDM files [primary]
if opts.inputFiles:
  process.source.fileNames = opts.inputFiles
else:
  process.source.fileNames = [
 #'/store/mc/Run3Winter21DRMiniAOD/VBFHToInvisible_M125_TuneCP5_14TeV-powheg-pythia8/GEN-SIM-DIGI-RAW/FlatPU30to80FEVT_112X_mcRun3_2021_realistic_v16-v1/270000/01a06ce0-a218-423f-a576-587debd69c63.root',
 #"/store/mc/RunIISummer16DR80/NeutrinoGun_E_10GeV/AODSIM/FlatPU0to75TuneCUETP8M4_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/120000/104F26EB-3B0B-E711-8750-A0369FC5EEF4.root"
 #"/store/mc/RunIIAutumn18DR/SingleNeutrinoGun/GEN-SIM-DIGI-RAW/PUPoissonAve85_102X_upgrade2018_realistic_v15_ext5-v1/100000/3D6B0068-DC22-4143-8DDE-5A68D48FCA4A.root"
 #'/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/003cee26-b0ed-4491-a301-f3261420b157.root'
 
 # test PU-only
 #'/store/mc/Run3Summer21DRPremix/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/SNB_120X_mcRun3_2021_realistic_v6-v2/2540000/000f4b8d-d64a-473d-9c30-acc77e148637.root'
 #'/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/AODSIM/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520000/00362d0b-f7a4-426b-ba2c-e91c2cd2b792.root'
 # test QCD
 # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/MINIAODSIM/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/1fb87340-34b4-4c8a-a049-33192b21d54b.root' 
 # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/AODSIM/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820000/01e4d447-2f4a-4ad0-bbc2-a8324f18ea2a.root'
 
 # '/store/mc/Run3Summer21MiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/MINIAODSIM/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v5-v1/30000/76dfad7c-52eb-4207-96cf-e74c5c6509d0.root'

 #  '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/0d8a6361-5115-49d3-86a4-4dbeca2e2fd6.root'
 #'/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810000/00323e70-75e6-4098-8cbc-31c69a451d8c.root'
 # '/store/mc/Run3Summer22DRPremix/SingleNeutrino_E-10_gun/GEN-SIM-RAW/SNB_124X_mcRun3_2022_realistic_v12-v2/70000/004ec806-0719-4f8c-8056-0efbd5ba22b1.root'
 # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/70007/98c44c2f-d5b4-49b3-a2bf-a709898dd8cd.root' 
 
  #'/store/mc/Run3Summer22MiniAODv3/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/MINIAODSIM/castor_124X_mcRun3_2022_realistic_v12-v2/50000/b72c6ff5-0480-46d7-be7c-f534057565a9.root'
  #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/090c78ea-c171-420a-a080-1d12cedac27b.root'
  #'/store/data/Run2022D/JetMET/MINIAOD/PromptReco-v1/000/357/538/00000/34aedf08-9e06-40a8-bfe9-8918be77570b.root'
  #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/090c78ea-c171-420a-a080-1d12cedac27b.root'
 
  '/store/data/Run2022D/MinimumBias/MINIAOD/27Jun2023-v2/80000/f6cb85d8-d3f3-43c9-ab0f-bf12fa35fbf3.root'
  #'/store/data/Run2022D/MinimumBias/MINIAOD/PromptReco-v1/000/357/537/00000/78fc82fa-1152-4bc8-9f21-ccb3190b5a5a.root'
  #'/store/data/Run2022D/JetMET/MINIAOD/PromptReco-v1/000/357/538/00000/34aedf08-9e06-40a8-bfe9-8918be77570b.root'
  #'/store/data/Run2022D/MinimumBias/MINIAOD/16Jun2023-v2/70000/28cf4c79-0dcc-4dab-895d-061e73f8527f.root' 
  #'/store/data/Run2022D/MinimumBias/RAW/v1/000/357/503/00000/45227074-eca3-492b-b55b-c9da0be23ef5.root'
  #'/store/mc/Run3Summer22MiniAODv3/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/MINIAODSIM/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810000/45730788-6f02-441f-b7fe-8ea83190d646.root'
  ]

# input EDM files [secondary]
if not hasattr(process.source, 'secondaryFileNames'):
  process.source.secondaryFileNames = cms.untracked.vstring()

if opts.secondaryInputFiles:
  process.source.secondaryFileNames = opts.secondaryInputFiles
else:
  process.source.secondaryFileNames = [
     
    #'/store/data/Run2022D/MinimumBias/RAW/v1/000/357/537/00000/c2089678-b808-4498-946a-eca4d23abe1b.root',
    #'/store/data/Run2022D/MinimumBias/RAW/v1/000/357/537/00000/dff5c6b2-69d8-41a5-95f8-e4ac9bc9f558.root',

    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/503/00000/45227074-eca3-492b-b55b-c9da0be23ef5.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/517/00000/5cf048f6-8bfe-4aa5-85f9-0066f8e2b273.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/523/00000/4b7e3258-0414-4e1d-b234-90a1c3839953.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/527/00000/87dfb7b4-cd82-454e-a057-d17a3986ff52.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/529/00000/b55ebc5e-8546-434b-9cfa-24bb4a877955.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/532/00000/ffa1e80d-4e60-4cd9-9d8e-2971f5f88482.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/533/00000/344f7354-84b9-4f21-ad60-41b60f02ec9a.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/554/00000/9c1097d7-3b87-410e-a06c-86b6f103e3b7.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/556/00000/3731ac39-b183-4cd9-8b38-0fdd4b4b32fb.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/556/00000/bf7dc05e-16da-4a79-b812-2bfb010820c8.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/556/00000/ddae1f63-3fda-4db7-8ff8-4f3e5a37250e.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/056b43d7-f988-465f-971e-8f5f0a5824be.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/0897f890-047a-48e5-87ef-5672ce496287.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/192e26b5-82b5-4f0b-bede-f781781ba6ba.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/3a19acdc-8aed-4a73-ad30-779b39cd4197.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/421e862c-84e7-4460-aff5-e0c1d71a1146.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/61a8d160-cb50-443e-8f0e-1758f44b4c3f.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/7a71ee3d-7698-40de-ba7c-b8800f9d58e2.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/8114aad0-9a1b-4046-80eb-04ec9686ec37.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/8a3f9b4a-59d0-47da-acc2-dde9be5ecf65.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/8a67df5a-de7d-47d6-a031-d7e55946d340.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/9a32c649-6aa3-4953-9ee3-cebb5f7ef59f.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/a17803f3-64b7-44dc-afc9-7a62e1b602be.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/a2a4862c-e1aa-44cb-87d9-2a658ffd49a9.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/a51c0844-cc90-486a-9c16-96322e8675df.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/c43e9c6c-f851-4e70-ac1b-52bd9842ab06.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/e0dde517-f46d-4348-a530-9f7422539e4b.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/ef5c124d-d79e-4828-bdb0-93b1c5f64785.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/fbdc91aa-9272-4596-bbdc-6a01f6da1264.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/557/00000/ff7a8af5-9245-448c-ba77-4dfe65de3451.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/558/00000/cab593c4-13cc-4d22-acdb-8c670617c4bc.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/559/00000/1e4a6f55-389e-42ea-8397-f973f6ef828f.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/559/00000/70c73522-91e8-46b2-b20e-190cffba8c4e.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/561/00000/82d99dda-b5f1-4d2d-b0b0-6674eec155cf.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/563/00000/2100a30b-fb8b-4400-a7d7-71c89731ac4f.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/574/00000/8f96f9c9-4f80-4c5e-8542-d8db36e74248.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/753/00000/8a9a06c0-70eb-43c8-9497-697362e4c92c.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/784/00000/57f501a5-f7da-4b16-b5ed-ba7ce96bed11.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/786/00000/dafd2414-f999-4cad-8f87-4e0c81419d71.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/801/00000/7802ce4c-5381-4bb9-9274-4356b060e31b.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/801/00000/8c1060cc-c662-495a-943b-0b6f71a02ce7.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/801/00000/fb4b2978-5dc3-42ad-bdad-66c7eabc7b34.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/875/00000/1dbae670-7044-46d2-a9c4-3e68da847872.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/357/881/00000/fb2a9da1-8d13-4db1-87d1-b0bfc0c52680.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/154/00000/703d5ef3-da7e-49f8-baae-7acb13bece9b.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/155/00000/52a3cfd5-4269-44f8-991f-1754e42ee707.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/155/00000/7b76c84e-452c-4818-8147-0857739a644c.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/155/00000/9a99b048-b180-42c2-8091-f97d0dd40bac.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/155/00000/daf407ff-5841-4dc1-9c1b-18ca8272fde5.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/155/00000/e4b62354-4603-4af7-b269-7d70da885284.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/157/00000/084ad4bc-0ac4-459d-a235-62f9c954be6a.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/164/00000/8e62ecdc-68aa-4ea3-9800-fce5b3a6a1b1.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/164/00000/aa9d6c80-a96d-47de-9472-aaa06629cdbf.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/164/00000/d66381e5-4ff4-4bd8-8a5f-06695569e160.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/164/00000/dd62c78b-eab5-42a1-b449-1c92d3a5b9b7.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/165/00000/d1f0d5e4-5e8d-4795-be31-1fffc07bd44a.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/176/00000/062ee87c-03ff-48db-a1fd-b7895b1721f9.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/178/00000/bd2a2349-ea2a-44f1-b0af-74e2990e6062.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/181/00000/b9e6fcc1-e151-4fe0-9afc-bacbd81eb7dc.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/184/00000/69be86ad-c4e4-4135-85d3-b7ae29dc0100.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/185/00000/ff708662-202a-44d1-afb4-c556563ba0f2.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/186/00000/5c56836d-e5a7-4b9e-ba7c-8a8acc4fcae8.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/283/00000/6641f3e4-9921-46db-b4b2-59410dda324b.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/283/00000/e0c27a36-ac66-4a06-bbb4-e2043ed0e871.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/284/00000/cd1fcf64-c77b-4eab-ad29-e43ed5911f31.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/285/00000/6f704466-57c0-448e-aa6e-2daecc6cce46.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/298/00000/36ebca39-267c-4d2c-903e-c51f8d522a39.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/300/00000/6801f0b8-7019-44b0-bc2d-9110b2782faf.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/302/00000/8e8ab489-0d63-4c03-96dc-02ef5b2ffc61.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/308/00000/c13b6f64-b5a2-4ec8-8d04-84b023ccf349.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/382/00000/35e70d50-9d5d-4ab4-a4b3-ff35252a8e3a.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/382/00000/37f62722-b363-47c8-bec0-89d3317572e3.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/382/00000/60474b9a-312e-4c12-9fb1-d1165f0b3250.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/382/00000/82fb68c6-a0ac-47c9-9e12-e87224f12029.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/382/00000/cb3570e0-b527-42e2-ba4d-19fe4fd04c2a.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/383/00000/d7a6cbd0-9622-422a-b602-f650e6cd9083.root',
    '/store/data/Run2022D/MinimumBias/RAW/v1/000/358/393/00000/3f766c12-3b77-4ffc-9921-e314e773a881.root',

    #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/090c78ea-c171-420a-a080-1d12cedac27b.root',
    #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/09b98bf7-41cc-4e8a-802c-304f5408de63.root',`
    #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/64c87a7c-688e-4a63-ba4e-cb2a006f7bf5.root',
    #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/73f0f134-355b-428c-a941-bde153a85def.root',
    #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/962d13e7-3dc7-4df2-9d29-fd1a37637388.root',
    #'/store/data/Run2022D/JetMET/RAW/v1/000/357/538/00000/c84eb850-9992-4693-8ad0-82d9a07c18c8.root',
  
    #'/store/data/Run2022D/MinimumBias/RAW/v1/000/357/503/00000/45227074-eca3-492b-b55b-c9da0be23ef5.root',
        
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/1da83140-9302-459c-a05c-fb1da65a8bc6.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/356ad8ab-ca0e-4848-a36f-46cd319afab6.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/364b4bd1-c6e9-44da-82e2-24bd63a0848e.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/472c61aa-d874-4b10-8d9a-49dc240536a9.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/612f0816-b05d-4bc2-92fb-f07e220042f6.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/89109c46-b2c4-4b63-94b1-bd74dcf3bdb8.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/8f1eadb5-70ad-4d7e-a5ba-78f33a3bdca3.root',

    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/02e2860f-5eb8-4ae8-b322-c9bb939f68d6.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/0ea37a71-6301-4915-93f7-89dfd2dd0233.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/404165bc-549c-4fa1-a091-54233efce405.root',

    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/964fd330-4c49-4a13-ae6a-60f5aea3efec.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/9bd8d959-1d86-4ae4-9120-855b5c6ecb54.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/a96ca7a6-f4ea-4256-a7b0-2303c884da3b.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/fdb46d54-9597-417c-af66-27a15d5e2175.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/06c3152c-5ebf-43a0-9e45-5c8e9263e602.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/209017ae-f9e9-4629-bf16-74c1e283fd71.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/2cc3c503-8e81-4094-928d-d0d53990cd14.root',

    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/472224cf-878d-4f88-9aa6-b0718e79e93f.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/4dce1bab-a309-4038-b6e9-b18d6631d37f.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/597d269d-aa06-4f99-bba6-4f412928ab33.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/6523d35a-2bc5-4322-97ab-065e09dd202f.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/5023584d-426a-42c6-b21a-2bdfb77bf61e.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/59785e1f-61df-4979-a4e0-eb57840739ef.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/69bae641-2cd1-45f7-bda1-fb23b1e646de.root',

    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/850e88db-36b9-4232-8f29-160bffd42675.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/c8e6a181-f21e-4445-b7db-3750d54a275c.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/c8f0e07f-112c-4eb3-9ac5-000bc644807d.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/da06b368-b73b-4c68-8768-7d66364c2fd5.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/255b55f9-ac37-49d1-8def-b2ac0a82d637.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/2e668597-ee42-41dc-babd-8bbe130ca921.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/4ef4ebef-d545-4ea9-b889-5af45b3cf67b.root',

    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/7271afe7-cdc2-4783-9b01-0b54bfe8101b.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/d6eda954-67ff-4a0e-88d6-4eefdf285551.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/e084dc7c-e61c-4c43-b7a3-888690602246.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/ee4dfcab-b826-4948-99e3-260816fd7a64.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/f252f54c-8fed-4c1d-b3f8-c56ab6ef51c9.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/108aada9-5cb8-44bd-83ea-61823bde4d0f.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/3f7163ef-35ba-4326-b1a2-244339579064.root',

    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/43bdae48-0d46-4823-bb0e-5462e1615416.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/818c513e-f26d-4911-bb76-fa9369185403.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/823d82a5-47a4-4770-b9cc-4f887af0d5d9.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/c9439dc3-dd42-40c8-8006-d0d04e9c4226.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/d5b412f1-a246-4230-a842-448db2f917de.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/2e668597-ee42-41dc-babd-8bbe130ca921.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/3bc68ae4-6838-4457-92ba-0f4b5e0f094f.root',

    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/464e5986-ff25-4836-809b-aab0d2a5edda.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/48da7ac7-7972-4222-98ba-996aec4297d0.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/7cc253e2-517f-459a-9434-cefd9cb0ec1e.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/8baeeb6a-e023-4984-b565-1daa47c41d03.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/a35ce5ee-e79f-4bb4-aa5c-465da3a517b3.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/adc02e58-fc58-40f1-bbf6-b1e8c4af6ccd.root',
    #'/store/mc/Run3Summer22DRPremix/QCD_PT-15to7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/castor_124X_mcRun3_2022_realistic_v12-v2/50000/d66e52f9-a8fe-4a39-abcb-82bcbfe6ef8e.root',
  
  ]
  

  '''
  process.source.secondaryFileNames = [
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810002/c221ca4f-6fae-4a9e-bb4f-e23ad6d740d3.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810002/d89c534c-bac9-4e5b-a3e6-b0ad9b1951f2.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/13bdc43b-8434-4196-af33-831d8c8425cd.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/80529447-c204-467c-a28b-b15767d675a9.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/008a15bc-bcd6-42d1-862c-8bcc312a2f9c.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/2c630511-03bb-4dcd-b159-b1c16c8d9376.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/9a7f6689-8364-4b2b-aa0a-0e1356e0760f.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/ea15c490-5a05-4da0-9705-f7f569ae28c4.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/9b3a18e1-cf30-40d4-a67f-425380078044.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/a9dd3de9-fa3a-4be7-a67e-1eea11e5840d.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/21bd21c2-7707-487e-a886-b0d4f146e15a.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/eec0ce57-77b4-498a-8869-8205b3c8fbbb.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/3b3d7563-015b-4332-b962-9fb03a4f309f.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/4e65c388-ee1f-4484-9ac9-3987be8d63bf.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/5139d3b2-f1ba-492d-a36f-dcb57549b4ac.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/b6174b51-f6d4-4f25-859b-89350466dd39.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/a503fc2a-0a1f-4359-8893-2c12a6e9b5d7.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/e7b22f48-47b8-4d44-8ca5-8e09ced66851.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810002/b89b365f-cabe-49d7-920a-0595b4544d4a.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810002/ddf4bf54-7ed8-4ea2-a6d4-6ec72dcb994d.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/10bacc4e-4210-4dcf-b343-f3db08eb7529.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/4041829d-7cb8-4edd-bf92-41c06752a6e8.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/ab937efb-74fd-48d9-bfb1-771bd9d20f54.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/c198d195-be61-4ec0-b9c0-6b03ccd27d9f.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810000/6cef5778-ffee-4b37-9cb6-2481e959adeb.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/bd81815b-444b-4939-95f2-19bae0707952.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/294d71e0-be27-4b63-971f-15b9f7afb88e.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810003/7fce48bb-a539-47e3-967a-bd83797a17bd.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/1a29f816-94eb-45eb-8a3f-43a9bea41ddc.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/2cc0526a-636d-4cdd-a8c1-42de6138445e.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/9c77bca8-8f3e-49d2-907b-e619bed85533.root',
    '/store/mc/Run3Summer22DR/QCD_Pt-15To7000_TuneCP5_13p6TeV_pythia8/GEN-SIM-RAW/FlatPU0to80_castor_124X_mcRun3_2022_realistic_v12-v1/2810001/bf75206a-d05c-439e-857c-151462ae0df1.root',


    # test PU-only
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520001/9154d5a7-8d1e-40a5-8ff2-0ec12515c390.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/02141377-fef1-4fa1-86f1-9bbae0927d07.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/033d4a7f-4731-4838-b680-40756a41974a.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/03e84645-9aff-4988-ad68-6eb8a1a8d03c.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/17c4f5c4-80ab-4191-95d3-8809e7cee970.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/2602ec39-bfc0-43e7-a72d-d237111342e4.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/32441529-91fb-4b95-ae01-c28a27a9a22e.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/4a417aa4-fce3-4632-886e-fb8a6ec853be.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/4e8a3050-fff4-4292-9eb5-91f48f902cb9.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/65529587-a211-479b-b804-71360ca2a63a.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/80e28bfa-b264-4b52-ac42-1c7b7dca6f0e.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/81e9ae8c-d7f8-4517-9dbe-7ebc868d41f2.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/8cd48b79-77e7-40f3-9c9b-43c8c71a7406.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/8d7a88df-727c-4e98-9d26-4483a7fdb595.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/9923a456-6773-4ea0-b82c-0bcafc94267c.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/b5e84669-cffe-4a7d-b437-65067597c1fa.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/ccbfffab-2c68-4574-a220-cb7dfee2d4b3.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/d2419e1a-97e4-49fa-9bf8-f6fa281dbd19.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/f40e56eb-6589-4c03-99c5-5b40d082888d.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/f9051a3a-670b-4b30-aac0-feee81e9dc06.root',
    # '/store/mc/Run3Winter22DR/SingleNeutrino_E-10-gun/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_SNB_122X_mcRun3_2021_realistic_v9-v2/2520005/f9a3c6a9-6c81-46d9-952e-12438e946239.root',
    
    # test QCD
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820000/a6db45f3-aac7-4123-b48f-021db13fe79c.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820000/bc364d75-61b7-47bc-87a8-54091ce8f0aa.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820001/0e728e38-ff2b-4087-95c3-758e322cdb6e.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820001/f05ad893-993f-4160-939f-3606967070df.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820003/0cf7acea-001f-42b9-b157-222543d86266.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820003/5ce782ce-e5dc-4a2b-952a-02dbc3cf0c7f.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820003/9b91cdb4-a430-4251-b409-f07dfb6e93bc.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820004/1c70a5f5-df2a-4eb3-8abe-91de54b8971a.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820004/8838f488-ed2f-4c3a-b122-6cfe75f55607.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820004/88fc5934-8f30-4af5-827a-a1e075228fff.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820004/a5e064b1-000a-469e-8c7d-221b11c085c5.root',
    # '/store/mc/Run3Winter22DR/QCD_Pt15to7000_TuneCP5_13p6TeV-pythia8/GEN-SIM-DIGI-RAW/L1TPU0to99FEVT_castor_122X_mcRun3_2021_realistic_v9-v2/2820004/d5b09519-335d-4012-bb36-2c155c063c5c.root'

#  '/store/mc/Run3Winter22GS/QCD_Pt-15to7000_TuneCP5_Flat_13p6TeV_pythia8/GEN-SIM/122X_mcRun3_2021_realistic_v9-v2/40003/0f6dd686-c85f-4c55-b207-cdd1646f7d1a.root',
#  '/store/mc/Run3Winter22GS/QCD_Pt-15to7000_TuneCP5_Flat_13p6TeV_pythia8/GEN-SIM/122X_mcRun3_2021_realistic_v9-v2/40003/45cc05fe-c6ea-42b2-84cf-e6e4af83c1a5.root',
#  '/store/mc/Run3Winter22GS/QCD_Pt-15to7000_TuneCP5_Flat_13p6TeV_pythia8/GEN-SIM/122X_mcRun3_2021_realistic_v9-v2/40003/571695d2-0e3e-45dc-95b8-5b4881bf0356.root',
#  '/store/mc/Run3Winter22GS/QCD_Pt-15to7000_TuneCP5_Flat_13p6TeV_pythia8/GEN-SIM/122X_mcRun3_2021_realistic_v9-v2/40003/5835fbc1-66f6-4372-a450-83002f5068a3.root',
#  '/store/mc/Run3Winter22GS/QCD_Pt-15to7000_TuneCP5_Flat_13p6TeV_pythia8/GEN-SIM/122X_mcRun3_2021_realistic_v9-v2/40003/6fde9068-2ec2-4ead-bca4-5df23c7c6a01.root',
#  '/store/mc/Run3Winter22GS/QCD_Pt-15to7000_TuneCP5_Flat_13p6TeV_pythia8/GEN-SIM/122X_mcRun3_2021_realistic_v9-v2/40003/ddc677fc-592d-4c43-ba41-fbf3d127902e.root',
#  '/store/mc/Run3Winter22GS/QCD_Pt-15to7000_TuneCP5_Flat_13p6TeV_pythia8/GEN-SIM/122X_mcRun3_2021_realistic_v9-v2/40003/ed761382-1713-4bca-bebc-0a0be2c04417.root'

      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/08f9d5ad-7a1c-4440-ac2f-f71c84d6f525.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/0bd11d4d-1967-4973-80ad-0b962d2669c5.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/0e0481b5-1c39-4eda-a1de-0e2254f52a9c.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/2045ffa9-fbd3-4153-bc38-207b607304cb.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/236704cf-462c-47ec-a8b3-6147ff0f4be9.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/23dc9f4b-488c-4f9b-82dd-9c982a7cd449.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/2c2c1b8c-3378-44da-87e5-bd3b4f948d22.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/4fea1664-d8db-43bd-bfad-cd94126424d3.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/5556d434-1dd5-434a-bccd-a0bc5f277152.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/5561b0cb-fe04-4c02-881f-295e558c5444.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/5f8f1d6d-6210-42ab-b8ee-0b00aacdd8e1.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/600ff5f5-716d-49b5-b728-f8376f84ceb0.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/6742997d-3d24-4deb-8365-61b6abc87ca4.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/6cbfb800-3d15-488a-954f-0feb585d37a5.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/755bff65-36b9-4172-ac83-f4e2685b53b4.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/87b78df9-1cf3-4ab7-806e-58f748112d2f.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/991c0347-412d-43eb-b219-b28af01e067f.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/ac7addf7-cbd6-434b-b8b3-8f56407deecd.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/ae75c926-22a1-4d3e-b0b0-7fc2a67c9fb5.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/b259fb57-968d-4aef-b27d-c2fc03aaea27.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/b5799868-5a40-48f3-83ca-b6f59d666565.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/c0640f64-da4d-49b0-87f5-e25f02277eef.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/c1ae0140-d077-4d40-a895-87852244210f.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/ce4c3976-70d7-4d77-aa43-dfeb2eb32f4f.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/ce6ebc04-d829-42d8-88f6-9a7259809f79.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/cf182551-397e-424f-aa9b-190e1003ec38.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/d34ff4b3-ce41-47f7-8f83-9ddcd95122c3.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/d428f27f-2d2f-4e46-a005-92a7f4199fd7.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/d6f2e27b-c502-4fcd-812d-a96280814cca.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/f2bf3602-f0d9-4ddc-9503-e1deefa9a8d8.root',
      # '/store/mc/Run3Winter21DRMiniAOD/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_112X_mcRun3_2021_realistic_v16-v2/120000/fff0e03b-c95e-41b9-b72e-fa6f163d6308.root'
    #########
    # '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/5a423664-f0f4-432a-9573-601f608ffd61.root',
    # '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/76845592-a3ca-4ba0-88d6-62a7783903d7.root',
    # '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/a825d603-efb0-4ec8-aa97-64c1d1668be4.root',
    # '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/00169f6c-2bd0-4419-9de0-f9dff5f6e909.root',
    # '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/4489ddce-a7e0-4a36-b924-7ec6de3b6bab.root',
    # '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/b66444c2-1e9e-4f10-8f75-6e9099fa7d6e.root',
    # '/store/mc/Run3Summer21DR/QCD_Pt15to7000_TuneCP5_14TeV-pythia8/GEN-SIM-DIGI-RAW/FlatPU0to80FEVT_castor_120X_mcRun3_2021_realistic_v6-v1/30000/d73315f5-4981-4a87-a48d-465ab24e203e.root',
  ]
'''

# dump content of cms.Process to python file
if opts.dumpPython is not None:
   open(opts.dumpPython, 'w').write(process.dumpPython())

# printouts
if opts.verbosity > 0:
   print('--- jmeTriggerNTuple_cfg.py ---')
   print('')
   print('option: output =', opts.output)
   print('option: reco =', opts.reco)
   print('option: dumpPython =', opts.dumpPython)
   print('')
   #print('process.GlobalTag =', process.GlobalTag.dumpPython())
   print('process.source =', process.source.dumpPython())
   print('process.maxEvents =', process.maxEvents.dumpPython())
   print('process.options =', process.options.dumpPython())
   print('-------------------------------')
