###########################3
## Functions for fitting sigmoid curves to activation and inactivation as well as
## 2 phase inactivation for recovery.
## Author: Michael Lam, adapted from code in optimize_na_ga_v2

import matplotlib.pyplot as plt
import numpy as np
import eval_helper as eh
import generalized_genSim_shorten_time as ggsd
from scipy import optimize, stats

def fit_sigmoid(x, slope, v_half, top, bottom):
    '''
    Fit a sigmoid curve to the array of datapoints.
    '''
    return bottom +  ((top - bottom) / (1.0 + np.exp((v_half - x)/slope)))

def fit_two_phase_association(x, y0, plateau, percent_fast, k_fast, k_slow):
    '''
    Fit a two-phase association curve to an array of data points X. 
    For info about the parameters, visit 
    https://www.graphpad.com/guides/prism/latest/curve-fitting/REG_Exponential_association_2phase.htm
    '''
    span_fast = (plateau - y0) * percent_fast * 0.01
    span_slow = (plateau - y0) * (100 - percent_fast) * 0.01
    return y0 + span_fast * (1 - np.exp(-k_fast * x)) + span_slow * (1 - np.exp(-k_slow * x))

class Curve_Fitter:

    def __init__(self):
        self.activation = ggsd.Activation()
        self.inactivation = ggsd.Inactivation()
        self.recovery = ggsd.RFI()

    def gen_figure_given_params(self, params, save=True, file_name=None,mutant='N_A', exp='N_A',rmse=None, plot=False):
        #set-up figure
        param_dict = {}
        plt.close()
        fig, axs = plt.subplots(3, figsize=(10,10))
        fig.suptitle("Mutant: {} \n Experiment: {}".format(mutant, exp))
        # Inactivation curve
        inorm_vec, v_vec, all_is = self.inactivation.genInactivation()
        inorm_array = np.array(inorm_vec)
        v_array = np.array(v_vec)
        ssi_slope, v_half, top, bottom = self.calc_inact_obj()
        even_xs = np.linspace(v_array[0], v_array[len(v_array)-1], 100)
        curve = fit_sigmoid(even_xs, ssi_slope, v_half, top, bottom)
        axs[0].set_xlabel('Voltage (mV)')
        axs[0].set_ylabel('Fraction Inactivated')
        axs[0].set_title("Inactivation Curve")
        axs[0].scatter(v_array, inorm_array, color='black',marker='s')
        axs[0].plot(even_xs, curve, color='red', label="Inactivation")
        axs[0].text(-10, 0.5, 'Slope: ' + str(ssi_slope) + ' /mV')
        axs[0].text(-10, 0.3, 'V50: ' + str(v_half) + ' mV')
        axs[0].legend()

        # Activation curve
        gnorm_vec, v_vec, all_is = self.activation.genActivation()
        gnorm_array = np.array(gnorm_vec)
        v_array = np.array(v_vec)
        gv_slope, v_half, top, bottom = self.calc_act_obj()
        even_xs = np.linspace(v_array[0], v_array[len(v_array)-1], 100)
        curve = fit_sigmoid(even_xs, gv_slope, v_half, top, bottom)
        axs[1].set_xlabel('Voltage (mV)')
        axs[1].set_ylabel('Fraction Activated')
        axs[1].set_title("Activation Curve")
        axs[1].scatter(v_array, gnorm_array, color='black',marker='s')
        axs[1].plot(even_xs, curve, color='red', label="Activation")
        axs[1].text(-10, 0.5, 'Slope: ' + str(gv_slope) + ' /mV')
        axs[1].text(-10, 0.3, 'V50: ' + str(v_half) + ' mV')
        axs[1].legend()
        
        # Recovery Curve
        #axs[2].set_xlabel('Log(Time)')
        #axs[2].set_ylabel('Fractional Recovery')
        #axs[2].set_title("Recovery from Inactivation")
        #even_xs = np.linspace(times[0], times[len(times)-1], 100)
        #curve = fit_two_phase_association(even_xs, *popt)
        #axs[2].plot(np.log(even_xs), curve, c=fit_color,label="Recovery Fit")
        #axs[2].scatter(np.log(times), data_pts, label='Recovery', color=fit_color,marker=curr_marker)
        plt.show()

    def calc_act_obj(self):
        gnorm_vec, v_vec, all_is = self.activation.genActivation()
        try:
            popt, pcov = optimize.curve_fit(fit_sigmoid, v_vec, gnorm_vec)
        except:
            print("Very bad voltages in activation.")
            return
        gv_slope, v_half, top, bottom = popt
        return gv_slope, v_half, top, bottom


    def calc_inact_obj(self):
        inorm_vec, v_vec, all_is = self.inactivation.genInactivation()
        try:
            popt, pcov = optimize.curve_fit(fit_sigmoid, v_vec, inorm_vec)
        except:
            print("Very bad voltages in inactivation.")
            return
        ssi_slope, v_half, top, bottom = popt
        return ssi_slope, v_half, top, bottom

    def calc_recov_obj(self):
        return
