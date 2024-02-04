import os
import sys
import subprocess
sys.dont_write_bytecode = True
from optparse import OptionParser

#https://egamma-regression.readthedocs.io/en/latest/GetHLTConfig.html
#----------------------------------------
#INPUT command-line arguments 
#----------------------------------------
parser = OptionParser()
parser.add_option("--s1Conf",   "--s1Conf",     dest="s1Conf",action="store_true",default=False, help="Get HLT Configuration") 
parser.add_option("--s2Crab",   "--s2Crab",     dest="s2Crab",action="store_true",default=False, help="Crab submission")
parser.add_option("--s3Ntuple", "--s3Ntuple",   dest="s3Ntuple",action="store_true",default=False, help="Ntuples")
parser.add_option("--s4Flat",   "--s4Flat",   dest="s4Flat",action="store_true",default=False, help="Flat Flats")
parser.add_option("--s5Reg",    "--s5Reg",      dest="s5Reg",action="store_true",default=False, help="Perform regression")
parser.add_option("--s6Plot",   "--s6Plot",     dest="s6Plot",action="store_true",default=False, help="Plot reg output")
parser.add_option("--s7NewGT",  "--s7NewGT",    dest="s7NewGT",action="store_true",default=False, help="Create new GT")
(options, args) = parser.parse_args()

s1Conf = options.s1Conf
s2Crab = options.s2Crab
s3Ntuple = options.s3Ntuple
s4Flat = options.s4Flat
s5Reg = options.s5Reg
s6Plot = options.s6Plot
s7NewGT = options.s7NewGT

eosDir = "/store/group/phys_egamma/ec/rverma/egammaRegChain_01Feb"
#----------------------------------------
# Steo-1: Get HLT Configuration file
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/EGMHLTRun3RecommendationForPAG
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideGlobalHLT
#----------------------------------------
typeIC = {}
typeIC["REAL"]  = "126X_mcRun3_2023_forPU65_v1"
typeIC["IDEAL"] = "126X_mcRun3_2023_forPU65_v1_ECALIdealIC"
gRunMenu = "/dev/CMSSW_13_1_0/GRun"
sample   = "/DoublePhoton_Pt-5To300_gun/Run3Summer23BPixDRPremix-130X_mcRun3_2023_realistic_postBPix_v2-v2/GEN-SIM-RAW"
custom   = "HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaMenuDev,HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaInputContent"
common   = "--mc --process MYHLT --prescale none --max-events 100 --eras Run3 --l1-emulator FullMC --l1  L1Menu_Collisions2023_v1_0_0_xml --output minimal  --paths HLTriggerFirstPath,MC_Egamma_Open_v*,MC_Egamma_Open_Unseeded_v*,HLTriggerFinalPath"
samp = sample.split("/")[1].replace("/", "")

def getFile(sample):
    print("voms-proxy-init --voms cms --valid 24:00")
    das = "dasgoclient --query='file dataset=%s status=*'"%sample
    print(das)
    std_output, std_error = subprocess.Popen(das,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    files = std_output.decode("ascii").replace('\n',' ')
    files_ = files.split(" ")
    if len(files_)==0:
        print("No files found")
        exit(0)
    return files_[0]

if s1Conf:
    inFile = getFile(sample)
    inFile_ = "root://cms-xrd-global.cern.ch/%s"%inFile
    #inFile_ = "file:2560000/8c0c4efa-ab57-4152-b313-4ae24aaaf04e.root"
    print(inFile_)
    for t in typeIC.keys():
        cmd = "hltGetConfiguration %s --globaltag %s --input %s --customise %s %s > hlt_%s.py"%(gRunMenu, typeIC[t], inFile_, custom, common, t)
        print(cmd)
        os.system(cmd)
        #os.system("cmsRun hlt_%s.py"%t)

#----------------------------------------
# Step-2: Crab submission 
#----------------------------------------
crab = """
from CRABClient.UserUtilities import config
config = config()

# config.section_('General')
config.General.requestName = 'crab_%s'
config.General.workArea = 'crab_%s'
config.General.transferOutputs = True
config.General.transferLogs = True

# config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'hlt_%s.py'
config.JobType.numCores = 4

# config.Data.inputDBS = 'phys03'
config.JobType.allowUndistributedCMSSW = True
config.JobType.maxMemoryMB = 4000

# config.JobType.numCores = 8
config.Data.inputDataset ='%s'
# config.Data.splitting = 'Automatic'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 10

config.Data.outLFNDirBase = '%s'
config.Data.publication = False
config.Site.storageSite = 'T2_CH_CERN'
"""
if s2Crab:
    os.system("rm -rf crab_*")
    os.system("source /cvmfs/cms.cern.ch/crab3/crab.sh")
    for t in typeIC.keys():
        outFile = open("crab_%s.py"%t, "w")
        dirName = "%s_%s"%(samp, t)
        eosDir_ = "%s/s2Crab"%eosDir
        outStr  = crab%(dirName, dirName, t, sample, eosDir_)
        print(outStr)
        print("/eos/cms/%s"%eosDir_) 
        outFile.write(outStr)
        #os.system("crab submit %s"%outFile)
        outFile.close()

#----------------------------------------
# Step-3: Edm to ntuples 
#----------------------------------------
def getFile2(dir_):
    edm = "find %s -type f | grep output_99\.root"%dir_
    #edm = "find %s -type f | grep root"%dir_
    #edm = "find %s -type f -name *.root"%dir_
    std_output, std_error = subprocess.Popen(edm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    files = std_output.decode("ascii").replace('\n',' ')
    files_ = files.split(" ")
    if len(files_)==0:
        print("No files found")
        exit(0)
    return files

if s3Ntuple:
    for t in typeIC.keys():
        crabEOSDir = "/eos/cms%s/s2Crab/%s/crab_crab_%s_%s"%(eosDir, samp, samp, t)
        edmFiles = getFile2(crabEOSDir)
        ntupDir = "/eos/cms%s/s3Ntuple/%s"%(eosDir, samp)
        os.system("mkdir -p %s"%ntupDir)
        ntup = "%s/HLTAnalyzerTree_%s.root"%(ntupDir, t)
        cmd = "python3 Analysis/HLTAnalyserPy/test/makeRun3Ntup.py -r 1000 %s -o %s &"%(edmFiles, ntup)
        print(cmd)
        #os.system("%s"%cmd)
        #os.system("python3 Analysis/HLTAnalyserPy/test/runMultiThreaded.py --cmd \" %s \" %s -o %s --hadd"%(cmd, edmFiles, ntup))

#----------------------------------------
# Step-4: Flat ntuples 
#----------------------------------------
if s4Flat:
    for t in typeIC.keys():
        ntupDir = "/eos/cms%s/s3Ntuple/%s"%(eosDir, samp)
        flatDir = "/eos/cms%s/s4Flat/%s"%(eosDir, samp)
        os.system("mkdir -p %s"%flatDir)
        ntup = "%s/HLTAnalyzerTree_%s.root"%(ntupDir, t)
        flat = "%s/HLTAnalyzerTree_%s_Flat.root"%(flatDir, t)
        cmd = "root -l -b -q EgRegresTrainerLegacy/GetFlatNtuple/GetFlatNtuple.C\(\\\"%s\\\",\\\"%s\\\"\) &"%(ntup, flat)
        print(cmd)
        os.system("%s"%cmd)

if s5Reg:
    cmd1 = "cd EgRegresTrainerLegacy"
    cmd2 = "export PATH=$PATH:./bin/$SCRAM_ARCH"
    cmd3 = "export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$PWD/include"
    ntupDir = "/eos/cms%s/s4Flat/%s"%(eosDir, samp)
    regDir  = "/eos/cms%s/s5Reg/%s"%(eosDir, samp)
    os.system("rm -r %s"%regDir)
    os.system("mkdir -p %s"%regDir)
    cmd4 = "python3 scripts/runSCRegTrainings.py --era \"Run3\" -i %s -o %s"%(ntupDir, regDir)
    print("%s && %s && %s && %s && cd .."%(cmd1, cmd2, cmd3, cmd4))

if s6Plot:
    regDir  = "/eos/cms%s/s5Reg/%s"%(eosDir, samp)
    cmd = "python3 EgRegresTrainerLegacy/Plot_mean.py -i %s"%regDir
    print(cmd)
    os.system(cmd)

