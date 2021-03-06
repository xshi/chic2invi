#!/usr/bin/env python
"""
Event Selection 
"""

__author__ = "XIAO Suyu <xiaosuyu@ihep.ac.cn>"
__copyright__ = "Copyright (c) XIAO Suyu"
__created__ = "[2017-12]" 

import sys
import os
import math 
import ROOT 
from progressbar import Bar, Percentage, ProgressBar
from time import time 
from tools import duration, check_outfile_path
from array import array
#import subprocess

#TEST=True 
TEST=False

# Global constants 
M_PSIP = 3.686;
ECMS = 3.686;

# Global histograms

h_evtflw = ROOT.TH1F('hevtflw', 'eventflow', 10, 0, 10) 
h_evtflw.GetXaxis().SetBinLabel(1, 'raw')
h_evtflw.GetXaxis().SetBinLabel(2, 'N_{#gamma}=2')
h_evtflw.GetXaxis().SetBinLabel(3, '|cos#theta|<0.75')
h_evtflw.GetXaxis().SetBinLabel(8, '3<M_{#gamma#gamma}^{rec}<3.75') 

h_mrec_gam1 = ROOT.TH1D('h_mrec_gam1', 'mrec_gam1', 100, 3.3, 3.7)
h_mrec_gamgam = ROOT.TH1D('h_mrec_gamgam', 'mrec_gamgam', 100, 0.0, 3.95)
h_Mgamgam = ROOT.TH1D('h_Mgamgam', 'Mgamgam', 100, 3, 4) 
h_gam1_p = ROOT.TH1D('h_gam1_p', 'gam1_p', 100, 0.0, 0.5) 
h_gam2_p = ROOT.TH1D('h_gam2_p', 'gam2_p', 100, 0.0, 0.5) 
h_gam1_costhe = ROOT.TH1D('h_gam1_costhe', 'gam1_costhe', 100, -1.0, 1.0)
h_gam1_E = ROOT.TH1D('h_gam1_E', 'gam1_E', 100, 0.0, 0.4)
h_gam2_costhe = ROOT.TH1D('h_gam2_costhe', 'gam2_costhe', 100, -1.0, 1.0)
h_ngam = ROOT.TH1D('h_ngam', 'ngam', 100, 0, 11)

# Global items
raw_gpx = ROOT.vector('double')()
raw_gpy = ROOT.vector('double')()
raw_gpz = ROOT.vector('double')()
raw_ge = ROOT.vector('double')()
raw_costheta = ROOT.vector('double')()
#m_pdgid = ROOT.vector('int')()
#m_pdgid = ROOT.array

ROOT.gROOT.ProcessLine(
"struct MyTreeStruct{\
   Double_t mrec_gam1_raw;\
};"	);

#   Double_t vtx_mrecgam1;\
#   Int_t run;\
#   Int_t event;\
#   Int_t indexmc;\

def usage():
    sys.stdout.write('''
NAME
    sel_events_inclusiveMC.py 

SYNOPSIS

    ./sel_events_inclusiveMC.py infile outfile 

AUTHOR 
    XIAO Suyu <xiaosuyu@ihep.ac.cn> 

DATE
    Dec 2017 
\n''')

    
def main():

    if TEST:
        sys.stdout.write('Run in TEST mode! \n')
    
    args = sys.argv[1:]
#    print sys.argv[0]
#    exit (0)

    if len(args) < 2:
        return usage()
    
    infile = args[0]
    outfile = args[1]
    check_outfile_path(outfile)

    fin = ROOT.TFile(infile)
    t = fin.Get('tree')
    t.SetBranchAddress("raw_gpx", raw_gpx)
    t.SetBranchAddress("raw_gpy", raw_gpy)
    t.SetBranchAddress("raw_gpz", raw_gpz)
    t.SetBranchAddress("raw_ge", raw_ge)
    t.SetBranchAddress("raw_costheta", raw_costheta)
    t.SetBranchAddress("raw_costheta", raw_costheta)
 #   t.SetBranchAddress("pdgid", m_pdgid, "pdgid[100]/I")
#    t.SetBranchAddress("motheridx", m_motheridx, "motheridx[100]/I")
    entries = t.GetEntriesFast()
 #   fout = ROOT.TFile(outfile, "RECREATE")
    fout = ROOT.TFile(outfile, "RECREATE")
    t_out = ROOT.TTree('tree', 'tree')
    mystruct = ROOT.MyTreeStruct()
#    t_out.Branch('vtx_mrecgam1', mystruct, 'vtx_mrecgam1/D')
    t_out.Branch('mrec_gam1_raw', mystruct, 'mrec_gam1_raw/D')
    t_out.Branch("raw_gpx", raw_gpx)
    t_out.Branch("raw_gpy", raw_gpy)
    t_out.Branch("raw_gpz", raw_gpz)
    t_out.Branch("raw_ge", raw_ge)
    t_out.Branch("raw_costheta", raw_costheta)
    n_run = array('i',[0])
    n_event = array('i',[0])
    n_indexmc = array('i',[0])
    t_out.Branch("run", n_run, "run/I")
    t_out.Branch("event", n_event, "event/I")
    t_out.Branch("indexmc", n_indexmc, "indexmc/I")
    n_pdgid = array('i', 100*[-99])
    n_motheridx = array('i', 100*[-99])
    t_out.Branch("pdgid", n_pdgid, "pdgid[100]/I")
    t_out.Branch("motheridx", n_motheridx, "motheridx[100]/I")

    pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=entries).start()
    time_start = time()

    for jentry in xrange(entries):
        pbar.update(jentry+1)
        # get the next tree in the chain and verify
        ientry = t.LoadTree(jentry)
        if ientry < 0:
            break
        # copy next entry into memory and verify

        if TEST and ientry > 10000:
            break
        
        if select_chic0_to_inclusive(t): 
#            h_mrecgam1.Fill(t.vtx_mrecgam1)
#            mystruct.vtx_mrecgam1 = t.vtx_mrecgam1
            t_out.Fill()
            fill_histograms(t)
 
        nb = t.GetEntry(jentry)
        if nb<=0:
            continue
        n_run[0] = t.run
        n_event[0] = t.event
        n_indexmc[0] = t.m_indexmc
        for ii in range(t.m_indexmc):
            n_pdgid[ii] = t.m_pdgid[ii]
            n_motheridx[ii] = t.m_motheridx[ii]
        
    t_out.Write()
    write_histograms() 
    fout.Close()
    pbar.finish()
    
    dur = duration(time()-time_start)
    sys.stdout.write(' \nDone in %s. \n' % dur) 

def fill_histograms(t):
    if (len(raw_ge) == 2):
        gam1_index = -1
        gam2_index = -1
#    t = m_raw_ge.size()
        if (raw_ge[0] < raw_ge[1]):
            gam1_index = 0
            gam2_index = 1
        else:
            gam1_index = 1
            gam2_index = 0

        gam1_p4_raw = ROOT.TLorentzVector(t.raw_gpx.at(gam1_index), t.raw_gpy.at(gam1_index), t.raw_gpz.at(gam1_index), t.raw_ge.at(gam1_index))    
        gam2_p4_raw = ROOT.TLorentzVector(t.raw_gpx.at(gam2_index), t.raw_gpy.at(gam2_index), t.raw_gpz.at(gam2_index), t.raw_ge.at(gam2_index))    
        cms_p4 = ROOT.TLorentzVector(0.011*ECMS, 0, 0, ECMS)
        gamgam_p4_raw = gam1_p4_raw + gam2_p4_raw
        rec_gam1_p4_raw = cms_p4 - gam1_p4_raw
        rec_gamgam_p4_raw = cms_p4 - gamgam_p4_raw
        Mgamgam = gamgam_p4_raw.M()
        mrec_gam1_raw = rec_gam1_p4_raw.M()
        mrec_gamgam_raw = rec_gamgam_p4_raw.M()

        cut_ngam = (t.ngam == 2)
#        cut_ngam = (t.ngam < 11)
        cut_gam1_costhe = (abs(t.raw_costheta.at(gam1_index)) < 0.75)
        cut_gam2_costhe = (abs(t.raw_costheta.at(gam2_index)) < 0.75)
   #     cut_mgamgam = (t.vtx_mgamgam > 3.0 and t.vtx_mgamgam < 3.75)
        cut_pi0 = (Mgamgam < 0.10 or Mgamgam > 0.16)
        cut_eta = (Mgamgam < 0.50 or Mgamgam > 0.57)
        cut_chic = (Mgamgam < 3.22 or Mgamgam > 3.75)
        cut_egam = (t.raw_ge.at(gam1_index) < t.raw_ge.at(gam2_index))
	# don't know how to tag gam1 and gam2
    #    if (cut_ngam and cut_gam1_costhe and cut_gam2_costhe and cut_mgamgam and cut_egam):
        if (cut_ngam and cut_egam and cut_pi0 and cut_eta and cut_chic):
#        if (cut_ngam and cut_egam and cut_gam1_costhe and cut_gam2_costhe):
#        if (cut_ngam):
            h_Mgamgam.Fill(Mgamgam)
            h_mrec_gam1.Fill(mrec_gam1_raw)
            h_mrec_gamgam.Fill(mrec_gamgam_raw)
#            h_gam1_p.Fill(t.(gam1_index))
#            h_gam2_p.Fill(t.gam2_p)
            h_gam1_costhe.Fill(t.raw_costheta.at(gam1_index))
            h_gam1_E.Fill(t.raw_ge.at(gam1_index))
            h_gam2_costhe.Fill(t.raw_costheta.at(gam2_index))
            h_ngam.Fill(t.ngam)

def write_histograms():
    h_evtflw.Write()
    h_mrec_gam1.Write()
    h_mrec_gamgam.Write()
    h_Mgamgam.Write()
#    h_gam1_p.Write()
#    h_gam2_p.Write()
    h_gam1_costhe.Write()
    h_gam1_E.Write()
    h_gam2_costhe.Write()
    h_ngam.Write()

    
def select_chic0_to_inclusive(t):
    h_evtflw.Fill(0) 

    if not (t.ngam == 2):
        return False
    h_evtflw.Fill(1) 
 
#    if not ( (abs(t.raw_costheta.at(gam1_index)) < 0.75) and abs(t.raw_costheta.at(gam2_index)) < 0.75 ):
#        return False
#    h_evtflw.Fill(2) 
 
#    if not (t.raw_ge.at(gam1_index) < t.raw_ge.at(gam2_index)):
#        return False
#    h_evtflw.Fill(3) 
 
#    if not ((Mgamgam < 0.12 or Mgamgam > 0.14) and (Mgamgam < 0.53 or Mgamgam > 0.57)):
#        return False
#    h_evtflw.Fill(4) 

#    for i in range(1, 3):
#        if not ( t.raw_costheta.at(i) < 0.75 and t.raw_costheta.at(i) > -0.75):
#            return False
#        h_evtflw.Fill(2) 

#    if not ( t.vtx_mrecgam1 > 3 and t.vtx_mrecgam1 < 3.75):
#        return False
#    h_evtflw.Fill(3) 
    
    return True
    
    
if __name__ == '__main__':
    main() 
