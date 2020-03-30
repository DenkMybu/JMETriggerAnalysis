import FWCore.ParameterSet.Config as cms

from RecoLocalTracker.SiPixelRecHits._generic_default_cfi import _generic_default
from RecoLocalTracker.SiPixelClusterizer.SiPixelClusterizerDefault_cfi import SiPixelClusterizerDefault as _SiPixelClusterizerDefault
from RecoLocalTracker.SubCollectionProducers.phase2trackClusterRemover_cfi import phase2trackClusterRemover as _phase2trackClusterRemover
from RecoTracker.FinalTrackSelectors.multiTrackSelector_cfi import looseMTS as _looseMTS
from RecoTracker.FinalTrackSelectors.trackAlgoPriorityOrderDefault_cfi import trackAlgoPriorityOrderDefault as _trackAlgoPriorityOrderDefault
from RecoTracker.MeasurementDet._MeasurementTrackerESProducer_default_cfi import _MeasurementTrackerESProducer_default
from RecoTracker.TkSeedGenerator.trackerClusterCheckDefault_cfi import trackerClusterCheckDefault as _trackerClusterCheckDefault
from RecoTracker.TrackProducer.TrackProducer_cfi import TrackProducer as _TrackProducer

### Needed for initialStepSeeds
from RecoTracker.TkSeedGenerator.seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer_cfi import seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer as _seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer

### Needed for ...?
from RecoJets.JetProducers.caloJetsForTrk_cff import caloTowerForTrk as _caloTowerForTrk

### Rationale: define HLT tracking as "offline tracking" + modifications. The modifications are those in this file.
# Initial step
from RecoTracker.IterativeTracking.InitialStep_cff import initialStepSeedLayers as _initialStepSeedLayers
from RecoTracker.IterativeTracking.InitialStep_cff import initialStepTrackingRegions as _initialStepTrackingRegions
from RecoTracker.IterativeTracking.InitialStep_cff import initialStepHitDoublets as _initialStepHitDoublets
from RecoTracker.IterativeTracking.InitialStep_cff import initialStepHitQuadruplets as _initialStepHitQuadruplets
from RecoTracker.IterativeTracking.InitialStep_cff import initialStepTracks as _initialStepTracks
from RecoTracker.IterativeTracking.InitialStep_cff import initialStepSelector as _initialStepSelector
# High-pt triplet
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepSeedLayers as _highPtTripletStepSeedLayers
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepTrackingRegions as _highPtTripletStepTrackingRegions
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepHitDoublets as _highPtTripletStepHitDoublets
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepHitTriplets as _highPtTripletStepHitTriplets
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepSeeds as _highPtTripletStepSeeds
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepTrackCandidates as _highPtTripletStepTrackCandidates
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepTracks as _highPtTripletStepTracks
from RecoTracker.IterativeTracking.HighPtTripletStep_cff import highPtTripletStepSelector as _highPtTripletStepSelector

def customize_hltPhase2_TRKv02(process):

    ###
    ### Modules (taken from configuration developed by TRK POG)
    ###

    ### The rationale is to take from the release as much as possible, 
    ### and use clone() calls with changes to the parameters if needed

    process.TrackProducer = _TrackProducer.clone()

    process.trackAlgoPriorityOrder = _trackAlgoPriorityOrderDefault.clone(
        algoOrder = cms.vstring(
            'initialStep',
            'highPtTripletStep'
        ),
    )    

    process.PixelCPEGenericESProducer = _generic_default.clone(
        LoadTemplatesFromDB = cms.bool(False),
        TruncatePixelCharge = cms.bool(False),
        Upgrade = cms.bool(True),
        UseErrorsFromTemplates = cms.bool(False),
    )

    process.MeasurementTracker = _MeasurementTrackerESProducer_default.clone(
        Phase2StripCPE = cms.string('Phase2StripCPE')
    )

    process.siPixelClustersPreSplitting = _SiPixelClusterizerDefault.clone(
        ElectronPerADCGain = cms.double(600.0),
        MissCalibrate = cms.bool(False),
        Phase2Calibration = cms.bool(True),
        src = cms.InputTag("simSiPixelDigis","Pixel")
    )
    
    process.siPixelClusters = _SiPixelClusterizerDefault.clone(
        ElectronPerADCGain = cms.double(600.0),
        MissCalibrate = cms.bool(False),
        Phase2Calibration = cms.bool(True),
        src = cms.InputTag("simSiPixelDigis","Pixel")
    )

    process.trackerClusterCheck = _trackerClusterCheckDefault.clone(
        doClusterCheck = cms.bool(False),
    )
    
    ### Why do we need this?
    process.caloTowerForTrk = _caloTowerForTrk.clone(
        HBThreshold = cms.double(0.3),
        HBThreshold1 = cms.double(0.1),
        HBThreshold2 = cms.double(0.2),
        HEDThreshold = cms.double(0.2),
        HEDThreshold1 = cms.double(0.1),
        HESThreshold = cms.double(0.2),
        HESThreshold1 = cms.double(0.1),
        HcalPhase = cms.int32(1),
        hbheInput = cms.InputTag("hbhereco")
    )

    ### INITIAL STEP
    process.initialStepSeedLayers = _initialStepSeedLayers.clone(
                layerList = cms.vstring(
                    'BPix1+BPix2+BPix3+BPix4', 
                    'BPix1+BPix2+BPix3+FPix1_pos', 
                    'BPix1+BPix2+BPix3+FPix1_neg', 
                    'BPix1+BPix2+FPix1_pos+FPix2_pos', 
                    'BPix1+BPix2+FPix1_neg+FPix2_neg', 
                    'BPix1+FPix1_pos+FPix2_pos+FPix3_pos', 
                    'BPix1+FPix1_neg+FPix2_neg+FPix3_neg', 
                    'FPix1_pos+FPix2_pos+FPix3_pos+FPix4_pos', 
                    'FPix1_neg+FPix2_neg+FPix3_neg+FPix4_neg', 
                    'FPix2_pos+FPix3_pos+FPix4_pos+FPix5_pos', 
                    'FPix2_neg+FPix3_neg+FPix4_neg+FPix5_neg', 
                    'FPix3_pos+FPix4_pos+FPix5_pos+FPix6_pos', 
                    'FPix3_neg+FPix4_neg+FPix5_neg+FPix6_neg', 
                    'FPix4_pos+FPix5_pos+FPix6_pos+FPix7_pos', 
                    'FPix4_neg+FPix5_neg+FPix6_neg+FPix7_neg', 
                    'FPix5_pos+FPix6_pos+FPix7_pos+FPix8_pos', 
                    'FPix5_neg+FPix6_neg+FPix7_neg+FPix8_neg'
                )
    )

    process.initialStepTrackingRegions = _initialStepTrackingRegions.clone(
        RegionPSet = dict(
            originRadius = cms.double(0.03),
        ),
    )

    process.initialStepHitDoublets = _initialStepHitDoublets.clone(
        layerPairs = cms.vuint32(0, 1, 2),
    )

    process.initialStepHitQuadruplets = _initialStepHitQuadruplets.clone(
        CAPhiCut = cms.double(0.175),
        CAThetaCut = cms.double(0.001),
        mightGet = cms.untracked.vstring(
            'IntermediateHitDoublets_initialStepHitDoublets__RECO', 
            'IntermediateHitDoublets_initialStepHitDoublets__RECO'
        ),
    )
    
    # The usual "initialStepSeeds" from "InitialStep_cff" is a
    # "SeedCreatorFromRegionConsecutiveHitsEDProducer",
    # In this configuration we want a 
    # "SeedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer"
    process.initialStepSeeds = _seedCreatorFromRegionConsecutiveHitsTripletOnlyEDProducer.clone(
        SeedComparitorPSet = dict(
            ClusterShapeCacheSrc = cms.InputTag("siPixelClusterShapeCache"),
            ClusterShapeHitFilterName = cms.string('ClusterShapeHitFilter'),
            ComponentName = cms.string('PixelClusterShapeSeedComparitor'),
            FilterAtHelixStage = cms.bool(False),
            FilterPixelHits = cms.bool(True),
            FilterStripHits = cms.bool(False)
        ),
        magneticField = cms.string(''),
        mightGet = cms.untracked.vstring(
            'RegionsSeedingHitSets_initialStepHitQuadruplets__RECO', 
            'RegionsSeedingHitSets_initialStepHitQuadruplets__RECO'
        ),
        propagator = cms.string('PropagatorWithMaterial'),
        seedingHitSets = cms.InputTag("initialStepHitQuadruplets")
    )
    
    # process.initialStepTrackCandidates ### Where does this come from?
    
    process.initialStepTracks = _initialStepTracks.clone(
        AlgorithmName = cms.string('initialStep'),
        Fitter = cms.string('FlexibleKFFittingSmoother'),
        src = cms.InputTag("initialStepTrackCandidates"),
    )

    # Some PSets for TrackSelector
    hltInitialStepLoose = _looseMTS.clone(
        chi2n_par = cms.double(2.0),
        d0_par1 = cms.vdouble(0.8, 4.0),
        d0_par2 = cms.vdouble(0.6, 4.0),
        dz_par1 = cms.vdouble(0.9, 4.0),
        dz_par2 = cms.vdouble(0.8, 4.0),
        maxNumberLostLayers = cms.uint32(3),
        minNumber3DLayers = cms.uint32(3),
        minNumberLayers = cms.uint32(3),
        name = cms.string('initialStepLoose'),
        res_par = cms.vdouble(0.003, 0.002),
    )
    hltInitialStepTight = _looseMTS.clone(
        chi2n_par = cms.double(1.4),
        d0_par1 = cms.vdouble(0.7, 4.0),
        d0_par2 = cms.vdouble(0.5, 4.0),
        dz_par1 = cms.vdouble(0.8, 4.0),
        dz_par2 = cms.vdouble(0.7, 4.0),
        keepAllTracks = cms.bool(True),
        maxNumberLostLayers = cms.uint32(2),
        minNumber3DLayers = cms.uint32(3),
        minNumberLayers = cms.uint32(3),
        name = cms.string('initialStepTight'),
        preFilterName = cms.string('initialStepLoose'),
        qualityBit = cms.string('tight'),
        res_par = cms.vdouble(0.003, 0.002),
    )
    hltInitialStep = _looseMTS.clone(
        chi2n_par = cms.double(1.2),
        d0_par1 = cms.vdouble(0.6, 4.0),
        d0_par2 = cms.vdouble(0.45, 4.0),
        dz_par1 = cms.vdouble(0.7, 4.0),
        dz_par2 = cms.vdouble(0.55, 4.0),
        maxNumberLostLayers = cms.uint32(3),
        minNumber3DLayers = cms.uint32(3),
        minNumberLayers = cms.uint32(3),
        name = cms.string('initialStep'),
        preFilterName = cms.string('initialStepTight'),
        qualityBit = cms.string('highPurity'),
        res_par = cms.vdouble(0.003, 0.001),
    )

    process.initialStepSelector = _initialStepSelector.clone(
        #beamspot = cms.InputTag("offlineBeamSpot"), #Already default
        src = cms.InputTag("initialStepTracks"),
        trackSelectors = cms.VPSet(
            hltInitialStepLoose,
            hltInitialStepTight,
            hltInitialStep
        )
        #vertices = cms.InputTag("firstStepPrimaryVertices"), #Already default
    )

    process.siPixelClusterShapeCache = cms.EDProducer("SiPixelClusterShapeCacheProducer",
        onDemand = cms.bool(False),
        src = cms.InputTag("siPixelClusters")
    )
   
    ### HIGH PT TRIPLET ITERATION
    
    process.highPtTripletStepClusters = _phase2trackClusterRemover.clone(
        maxChi2 = cms.double(9.0),
        overrideTrkQuals = cms.InputTag("initialStepSelector","initialStep"),
        trackClassifier = cms.InputTag("","QualityMasks"),
        trajectories = cms.InputTag("initialStepTracks")
    )

    process.highPtTripletStepSeedLayers =  _highPtTripletStepSeedLayers.clone(
        layerList = cms.vstring(
            'BPix1+BPix2+BPix3', 
            'BPix2+BPix3+BPix4', 
            'BPix1+BPix3+BPix4', 
            'BPix1+BPix2+BPix4', 
            'BPix2+BPix3+FPix1_pos', 
            'BPix2+BPix3+FPix1_neg', 
            'BPix1+BPix2+FPix1_pos', 
            'BPix1+BPix2+FPix1_neg', 
            'BPix2+FPix1_pos+FPix2_pos', 
            'BPix2+FPix1_neg+FPix2_neg', 
            'BPix1+FPix1_pos+FPix2_pos', 
            'BPix1+FPix1_neg+FPix2_neg', 
            'FPix1_pos+FPix2_pos+FPix3_pos', 
            'FPix1_neg+FPix2_neg+FPix3_neg', 
            'BPix1+FPix2_pos+FPix3_pos', 
            'BPix1+FPix2_neg+FPix3_neg', 
            'FPix2_pos+FPix3_pos+FPix4_pos', 
            'FPix2_neg+FPix3_neg+FPix4_neg', 
            'FPix3_pos+FPix4_pos+FPix5_pos', 
            'FPix3_neg+FPix4_neg+FPix5_neg', 
            'FPix4_pos+FPix5_pos+FPix6_pos', 
            'FPix4_neg+FPix5_neg+FPix6_neg', 
            'FPix5_pos+FPix6_pos+FPix7_pos', 
            'FPix5_neg+FPix6_neg+FPix7_neg', 
            'FPix6_pos+FPix7_pos+FPix8_pos', 
            'FPix6_neg+FPix7_neg+FPix8_neg'
        )
    )

    process.highPtTripletStepTrackingRegions = _highPtTripletStepTrackingRegions.clone(
        RegionPSet = dict(
            originRadius = cms.double(0.02),
            ptMin = cms.double(0.7),
        )
    )
    
    process.highPtTripletStepHitDoublets = _highPtTripletStepHitDoublets.clone()
    
    process.highPtTripletStepHitTriplets = _highPtTripletStepHitTriplets.clone(
        CAHardPtCut = cms.double(0.5),
        CAPhiCut = cms.double(0.06),
        CAThetaCut = cms.double(0.003),
        #doublets = cms.InputTag("highPtTripletStepHitDoublets"), # default
        mightGet = cms.untracked.vstring(
            'IntermediateHitDoublets_highPtTripletStepHitDoublets__RECO', 
            'IntermediateHitDoublets_highPtTripletStepHitDoublets__RECO'
        ),
    )
    
    process.highPtTripletStepSeeds = _highPtTripletStepSeeds.clone(
        magneticField = cms.string(''),
        mightGet = cms.untracked.vstring(
            'RegionsSeedingHitSets_highPtTripletStepHitTriplets__RECO', 
            'RegionsSeedingHitSets_highPtTripletStepHitTriplets__RECO'
        ),
        propagator = cms.string('PropagatorWithMaterial'),
        #seedingHitSets = cms.InputTag("highPtTripletStepHitTriplets"), # default
    )
    
    process.highPtTripletStepTracks = _highPtTripletStepTracks.clone(
        TTRHBuilder = cms.string('WithTrackAngle'),
        alias = cms.untracked.string('ctfWithMaterialTracks'),
        #beamSpot = cms.InputTag("offlineBeamSpot"), # default
        
        src = cms.InputTag("highPtTripletStepTrackCandidates"),
        useHitsSplitting = cms.bool(False),
        useSimpleMF = cms.bool(False)
    )
    
    # Some PSets for TrackSelector
    hltHighPtTripletStepLoose = _looseMTS.clone(
        chi2n_par = cms.double(2.0),
        d0_par1 = cms.vdouble(0.7, 4.0),
        d0_par2 = cms.vdouble(0.6, 4.0),
        dz_par1 = cms.vdouble(0.8, 4.0),
        dz_par2 = cms.vdouble(0.6, 4.0),
        maxNumberLostLayers = cms.uint32(3),
        minNumber3DLayers = cms.uint32(3),
        minNumberLayers = cms.uint32(3),
        name = cms.string('highPtTripletStepLoose'),
        res_par = cms.vdouble(0.003, 0.002),       
    )
    hltHighPtTripletStepTight = _looseMTS.clone(
        chi2n_par = cms.double(1.0),
        d0_par1 = cms.vdouble(0.6, 4.0),
        d0_par2 = cms.vdouble(0.5, 4.0),
        dz_par1 = cms.vdouble(0.7, 4.0),
        dz_par2 = cms.vdouble(0.6, 4.0),
        keepAllTracks = cms.bool(True),
        maxNumberLostLayers = cms.uint32(2),
        minNumber3DLayers = cms.uint32(3),
        minNumberLayers = cms.uint32(3),
        name = cms.string('highPtTripletStepTight'),
        preFilterName = cms.string('highPtTripletStepLoose'),
        qualityBit = cms.string('tight'),
        res_par = cms.vdouble(0.003, 0.002),
    )
    hltHighPtTripletStep = _looseMTS.clone(
        chi2n_par = cms.double(0.8),
        d0_par1 = cms.vdouble(0.6, 4.0),
        d0_par2 = cms.vdouble(0.45, 4.0),
        dz_par1 = cms.vdouble(0.7, 4.0),
        dz_par2 = cms.vdouble(0.55, 4.0),
        keepAllTracks = cms.bool(True),
        maxNumberLostLayers = cms.uint32(2),
        minNumber3DLayers = cms.uint32(4),
        minNumberLayers = cms.uint32(4),
        min_nhits = cms.uint32(4),
        name = cms.string('highPtTripletStep'),
        preFilterName = cms.string('highPtTripletStepTight'),
        qualityBit = cms.string('highPurity'),
        res_par = cms.vdouble(0.003, 0.001),
    )

    process.highPtTripletStepSelector = _highPtTripletStepSelector.clone(
        #beamspot = cms.InputTag("offlineBeamSpot"),
        #src = cms.InputTag("highPtTripletStepTracks"),
        trackSelectors = cms.VPSet(
            hltHighPtTripletStepLoose,
            hltHighPtTripletStepTight,
            hltHighPtTripletStep,
        ),
        #vertices = cms.InputTag("firstStepPrimaryVertices")
    )

    ### The two iterations ended here, now put them together and do vertices.

    process.MeasurementTrackerEvent = cms.EDProducer("MeasurementTrackerEventProducer",
        Phase2TrackerCluster1DProducer = cms.string('siPhase2Clusters'),
        badPixelFEDChannelCollectionLabels = cms.VInputTag("siPixelDigis"),
        inactivePixelDetectorLabels = cms.VInputTag(),
        inactiveStripDetectorLabels = cms.VInputTag("siStripDigis"),
        measurementTracker = cms.string(''),
        pixelCablingMapLabel = cms.string(''),
        pixelClusterProducer = cms.string('siPixelClusters'),
        skipClusters = cms.InputTag(""),
        stripClusterProducer = cms.string(''),
        switchOffPixelsIfEmpty = cms.bool(True)
    )
        
    process.generalTracks = cms.EDProducer("TrackListMerger",
        Epsilon = cms.double(-0.001),
        FoundHitBonus = cms.double(5.0),
        LostHitPenalty = cms.double(5.0),
        MaxNormalizedChisq = cms.double(1000.0),
        MinFound = cms.int32(3),
        MinPT = cms.double(0.05),
        ShareFrac = cms.double(0.19),
        TrackProducers = cms.VInputTag("initialStepTracks", "highPtTripletStepTracks"),
        allowFirstHitShare = cms.bool(True),
        copyExtras = cms.untracked.bool(True),
        copyMVA = cms.bool(True),
        hasSelector = cms.vint32(1, 1),
        indivShareFrac = cms.vdouble(1.0, 0.16),
        makeReKeyedSeeds = cms.untracked.bool(False),
        newQuality = cms.string('confirmed'),
        selectedTrackQuals = cms.VInputTag(
            cms.InputTag("initialStepSelector","initialStep"), 
            cms.InputTag("highPtTripletStepSelector","highPtTripletStep")),
        setsToMerge = cms.VPSet(cms.PSet(
            pQual = cms.bool(True),
            tLists = cms.vint32(0, 1)
        )),
        trackAlgoPriorityOrder = cms.string('trackAlgoPriorityOrder'),
        writeOnlyTrkQuals = cms.bool(False)
    )
    
    process.inclusiveVertexFinder = cms.EDProducer("InclusiveVertexFinder",
        beamSpot = cms.InputTag("offlineBeamSpot"),
        clusterizer = cms.PSet(
            clusterMaxDistance = cms.double(0.05),
            clusterMaxSignificance = cms.double(4.5),
            clusterMinAngleCosine = cms.double(0.5),
            distanceRatio = cms.double(20),
            maxTimeSignificance = cms.double(3.5),
            seedMax3DIPSignificance = cms.double(9999),
            seedMax3DIPValue = cms.double(9999),
            seedMin3DIPSignificance = cms.double(1.2),
            seedMin3DIPValue = cms.double(0.005)
        ),
        fitterRatio = cms.double(0.25),
        fitterSigmacut = cms.double(3),
        fitterTini = cms.double(256),
        maxNTracks = cms.uint32(30),
        maximumLongitudinalImpactParameter = cms.double(0.3),
        maximumTimeSignificance = cms.double(3),
        minHits = cms.uint32(8),
        minPt = cms.double(0.8),
        primaryVertices = cms.InputTag("offlinePrimaryVertices"),
        tracks = cms.InputTag("generalTracks"),
        useDirectVertexFitter = cms.bool(True),
        useVertexReco = cms.bool(True),
        vertexMinAngleCosine = cms.double(0.95),
        vertexMinDLen2DSig = cms.double(2.5),
        vertexMinDLenSig = cms.double(0.5),
        vertexReco = cms.PSet(
            finder = cms.string('avr'),
            primcut = cms.double(1),
            seccut = cms.double(3),
            smoothing = cms.bool(True)
        )
    )
    
    process.trackVertexArbitrator = cms.EDProducer("TrackVertexArbitrator",
        beamSpot = cms.InputTag("offlineBeamSpot"),
        dLenFraction = cms.double(0.333),
        dRCut = cms.double(0.4),
        distCut = cms.double(0.04),
        fitterRatio = cms.double(0.25),
        fitterSigmacut = cms.double(3),
        fitterTini = cms.double(256),
        maxTimeSignificance = cms.double(3.5),
        primaryVertices = cms.InputTag("offlinePrimaryVertices"),
        secondaryVertices = cms.InputTag("vertexMerger"),
        sigCut = cms.double(5),
        trackMinLayers = cms.int32(4),
        trackMinPixels = cms.int32(1),
        trackMinPt = cms.double(0.4),
        tracks = cms.InputTag("generalTracks")
    )

    ###
    ### Sequences
    ###

    process.itLocalReco = cms.Sequence(
        process.siPhase2Clusters
      + process.siPixelClusters
      + process.siPixelClusterShapeCache
      + process.siPixelClustersPreSplitting
      + process.siPixelRecHits
      + process.siPixelRecHitsPreSplitting
    )

    process.otLocalReco = cms.Sequence(
        process.MeasurementTrackerEvent
    )

    process.initialStepPVSequence = cms.Sequence(
        process.firstStepPrimaryVerticesUnsorted #uses beamspot
      + process.initialStepTrackRefsForJets
      + process.hcalGlobalRecoSequence
      + process.caloTowerForTrk
      + process.ak4CaloJetsForTrk
      + process.firstStepPrimaryVertices
    )

    process.initialStepSequence = cms.Sequence(
        process.initialStepSeedLayers
      + process.initialStepTrackingRegions
      + process.initialStepHitDoublets
      + process.initialStepHitQuadruplets
      + process.initialStepSeeds
      + process.initialStepTrackCandidates
      + process.initialStepTracks
      + process.initialStepPVSequence
      + process.initialStepSelector
    )

    process.highPtTripletStepSequence = cms.Sequence(
        process.highPtTripletStepClusters
      + process.highPtTripletStepSeedLayers
      + process.highPtTripletStepTrackingRegions
      + process.highPtTripletStepHitDoublets
      + process.highPtTripletStepHitTriplets
      + process.highPtTripletStepSeedLayers
      + process.highPtTripletStepSeeds
      + process.highPtTripletStepTrackCandidates
      + process.highPtTripletStepTracks
      + process.highPtTripletStepSelector
      + process.initialStepSeedClusterMask # needed by electron, but also by highPtTripletStepSeedClusterMask
      + process.highPtTripletStepSeedClusterMask
    )

    process.vertexReco = cms.Sequence(
        process.unsortedOfflinePrimaryVertices4DnoPID
      + process.unsortedOfflinePrimaryVertices
      + process.trackWithVertexRefSelectorBeforeSorting4DnoPID
      + process.trackWithVertexRefSelectorBeforeSorting
      + process.trackRefsForJetsBeforeSorting4DnoPID
      + process.trackRefsForJetsBeforeSorting
      + process.tpClusterProducer
      + process.tofPID4DnoPID
      + process.unsortedOfflinePrimaryVertices4D
      + process.trackWithVertexRefSelectorBeforeSorting4D
      + process.trackRefsForJetsBeforeSorting4D
      + process.tofPID
      + process.quickTrackAssociatorByHits
      + process.trackTimeValueMapProducer
      + process.caloTowerForTrk
      + process.ak4CaloJetsForTrk
#      + process.offlinePrimaryVertices4DnoPIDWithBS
#      + process.offlinePrimaryVertices4DWithBS
#      + process.offlinePrimaryVertices4D
      + process.offlinePrimaryVerticesWithBS
      + process.offlinePrimaryVertices
#      + process.generalV0Candidates
      + process.inclusiveVertexFinder
      + process.vertexMerger
      + process.trackVertexArbitrator
      + process.inclusiveSecondaryVertices
#      + process.offlinePrimaryVertices4DnoPID
    )

    process.globalreco_tracking = cms.Sequence(
        process.itLocalReco
      + process.otLocalReco
      + process.offlineBeamSpot #cmssw_10_6
      + process.trackerClusterCheck
      + process.initialStepSequence
      + process.highPtTripletStepSequence
      + process.generalTracks
      + process.vertexReco 
      + process.standalonemuontracking # needs to be included for early muons of PF
    )

    # remove globalreco_trackingTask to avoid any ambiguities
    # with the updated sequence process.globalreco_tracking
    if hasattr(process, 'globalreco_trackingTask'):
       del process.globalreco_trackingTask

    return process
