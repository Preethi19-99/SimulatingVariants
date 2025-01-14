""" VClamp SCN2A Variants (HMM)
 Generates simulated data for voltage-gated channel
 Hidden Markov Model
 Modified from Emilio Andreozzi "Phenomenological models of NaV1.5.
    # A side by side, procedural, hands-on comparison between
    # Hodgkin-Huxley and kinetic formalisms." 2019
 Contributors: Emily Nguyen UC Berkeley, Roy Ben-Shalom UCSF
"""

from neuron import h, gui
import numpy as np
from numpy import trapz
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from scipy import optimize, stats
import argparse
import os
from state_variables import finding_state_variables
import pickle
import curve_fitting as cf

from generate_simulation import *

# from sys import api_version
# from test.pythoninfo import collect_platform

##################
# Global
##################
# Create folder in CWD to save plots
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'Plots_Folder')
if not os.path.exists(final_directory):
    os.makedirs(final_directory)


##################
# Activation
##################
class Activation(Activation_general):

    def clamp(self, v_cl):
        """ Runs a trace and calculates peak currents.
        Args:
            v_cl (int): voltage to run
        """
        curr_tr = 0  # initialization of peak current
        h.finitialize(self.v_init)  # calling the INITIAL block of the mechanism inserted in the section.
        pre_i = 0  # initialization of variables used to commute the peak current
        dens = 0
        self.f3cl.amp[1] = v_cl  # mV

        for _ in self.ntrials:
            while h.t < h.tstop:  # runs a single trace, calculates peak current
                dens = self.f3cl.i / self.soma(0.5).area() * 100.0 - self.soma(
                    0.5).i_cap  # clamping current in mA/cm2, for each dt

                self.t_vec.append(h.t)
                self.v_vec_t.append(self.soma.v)
                self.i_vec.append(dens)

                if (h.t > 5) and (h.t <= 10):  # evaluate the peak
                    if abs(dens) > abs(pre_i):
                        curr_tr = dens  # updates the peak current

                h.fadvance()
                pre_i = dens

                # find i peak of trace
        peak,ttp = self.find_ipeaks()
        self.ipeak_vec.append(peak)
        self.ttp_vec.append(ttp)

    def clamp_at_volt(self, v_cl):
        self.t_vec = []
        self.v_vec_t = []
        self.i_vec = []
        """ Runs a trace and calculates peak currents.
        Args:
            v_cl (int): voltage to run
        """
        if self.gnorm_vec == []:
            time_padding = 5  # ms
            h.tstop = time_padding + self.dur + time_padding  # time stop
            
        curr_tr = 0  # initialization of peak current
        h.finitialize(self.v_init)  # calling the INITIAL block of the mechanism inserted in the section.
        pre_i = 0  # initialization of variables used to commute the peak current
        dens = 0
        self.f3cl.amp[1] = v_cl  # mV
        for _ in self.ntrials:
            while h.t < h.tstop:  # runs a single trace, calculates peak current
                dens = self.f3cl.i / self.soma(0.5).area() * 100.0 - self.soma(
                    0.5).i_cap  # clamping current in mA/cm2, for each dt
                # append data
                self.t_vec.append(h.t)
                self.v_vec_t.append(self.soma.v)
                self.i_vec.append(dens)
                # advance
                h.fadvance()

        # find i peak of trace
        peak,ttp = self.find_ipeaks()
        self.ipeak_vec.append(peak)
        self.ttp_vec.append(ttp)



##################
# Inactivation
##################
class Inactivation(Inactivation_general):

    def clamp(self, v_cl):
        """ Runs a trace and calculates peak currents.
        Args:
            v_cl (int): voltage to run
        """
        self.f3cl.amp[1] = v_cl
        h.finitialize(self.v_init)  # calling the INITIAL block of the mechanism inserted in the section.

        # parameters initialization
        peak_curr = 0
        t_peak = 0
        dtsave = h.dt

        for _ in self.ntrials:
            while h.t < h.tstop:  # runs a single trace, calculates peak current
                if (h.t > 537) or (h.t < 40):
                    h.dt = dtsave
                else:
                    h.dt = 1
                dens = self.f3cl.i / self.soma(0.5).area() * 100.0 - self.soma(
                    0.5).i_cap  # clamping current in mA/cm2, for each dt
                self.t_vec.append(h.t)  # code for store the current
                self.v_vec_t.append(self.soma.v)  # trace to be plotted
                self.i_vec.append(dens)  # trace to be plotted

                if (h.t >= 540) and (h.t <= 542):  # evaluate the peak
                    if abs(dens) > abs(peak_curr):
                        peak_curr = dens
                        t_peak = h.t

                h.fadvance()

        # updates the vectors at the end of the run
        self.ipeak_vec.append(peak_curr)

##################
# Recovery from Inactivation (RFI)
# &  RFI Tau
##################
class RFI(RFI_general):
    def placeholder(self):
        return None


##################
# Ramp Protocol
##################
class Ramp(Ramp_general):



    def persistentCurrent(self):
        """ Calculates persistent current (avg current of last 100 ms at 0 mV)
        Normalized by peak from IV (same number as areaUnderCurve).
        """
        persistent = self.i_vec[self.t_start_persist:self.t_end_persist]
        act = Activation()
        act.genActivation()
        IVPeak = min(act.ipeak_vec)
        return (sum(persistent) / len(persistent)) / IVPeak


##################
# UDB20 Protocol
##################
class UDB20(UDB20_general):
    def placeholder(self):
        return None
  

##################
# RFI dv tau
##################
class RFI_dv(RFI_dv_general):
    def placeholder(self):
        return None
