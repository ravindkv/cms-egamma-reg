#https://egamma-regression.readthedocs.io/en/latest/GetHLTConfig.html#setup
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/EGMHLTRun3RecommendationForPAG
#----------------------------------------
#Setup egamma regression packages 
#----------------------------------------
echo -e "\033[32m -----: CMSSW Setup :----\033[0m"
export SCRAM_ARCH=slc7_amd64_gcc11
cmsrel CMSSW_13_1_0
cd CMSSW_13_1_0/src
eval `scramv1 runtime -sh`

echo -e "\033[32m -----: Step-1 Setup (produce edm files from hltConfig) :----\033[0m"
git cms-merge-topic Sam-Harper:EGHLTCustomisation_1230pre6
git cms-merge-topic Sam-Harper:L1NtupleFWLiteFixes_1230pre5
scramv1 b -j 8

echo -e "\033[32m -----: Step-2 Setup (produce ntuple from edm file)  :----\033[0m"
git clone git@github.com:ravindkv/HLTAnalyserPy.git Analysis/HLTAnalyserPy
scramv1 b -j 8
echo -e "\033[32m Change pid to 11 or 22 according to the input sample in Analysis/HLTAnalyserPy/python/EgHLTRun3Tree.py, L-198\033[0m"

#Setup for making flat ntuple and doing regression
echo -e "\033[32m -----: Step-3&4 Setup (produce flat ntuple and do regression)  :----\033[0m"
git clone -b Run3_2023_rverma_CMSSW_13_1_0 git@github.com:ravindkv/EgRegresTrainerLegacy.git 
cd EgRegresTrainerLegacy
gmake RegressionTrainerExe -j 8
gmake RegressionApplierExe -j 8
cd .. && cp ../../runWorkflow_2023.py .


