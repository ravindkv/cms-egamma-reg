# cms-egamma-reg
EGamma HLT energy regression

#For Run 3 (2023)
* git clone git@github.com:ravindkv/cms-egamma-reg.git
* source setWorkflow_2023.sh

# When the setup is done
* python3 runWorkflow_2023.py --s1Conf
* python3 runWorkflow_2023.py --s2Crab
* python3 runWorkflow_2023.py --s3Ntuple
* python3 runWorkflow_2023.py --s4Flat
* python3 runWorkflow_2023.py --s5Reg
* python3 runWorkflow_2023.py --s6Plot
* python3 runWorkflow_2023.py --s7NewGT
