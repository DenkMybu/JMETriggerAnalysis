# Tools for JetMET Analysis

Workflow to produce JetMET performance plots from ROOT flat-NTuples

### Setup

Update global environment variables:
source env.sh

### Batch Jobs

# Create scripts for submission of batch jobs (default script [-s]: jmeAnalysis.py):
batch_driver.py -s jmeAnalysis.py -i ntuples/trackingV2_191114/*root -o outputs_trackingV2_191114/prod -n 5000

# Monitoring and (re)submission of batch jobs:
batch_monitor.py -i outputs_trackingV2_191114

### Harvesting of Outputs

# Merge outputs of batch jobs:
merge_batchOutputs.py -i outputs_trackingV2_191114/prod/*.root -o outputs_trackingV2_191114/outputs

# Harvest outputs of jmeAnalysis.py script:
jmeAnalysisHarvester.py -i outputs_trackingV2_191114/outputs/*.root -o outputs_trackingV2_191114/outputs_postHarvesting
