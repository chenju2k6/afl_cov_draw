#!/usr/bin/env python

import os
import sys

import numpy as np
# import statsmodels.api as sm
import scipy.stats as st

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import math
import matplotlib.ticker as ticker

# import plottools

matplotlib.rcParams.update({'font.size': 35})
matplotlib.rcParams.update({'figure.dpi': 96})

from pprint import pprint
import json


# g_type = 'png'
g_type = 'pdf'

g_cov_root = 'cov_data'
# g_cov_root2 = '/home/jinghan/cju/ccs_ext'

g_cbs = ['nm', 'objdump', 'readelf', 'size']
#g_cbs = ['objdump', 'readelf', 'size', 'libjpeg','vorbis','libpng','proj','woff2']
#g_cbs = ['proj']
g_trials = range(0,20)

#g_labels = ['AFL++', 'SEMCE6', 'SEMCE9', 'WEIZZ'] #'JIGSAW-SAMPLING', 'Z3-MULIT']
#g_labels = ['SEMCE6', 'SEMCE9', 'SEMCE10', 'SEMCE11', 'SEMCE12', 'SEMCE13'] #'JIGSAW-SAMPLING', 'Z3-MULIT']
#g_labels = ['Z310S16', 'Z350MS16','JIGSAW16Z'] #'JIGSAW-SAMPLING', 'Z3-MULIT']
#g_labels = ['JIGSAW', 'Angora', 'Z310S', 'Z350MS','NEUZZ', 'QSYM', 'FUZZOLIC', 'AFL++'] #'JIGSAW-SAMPLING', 'Z3-MULIT']
g_labels = ['SymCC', 'SymSan'] #'JIGSAW-SAMPLING', 'Z3-MULIT']
#g_labels = ['SymSanAFL'] #'JIGSAW-SAMPLING', 'Z3-MULIT']

g_colors = ['orangered', 'green', 'navy', 'blue', 'brown', 'black', 'gold', 'purple']

g_markers = ['o', 's', 'd', 'x', '^', 'v', '<', '>']

g_maxtime = 24 * 3600


def read_tcov(cov_fp):
    with open(cov_fp, 'r') as f:
        lines = f.readlines()

    lines = [l.strip().split(',') for l in lines]

    tcov = []
    for i, x in enumerate(lines):
        t = int(x[2])
        v = int(x[1])
        if i + 1 < len(lines):
            tn = int(lines[i+1][2])
            t = min(t, tn)
        tcov.append( (t, v) )

    # tcov = [(int(v[2]), int(v[1])) for v in tcov]

    # t0 = tcov[0][0]

    # # tx = tcov[-1][0]
    # # for t, _ in tcov:
    # #     if tx - t <= g_maxtime + 3600:
    # #         t0 = t
    # #         break

    # for t, _ in tcov:
    #     if t == t0:
    #         continue

    #     if t - t0 > 1000:
    #         t0 = t

    #     break
    
    # tcov = [(max(t - t0, 0), v) for t, v in tcov]

    # pprint(tcov)
    return tcov





def gen_seq(tcov):
    seq = dict()

    for t, c in tcov:
        #if t >= g_maxtime:
        #    break

        seq[t] = c
    
    ts = sorted(seq.keys())
    for k, v in list(seq.items()):
        if k > g_maxtime:
            del seq[k]
    ts.append(g_maxtime)
    n_len = len(seq)

    for i in range(n_len):
        t1 = ts[i]
        t2 = ts[i+1]

        for tx in range(t1, t2):
            seq[tx] = seq[t1]
    # print(seq)
    # print(sorted(seq.keys())[-1])
    seq[0] = tcov[0][1]

    return sorted(seq.values())



def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)

    if n == 1:
        m = a[0]
        m1 = m
        m2 = m
    else:
        m, se = np.mean(a), st.sem(a)
        # h = se * st.t.ppf((1 + confidence) / 2., n-1)
        # m1 = m - h
        # m2 = m + h
        m1, m2 = st.norm.interval(confidence, loc=m, scale=se)

    return m, m1, m2



# def collect_data(cb_dir):
#     all_seqs = {l:[] for l in g_labels}

#     for l in g_labels:
#         for i in g_trials:
#             cov_fp = os.path.join(cb_dir, '{}_{}'.format(l, i), 'default', 'cov_data')
#             if os.path.exists(cov_fp):
#                 tcov = read_tcov(cov_fp)
#                 seq = gen_seq(tcov)
#                 all_seqs[l].append(seq)

#     all_data = dict()

#     for l in g_labels:
#         merge = list(zip(*all_seqs[l]))
#         # print(merge)
#         data = [mean_confidence_interval(v) for v in merge]
#         # print(data)
#         data = list(zip(*data))
#         all_data[l] = data
#     # print(all_data)
#     return all_data


def find_pre(l1, l2):
    n = min(len(l1), len(l2))
    m1 = -1
    m2 = -1
    for i in range(n):
        if l1[i][0] != l2[i][0]:
            m1 = i
            break
    for i in range(n):
        if l1[i][1] != l2[i][1]:
            m2 = i 
            break
    
    return max(m1, m2)


def collect_data(cb):

    all_data = dict()

    for l in g_labels:

        # if l in ['JIGSAW-SAMPLING', 'Z3-MULIT']:
            # cb_dir = os.path.join(g_cov_root2, cb)

        # else:
        
        cb_dir = os.path.join(g_cov_root, cb)

        tcov_v = []
        for i in g_trials:
            cov_fp = os.path.join(cb_dir, '{}_{}'.format(l.split('-')[0], i), 'default', 'cov_data')
            if os.path.exists(cov_fp):
                tcov = read_tcov(cov_fp)
                # seq = gen_seq(tcov)
                tcov_v.append(tcov)

        start = 0
        if len(tcov_v) > 2:
            start = max(0, find_pre(tcov_v[0], tcov_v[1]) )
        
        print ('  ', l, start)
        
        seqs = []
        for tcov in tcov_v:
            t0 = tcov[start][0]
            for t, _ in tcov[start:]:
                if t == t0:
                    continue
                if t - t0 > 1000:
                    t0 = t
                break

            tcov_x = [(max(0, t - t0), v) for t, v in tcov]
            seq = gen_seq(tcov_x)
            seqs.append(seq)
        
        merge = list(zip(*seqs))
        # print '    ', merge[:2]
        data = [mean_confidence_interval(v) for v in merge]
        # print(data)
        data = list(zip(*data))
        all_data[l] = data
    # print(all_data)
    return all_data



def store_data(cb, data):
    with open('{}_cov.data'.format(cb), 'w+') as f:
        json.dump(data, f)


def load_data(cb):
    with open('{}_cov.data'.format(cb), 'r') as f:
        data = json.load(f)
    return data


def fmt(val):
    if val < 60:
        return '{0:g}s'.format(val)
    elif val < 3600:
        return '{0:g}m'.format(val / 60)
    else:
        return '{0:g}h'.format(val / 3600)




def plot():
    fig = plt.figure(figsize=(65, 12))   #6 * 5, 5 * 3
    ax0 = fig.add_subplot(111)

    for i, cb in enumerate(g_cbs):
        print(cb)

        #cb_data = load_data(cb)
        cb_data = collect_data(cb)

        store_data(cb, cb_data)
        
        ax = fig.add_subplot(1, 5, i+1)

        for label, color, marker in zip(g_labels, g_colors, g_markers):
            l_data = cb_data[label]
            if not bool(l_data):
                continue
            # x = [v * 0.5 / g_precision for v in range(0, g_maxtime * g_precision * 2)]
            y, y_min, y_max = l_data
            x = range(len(y))

            if g_type == 'pdf':
                xs = []
                ys = []
                ys_min = []
                ys_max = []
                for i, xi in enumerate(x):
                    if i % 10 == 0:
                        xs.append(xi)
                        ys.append(y[i])
                        ys_min.append(y_min[i])
                        ys_max.append(y_max[i])
                x = xs
                y = ys
                y_min = ys_min
                y_max = ys_max

            ax.plot(x, y, label=label, color=color, markersize=20, marker=marker, markevery=0.05, linewidth = 5.0)
            ax.fill_between(x, y_min, y_max, color=color, alpha=0.2)

            # print '  ', label, y[0], y[1], len(y)
            print ('  ', label, y[-1])
        
        ax.set_title(cb)


        # set the time to start 
        # ax.set_xlim([5, g_maxtime+600])
        # ax.set_xscale('symlog', base=2)

        ax.set_xlim([0, g_maxtime + 60])

        # ax.set_xscale('symlog', base=10)
        # ax.get_xaxis().set_major_formatter(ticker.ScalarFormatter())


        x_ticks = [v * 3600 for v in [1,3,6,9,12,15,18,21,24]]
        ax.set_xticks(x_ticks)
        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / 3600))
        ax.xaxis.set_major_formatter(ticks_x)

        

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(40)

        
        ax.grid()


    # ax = fig.add_subplot(111)
    for k in range(len(g_labels)):
        ax0.plot([], [], label=g_labels[k], color=g_colors[k], markersize=20, marker=g_markers[k])
    
    # ax.spines['top'].set_color('none')
    # ax.spines['bottom'].set_color('none')
    # ax.spines['left'].set_color('none')
    # ax.spines['right'].set_color('none')
    # ax.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')


    ax0.spines['top'].set_color('none')
    ax0.spines['bottom'].set_color('none')
    ax0.spines['left'].set_color('none')
    ax0.spines['right'].set_color('none')
    ax0.tick_params(labelcolor='w', top='off', bottom='off', left='off', right='off')
    ax0.set_xlabel("time (hour)", fontsize=50, labelpad=10)
    ax0.set_ylabel("number of edges", fontsize=50, labelpad=30) 

    leg = ax0.legend(prop={'size': 40}, markerscale=1.5, loc='lower center', bbox_to_anchor=(0.5,1.06), borderaxespad=0., ncol=len(g_labels))
    for line in leg.get_lines():
        line.set_linewidth(8.0)

    # plt.tight_layout()
    plt.subplots_adjust(left=0.05, right=0.99, bottom=0.11, top=0.88)

    plt.savefig('./cov.{}'.format(g_type))



def main():
    plot()



if __name__ == '__main__':
    main()




    # 
