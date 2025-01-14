# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 21:07:44 2021

@author: bensr
"""
import argparse
import numpy as np
from vm_plotter import *
from neuron import h
import json
from scipy.signal import find_peaks
import matplotlib.backends.backend_pdf

h.load_file("runModel.hoc")
soma_ref = h.root.sec
soma = h.secname(sec=soma_ref)
sl = h.SectionList()
sl.wholetree(sec=soma_ref)
def init_settings(nav12=1,
                  nav16=1,
                  dend_nav12=1, 
                  soma_nav12=1, 
                  ais_nav12=1, 
                  dend_nav16=1, 
                  soma_nav16=1,
                  ais_nav16=1, 
                  axon_Kp=1,
                  axon_Kt =1,
                  axon_K=1,
                  soma_K=1,
                  dend_K=1,
                  gpas_all=1):

    h.dend_na12 = 0.026145/2 
    h.dend_na16 = h.dend_na12 
    h.dend_k = 0.004226 * soma_K


    h.soma_na12 = 0.983955/10 
    h.soma_na16 = h.soma_na12 
    h.soma_K = 0.303472 * soma_K

    h.ais_na16 = 4 
    h.ais_na12 = 4 
    h.ais_ca = 0.000990
    h.ais_KCa = 0.007104

    h.node_na = 2

    h.axon_KP = 0.973538 * axon_Kp
    h.axon_KT = 0.089259 * axon_Kt
    h.axon_K = 1.021945 * axon_K

    h.cell.axon[0].gCa_LVAstbar_Ca_LVAst = 0.001376286159287454
    
    #h.soma_na12 = h.soma_na12/2
    h.naked_axon_na = h.soma_na16/5
    h.navshift = -10
    h.myelin_na = h.naked_axon_na
    h.myelin_K = 0.303472
    h.myelin_scale = 10
    h.gpas_all = 3e-5 * gpas_all
    h.cm_all = 1
    
    
    h.dend_na12 = h.dend_na12 * nav12 * dend_nav12
    h.soma_na12 = h.soma_na12 * nav12 * soma_nav12
    h.ais_na12 = h.ais_na12 * nav12 * ais_nav12
    
    h.dend_na16 = h.dend_na16 * nav16 * dend_nav16
    h.soma_na16 = h.soma_na16 * nav16 * soma_nav16
    h.ais_na16 = h.ais_na16 * nav16 * ais_nav16
    h.working()
  

def update_na16(dict_fn,wt_mul,mut_mul):
    with open(dict_fn) as f:
        data = f.read()
    param_dict = json.loads(data)
    for curr_sec in sl:
        if h.ismembrane('na16mut', sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = f'{curr_name}.gbar_na16mut({seg.x}) *= {mut_mul}'
                print(hoc_cmd)
                h(hoc_cmd)
            for p_name in param_dict.keys():
                hoc_cmd = f'{curr_name}.{p_name} = {param_dict[p_name]}'
                print(hoc_cmd)
                h(hoc_cmd)
        if h.ismembrane('na16', sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = f'{curr_name}.gbar_na16({seg.x}) *= {wt_mul}'
                print(hoc_cmd)
                h(hoc_cmd)

def update_K(channel_name,gbar_name,mut_mul):
    k_name = f'{gbar_name}_{channel_name}'
    prev = []
    for curr_sec in sl:
        if h.ismembrane(channel_name, sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = f'{curr_name}.{k_name}({seg.x}) *= {mut_mul}'
                print(hoc_cmd)
                h(f'a = {curr_name}.{k_name}({seg.x})')  # get old value
                prev_var = h.a
                prev.append(f'{curr_name}.{k_name}({seg.x}) = {prev_var}')  # store old value in hoc_cmd
                h(hoc_cmd)
    return prev

def reverse_update_K(channel_name,gbar_name, prev):
    k_name = f'{gbar_name}_{channel_name}'
    index = 0
    for curr_sec in sl:
        if h.ismembrane(channel_name, sec=curr_sec):
            curr_name = h.secname(sec=curr_sec)
            for seg in curr_sec:
                hoc_cmd = prev[index]
                h(hoc_cmd)
                index += 1
    
def init_stim(sweep_len = 800, stim_start = 100, stim_dur = 500, amp = 0.3, dt = 0.1):
    # updates the stimulation params used by the model
    # time values are in ms
    # amp values are in nA
    
    h("st.del = " + str(stim_start))
    h("st.dur = " + str(stim_dur))
    h("st.amp = " + str(amp))
    h.tstop = sweep_len
    h.dt = dt


def get_fi_curve(s_amp,e_amp,nruns,wt_data=None,ax1=None):
    all_volts = []
    npeaks = []
    x_axis = np.linspace(s_amp,e_amp,nruns)
    stim_length = int(600/dt)
    for curr_amp in x_axis:
        init_stim(amp = curr_amp)
        curr_volts,_,_,_ = run_model(dt=0.5)
        curr_peaks,_ = find_peaks(curr_volts[:stim_length],height = -20)
        all_volts.append(curr_volts)
        npeaks.append(len(curr_peaks))
    #print(npeaks)
    #if ax1 is None:
    #    fig,ax1 = plt.subplots(1,1)
    #ax1.plot(x_axis,npeaks,'black')
    #ax1.set_title('FI Curve')
    #ax1.set_xlabel('Stim [nA]')
    #ax1.set_ylabel('nAPs for 500ms epoch')
    #if wt_data is None:
    #    return npeaks
    #else:
    #    ax1.plot(x_axis,npeaks,'blue')
    #    ax1.plot(x_axis,wt_data,'black')
    #plt.show()
    #print("XAXIS", x_axis)
    #print("PEAK", npeaks)
    return [x_axis, npeaks]


def run_model(start_Vm = -72,dt= 0.1):
    h.finitialize(start_Vm)
    timesteps = int(h.tstop/h.dt)
    
    Vm = np.zeros(timesteps)
    I = {}
    I['Na'] = np.zeros(timesteps)
    I['Ca'] = np.zeros(timesteps)
    I['K'] = np.zeros(timesteps)
    stim = np.zeros(timesteps)
    t = np.zeros(timesteps)
    
    for i in range(timesteps):
        Vm[i] = h.cell.soma[0].v
        I['Na'][i] = h.cell.soma[0](0.5).ina
        I['Ca'][i] = h.cell.soma[0](0.5).ica
        I['K'][i] = h.cell.soma[0](0.5).ik
        stim[i] = h.st.amp 
        t[i] = i*h.dt / 1000
        h.fadvance()
        
    return Vm, I, t,stim


def plot_stim(amp,fn,clr='blue'):
    init_stim(amp=amp)
    Vm, I, t, stim = run_model()
    plot_stim_volts_pair(Vm, f'Step Stim {amp}pA', file_path_to_save=f'./Plots/V1/{fn}_{amp}pA',times=t,color_str=clr)
    return I

#def make_fi(ranges,fn):
    # not used
#    fig,ficurveax = plt.subplots(1,1)
#    get_fi_curve(ranges[0], ranges[1], ranges[2],ax1 = ficurveax)
#    fig.savefig(f'./Plots/Kexplore/{fn}_FI.pdf')
    

def cultured_neurons_wt(extra,fi_ranges,label):
    update_na16('./params/na16_mutv2.txt',2+extra,0)
    plot_stim(0.5,f'{label}_overexpressedWT{extra}')
    #make_fi(fi_ranges,f'{label}_overexpressedWT{extra}')
    #name = f'{label} WT {extra}' # label is ch_name and condition
    name = f'WT'
    x_axis, npeaks = get_fi_curve(fi_ranges[0], fi_ranges[1], fi_ranges[2])
    #fig.savefig(f'./Plots/Kexplore/{fn}_FI.pdf')
    return [x_axis, npeaks, name]


def cultured_neurons_mut(extra,fi_ranges,label):
    update_na16('./params/na16_mutv2.txt',2,extra)
    plot_stim(0.5,f'{label}_overexpressedMut{extra}')
    #make_fi(fi_ranges,f'{label}_overexpressedMut{extra}')
    #name = f'{label} Mut {extra}'
    name = f'Mut'
    x_axis, npeaks = get_fi_curve(fi_ranges[0], fi_ranges[1], fi_ranges[2])
    return [x_axis, npeaks, name]
    
def cultured_neurons_wtTTX(extra,fi_ranges,label):
    update_na16('./params/na16_mutv2.txt',extra,0)
    plot_stim(2,f'{label}_overexpressedWT_TTX{extra}')
    #make_fi(fi_ranges,f'{label}_overexpressedWT_TTX{extra}')
    #name = f'{label} WT_TTX {extra}'
    name = f'WT_TTX'
    x_axis, npeaks = get_fi_curve(fi_ranges[0], fi_ranges[1], fi_ranges[2])
    return [x_axis, npeaks, name]

def cultured_neurons_mutTTX(extra,fi_ranges,label):
    update_na16('./params/na16_mutv2.txt',0,extra)
    plot_stim(2,f'{label}_overexpressedmut_TTX{extra}')
    #make_fi(fi_ranges,f'{label}_overexpressedmut_TTX{extra}')
    #name = f'{label} mut_TTX {extra}'
    name = f'mut_TTX'
    x_axis, npeaks = get_fi_curve(fi_ranges[0], fi_ranges[1], fi_ranges[2])
    return [x_axis, npeaks, name]

def explore_param(ch_name, gbar_name, ranges, extras):
    all_prevs = []
    all_FIs = []

    for i in range(len(ranges)):
        init_settings()
        curr_factor = ranges[i]
        extra = np.round(extras[i], 2)
        prev = update_K(ch_name, gbar_name, curr_factor)
        label = f'{ch_name}_{curr_factor}'
        fi_wt = cultured_neurons_wt(extra, [0.1, 1, 5],
                                    label)  # set endpoint from 5 to 6 for even spacing across types
        fi_mut = cultured_neurons_mut(extra, [0.1, 1, 5],
                                      label)  # set endpoint from 5 to 6 for even spacing across types
        fi_wtTTX = cultured_neurons_wtTTX(extra, [0.4, 2, 5], label)
        fi_mutTTX = cultured_neurons_mutTTX(extra, [0.4, 2, 5], label)
        all_prevs.append(prev)
        all_FIs.append([fi_wt, fi_mut, fi_wtTTX, fi_mutTTX])

        reverse_update_K(ch_name, gbar_name, all_prevs[0])
    # plot FIs
    plot_all_FIs(all_FIs, ch_name, ranges, extras)

    # revert h back to initial condition
    #reverse_update_K(ch_name, gbar_name, all_prevs[0])

#running with the decided paramters (gSKV3.1x2 and extra of 0.1)

def plot_wt_vs_ttx(fi_arr):
    init_settings()
    extra = 0.1
    k_factor = 2
    prev = update_K('SKv3_1','gSKv3_1bar', k_factor)
    label = f'FI_curves'
    fi_wt = cultured_neurons_wt(extra, fi_arr,label)
    fi_mut = cultured_neurons_mut(extra, fi_arr,label)
    fi_wtTTX = cultured_neurons_wtTTX(extra, fi_arr, label)
    fi_mutTTX = cultured_neurons_mutTTX(extra, fi_arr, label)
    all_FIs = [fi_wt, fi_mut, fi_wtTTX, fi_mutTTX]
    plot_all_FIs(all_FIs)
def plot_wt_vs_het(fi_ranges):
    init_settings()
    k_factor = 2
    prev = update_K('SKv3_1','gSKv3_1bar', k_factor)
    label = f'WT_500pA'
    #NO MUT AND 2 ALLELS OF WT
    update_na16('./params/na16_mutv2.txt',2,0)
    plot_stim(0.5,label,clr='black')
    wt_x_axis, wt_npeaks = get_fi_curve(fi_ranges[0], fi_ranges[1], fi_ranges[2])
    reverse_update_K('SKv3_1','gSKv3_1bar', prev)
    init_settings()
    prev = update_K('SKv3_1','gSKv3_1bar', k_factor)
    update_na16('./params/na16_mutv2.txt',1,1)
    label = f'Het_500pA'
    plot_stim(0.5,label,clr='red')
    het_x_axis, het_npeaks = get_fi_curve(fi_ranges[0], fi_ranges[1], fi_ranges[2])
    fig = plt.figure()
    plt.plot(wt_x_axis, wt_npeaks, label='WT', color='black')
    plt.plot(het_x_axis, het_npeaks, label='HET', color='red')
    filename= f'./Plots/V1/FI_Het_plots.pdf'
    fig.savefig(filename)

def plot_all_FIs(condition_data):
    # save multiple figures in one pdf file
    filename= f'./Plots/V1/FI_WT_MUT_TTX_WT_plots.pdf'
    fig = plt.figure()
    x_axis, npeaks, name = condition_data[0]
    plt.plot(x_axis, npeaks, label=name, color='black')
    # plot mut
    x_axis, npeaks, name = condition_data[1]
    plt.plot(x_axis, npeaks, label=name, color='red')
    # plot wtTTX
    x_axis, npeaks, name = condition_data[2]
    plt.plot(x_axis, npeaks, label=name, color='black', linestyle='dashed')
    # plot mutTTX
    x_axis, npeaks, name = condition_data[3]
    plt.plot(x_axis, npeaks, label=name, color='red', linestyle='dashed')

    plt.legend()
    plt.xlabel('Stim [nA]')
    plt.ylabel('nAPs for 500ms epoch')
    plt.title(f'FI Curve: WT vs MUT with and without TTX')
    fig.savefig(filename)
    
def het_sims():
    init_settings()
    update_na16('./params/na16_mutv2.txt',1,1)
    init_stim(amp=0.5)
    Vm, I, t, stim = run_model()
    plot_stim_volts_pair(Vm, 'Step Stim 500pA', file_path_to_save=f'./Plots/hetrozygous_500pA',times=t,color_str='blue')


#######################
# MAIN
#######################



#explore_param('','equal_expression', [1])



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate simulated data.')
    parser.add_argument("--function", "-f", type=int, default=0, help="Specify which function to run")
    #plot simulation for cultured neurons with and without ttx
    args = parser.parse_args()
    if args.function == 0:
        plot_wt_vs_ttx([0,1.8, 10])
     #plot simulation for WT and Hetrozygous
    if args.function == 1:
        plot_wt_vs_het([0,1.8, 10])
        
    if args.function == 2:
        #gK_Tstbar_K_Tst
        #gK_Pstbar_
        #update_K('SKv3_1','gSKv3_1bar',2)
        #update_K('K_Tst','gK_Tstbar',2)
        #update_K('K_Pst','gK_Pstbar',2)
        #cultured_neurons_mut(0.25,[0.1, 1, 5])
        #cultured_neurons_wt(0.5,[0.1, 1, 5])
        #cultured_neurons_wtTTX(0.5,[0.4, 2, 6])
        #cultured_neurons_mutTTX(0.25,[0.4, 2, 6])


        # run 3
        conditions = np.repeat(2, 5) # factors
        extras = np.arange(0.1, 0.6, 0.1)
        explore_param('SKv3_1','gSKv3_1bar', conditions, extras)
        #explore_param('K_Tst','gK_Tstbar', [1, 10, 100])
        #explore_param('K_Pst','gK_Pstbar', [1, 2, 3])

        if args.function == 3:
            # run 1
            extras = np.repeat(0.25, 3)  # for mut channel # HOLD WT AT 0.5 (need to adjust code for this)
            explore_param('SKv3_1', 'gSKv3_1bar', [1, 2, 3], extras)
            explore_param('K_Tst','gK_Tstbar', [1, 10, 100], extras)
            explore_param('K_Pst','gK_Pstbar', [1, 2, 3], extras)

        if args.function == 4:
            # run 2
            init_settings()

            #create mutTTX
            init_stim(amp=0.5)
            update_na16('./params/na16_mutv2.txt',0,0.25)
            update_K('SKv3_1','gSKv3_1bar',2)
            I = plot_stim(2,f'mut_overexpressedmut_TTX_0.25')
            fig,ax1 = plt.subplots(1,1)
            ax1.plot(I['Na'],color = 'black')
            ax1.plot(I['K'],color = 'blue')
            ax1.plot(I['Ca'],color = 'green')
            fig.savefig('./Plots/mut_vclamp.pdf')


