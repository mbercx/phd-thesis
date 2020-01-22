import os, json
import numpy as np
from matplotlib import colors, cm
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

from monty.json import MontyDecoder
from ipywidgets import interact, interactive, interactive_output, fixed, FloatSlider, Tab, \
    Select, SelectMultiple, HBox, VBox, Output, Text, Button, Layout, Checkbox
from ipyfilechooser import FileChooser

from vscworkflows.firetasks.core import VaspParallelizationTask

OPT_BAND_PARALLEL_PBE = 7
OPT_BAND_PARALLEL_HSE = 8

def interface(f):
    
    try:
        with open(f.selected, "r") as file:
            data = json.loads(file.read(), cls=MontyDecoder)
    except FileNotFoundError:
        return "Please select an existing file."
    
    print("NKPTS = " + str(data["n_kpoints"]) + "\tNBANDS = " + str(data["nbands"]))
    timing_list = data["timing_list"]
    
    try:
        assert isinstance(timing_list, list)
    except AssertionError:
        return "timing_list is not a List. Please check your input file."

    nodes_list = list(set([t["nodes"] for t in timing_list]))
    nodes_list.sort()

    kpar_list = list(set([t["kpar"] for t in timing_list]))
    kpar_list.sort()

    ncore_list = list(set([t["ncore"] for t in timing_list]))
    ncore_list.sort()
    
    select_layout = Layout(width='70px')

    versus = Select(options=["NODES", "KPAR"], index=0,
                    layout=select_layout)
    nodes = Select(options=nodes_list, index=0,
                   layout=select_layout)
    x_axis_select = Select(options=["NCORE", "NPAR"], index=0, 
                           layout=select_layout)
    nodes_select = SelectMultiple(options=nodes_list,
                                  value=nodes_list[:3],
                                  rows=len(nodes_list),
                                  layout=select_layout)
    kpar_select = SelectMultiple(options=kpar_list,
                                 value=kpar_list[:3],
                                 rows=len(kpar_list),
                                 layout=select_layout)
    ncore_select = SelectMultiple(options=ncore_list,
                                  value=ncore_list[:3],
                                  rows=len(ncore_list),
                                  layout=select_layout)
    is_hybrid = Checkbox(value=False,
                      description="Hybrid?")

    widget_mappings = {
        "Timestep": {
            "descriptions": ["X-axis", ],
            "input": (versus, ),
            "output": interactive_output(
                time_plot, {"timing_list": fixed(timing_list),
                            "versus": versus}
            )
        },
        "Chessboard": {
            "descriptions": ["Nodes", "X-axis", "Hybrid"],
            "input": (nodes, x_axis_select, is_hybrid),
            "output": interactive_output(
                chessboard_plot, {"data": fixed(data),
                                  "nodes": nodes, 
                                  "x_axis": x_axis_select,
                                  "is_hybrid": is_hybrid}
            )
        },
        "Tetris": {
            "descriptions": ["Nodes", "KPAR", "NCORE", "Hybrid"],
            "input": [nodes_select, kpar_select, ncore_select, is_hybrid],
            "output": interactive_output(
                tetris_plot, {"data": fixed(data),
                              "nodes_choices": nodes_select,
                              "kpar_choices": kpar_select,
                              "ncore_choices": ncore_select,
                              "is_hybrid": is_hybrid}
            )
        },
        "Optimal": {
            "descriptions": [],
            "input": (),
            "output": interactive_output(
                optimal_settings, {"timing_list": fixed(timing_list)}
            )
        },
#         "NPAR line plot": {
#             "descriptions": ["Nodes", ],
#             "input": (nodes, ),
#             "output": interactive_output(
#                 npar_line_plot, {"timing_list": fixed(timing_list),
#                                 "nodes": nodes}
#             )
#         },
#         "NCORE line plot": {
#             "descriptions": ["Nodes", ],
#             "input": (nodes, ),
#             "output": interactive_output(
#                 ncore_line_plot, {"timing_list": fixed(timing_list),
#                                   "nodes": nodes}
#             )
#         }
    }

    tab = Tab()
    tab.children = [VBox((HBox([VBox((Button(description=desc, layout=select_layout), inp)) 
                                if desc != "Hybrid" else inp for (desc, inp) in zip(w["descriptions"], w["input"])]), w["output"])) 
                    for w in widget_mappings.values()]

    for i, title in enumerate(widget_mappings.keys()):
        tab.set_title(i, title)
    
    return tab

def time_plot(timing_list, versus):
    
    if versus == "NODES":
        time_vs_nodes(timing_list)
    elif versus == "KPAR":
        time_vs_kpar(timing_list)

def time_vs_nodes(timing_list):
    
    kpar_list = list(set(
        [t["kpar"] for t in timing_list]
    ))
    kpar_list.sort()
    
    plt.rcdefaults()
    cmap = cm.viridis._resample(len(kpar_list))

    plt.rc("font", size=14)
    fig, ax = plt.subplots()

    plt.scatter(
        x=[t["nodes"] for t in timing_list], 
        y=[t["timing"] for t in timing_list],
        c=[cmap.colors[kpar_list.index(t["kpar"])] for t in timing_list]
    )

    plt.yscale("log")
    ax.set_xlabel("Number of nodes")
    ax.set_ylabel("Average time / electronic step (s)")

    cbar = plt.colorbar()
    cbar.set_ticks([0, 1])
    cbar.ax.set_yticklabels([np.min(kpar_list), np.max(kpar_list)]);
    cbar.ax.set_ylabel("KPAR")
    
    return plt

def time_vs_kpar(timing_list):
    
    plt.rcdefaults()
    plt.rc("font", size=14)
    
    node_list = list(set(
        [t["nodes"] for t in timing_list]
    ))
    node_list.sort()

    for node in node_list:

        node_timings = [timing for timing in timing_list if timing["nodes"] == node]
        kpars = [t["kpar"] for t in node_timings]
        timings = [t["timing"] for t in node_timings]

        plt.plot(kpars, timings, "o")

    plt.xlabel("KPAR")
    if np.max(kpars) > 100:
        plt.xscale("log")
    plt.yscale("log")
    plt.ylabel("Average time / electronic step (s)")

    plt.legend(node_list, bbox_to_anchor=(1, 1.025), loc="upper left", title="# nodes")

def chessboard_plot(data, nodes, x_axis="NPAR", is_hybrid=False):
    
    timing_list = data["timing_list"]
    
    plt.rcdefaults()
    plt.rc("font", size=14)
    x_axis = x_axis.lower()
    
    node_timings = [t for t in timing_list if t["nodes"] == nodes]

    node_kpar_list = list(set([t["kpar"] for t in node_timings]))
    node_kpar_list.sort()
    node_x_list = list(set([t[x_axis] for t in node_timings]))
    node_x_list.sort()

    timestep = np.zeros([len(node_kpar_list), len(node_x_list)])

    for timing in node_timings:
        timestep[node_kpar_list.index(timing["kpar"])][node_x_list.index(timing[x_axis])] = timing["timing"]

    node_times = np.array([t["timing"] for t in node_timings])
    
    norm = colors.Normalize(
        vmin=np.min(node_times),
        vmax=min(np.max(node_times), np.mean(node_times) * 2.0)
    )
    
    timestep[timestep == 0.0] = None

    fig, ax = plt.subplots(figsize=(len(node_x_list), len(node_kpar_list)))
    ax.imshow(timestep, cmap=cm.RdYlGn_r, origin="lower", norm=norm)

    for i in range(len(node_kpar_list)):
        for j in range(len(node_x_list)):
            if not np.isnan(timestep[i, j]):
                text = ax.text(j, i, round(timestep[i, j], 1),
                               ha="center", va="center", color="k")

    ax.set_xticks(range(len(node_x_list)))
    ax.set_xticklabels([str(n) for n in node_x_list])
    ax.set_xlabel(x_axis.upper())
    ax.set_yticks(range(len(node_kpar_list)))
    ax.set_yticklabels([str(k) for k in node_kpar_list])
    ax.set_ylabel("KPAR")
    
    opt_band_parallel = OPT_BAND_PARALLEL_HSE if is_hybrid else OPT_BAND_PARALLEL_PBE
    n_cores = node_timings[0]["kpar"] * node_timings[0]["npar"] * node_timings[0]["ncore"]
    cores_per_node = n_cores // nodes
    
    kpar, ncore = VaspParallelizationTask._optimize_parallelization(
        nkpts=data["n_kpoints"], nbands=data["nbands"], number_of_cores=n_cores, 
        cores_per_node=cores_per_node, opt_band_parallel=opt_band_parallel,
        is_hybrid=is_hybrid
    )
    optimal_x = ncore if x_axis == "ncore" else n_cores // kpar // ncore
    
    try:
        ax.add_patch(Rectangle(
            xy=(node_x_list.index(optimal_x) - 0.5, 
                node_kpar_list.index(kpar) - 0.5),
                width=1, height=1,
                linewidth=3, edgecolor='r', facecolor='none'
        ))
        print("The red square indicates the optimal setting determined by VaspParallelizationTask.")
    except ValueError:
        print("Optimal settings (KPAR = " + str(kpar) 
              + " ; " + x_axis.upper() + " = " + str(optimal_x) 
              + ") not in test.")

    plt.title(str(nodes) + " NODES")
    
def tetris_plot(data, nodes_choices, kpar_choices, 
                ncore_choices, is_hybrid):
    
    timing_list = data["timing_list"]
    
    fontsize = 18
    plt.rcParams["axes.linewidth"] = 2
    plt.rcParams["font.size"] = 14
    plt.rc('axes', labelsize=fontsize)
    plt.rc('xtick', labelsize=fontsize)
    plt.rc('ytick', labelsize=fontsize)

    fig, ax = plt.subplots(1, len(nodes_choices), 
                           figsize=(len(nodes_choices) * len(ncore_choices), len(kpar_choices)))
    plt.subplots_adjust(wspace=0, bottom=0.0)
    
    print("The red square indicates the optimal setting determined by VaspParallelizationTask.")

    for i, n in enumerate(nodes_choices):

        n_timings = [t for t in timing_list if t["nodes"] == n 
                     and t["kpar"] in kpar_choices and t["ncore"] in ncore_choices]

        timestep = np.zeros([len(kpar_choices), len(ncore_choices)])

        for t in n_timings:
            timestep[kpar_choices.index(t["kpar"])][ncore_choices.index(t["ncore"])] = t["timing"]
        
        try:
            norm = colors.Normalize(vmin=np.min([t["timing"] for t in n_timings]),
                                    vmax=min(np.max([t["timing"] for t in n_timings]),
                                             np.mean([t["timing"] for t in n_timings]) * 2.0))
        except ValueError:
            print()
            print("Chosen combination of Nodes/KPAR/NCORE results in empty plot for " + str(n) + " nodes.")
            plt.close()
            return None

        timestep[timestep == 0.0] = np.nan
        try:
            im = ax[i].imshow(timestep, cmap=cm.RdYlGn_r, origin="lower", norm=norm)
        except TypeError:
            print()
            print("Please select at least 2 node choices. For analyzing the optimal " +
                  "parallelization for a single # of nodes, use the chessboard plot.")
            plt.close()
            return None

        for x in range(len(kpar_choices)):
            for y in range(len(ncore_choices)):
                if not np.isnan(timestep[x, y]):
                    t = ax[i].text(y, x, round(timestep[x, y], 1),
                               ha="center", va="center", color="k")

        ax[i].set_title(str(n) + " NODES", fontsize=20)
        ax[i].set_xticks(range(len(ncore_choices)))
        ax[i].set_xticklabels([str(c) for c in ncore_choices])
        ax[i].set_xlabel("NCORE")
        if i > 0:
            #ax[i].tick_params(left="off", right="off")
            ax[i].yaxis.set_major_locator(plt.NullLocator())
        
        opt_band_parallel = OPT_BAND_PARALLEL_HSE if is_hybrid else OPT_BAND_PARALLEL_PBE
        n_cores = n_timings[0]["kpar"] * n_timings[0]["npar"] * n_timings[0]["ncore"]
        cores_per_node = n_cores // n
        
        kpar, ncore = VaspParallelizationTask._optimize_parallelization(
            nkpts=data["n_kpoints"], nbands=data["nbands"], number_of_cores=n_cores, 
            cores_per_node=cores_per_node, opt_band_parallel=opt_band_parallel,
            is_hybrid=is_hybrid
        )

        if kpar in kpar_choices and ncore in ncore_choices:
            ax[i].add_patch(Rectangle(
                xy=(ncore_choices.index(ncore) - 0.5, 
                    kpar_choices.index(kpar) - 0.5),
                    width=1, height=1,
                    linewidth=3, edgecolor='r', facecolor='none'
            ))

    ax[0].set_yticks(range(len(kpar_choices)))
    ax[0].set_yticklabels([str(k) for k in kpar_choices])
    ax[0].set_ylabel("KPAR")
    
def optimal_settings(timing_list):
    
    nodes_list = list(set(
        [t["nodes"] for t in timing_list]
    ))
    nodes_list.sort()
    
    best_setting_list = []

    for nodes in nodes_list:

        best_time = 1e10

        for t in [timing for timing in timing_list if timing["nodes"] == nodes]:
            if t["timing"] < best_time:
                best_setting = t
                best_time = t["timing"]
        best_setting_list.append(best_setting)
        
    speedup = []
    efficiency = []

    for d in best_setting_list:
        speedup.append(
            best_setting_list[0]["timing"] / d["timing"]
        )
        efficiency.append(
            best_setting_list[0]["timing"] / d["timing"] / d["nodes"]
        )
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx() 

    ax1.plot(
        [t["nodes"] for t in best_setting_list],
        [t["timing"] for t in best_setting_list],
        "o-", color="b"
    )
    ax2.plot(
        [t["nodes"] for t in best_setting_list],
        efficiency,
        "o-", color="r"
    )
    ax2.plot(
        [t["nodes"] for t in best_setting_list],
        [1]*len(best_setting_list),
        "-", color="k"
    )
    ax1.set_xlabel("# nodes")
    ax1.set_ylabel("Average time / electronic step", color="b")
    reference = str(best_setting_list[0]["nodes"]) + " node"
    if best_setting_list[0]["nodes"] > 1:
        reference += "s"
    ax2.set_ylabel("Efficiency vs " + reference , color="r")
    

def npar_line_plot(timing_list, nodes):
    
    import matplotlib.pyplot as plt
    
    nodes_timings = [timing for timing in timing_list if timing["nodes"] == nodes]
    nodes_timings = sorted(nodes_timings, key=lambda x: x["kpar"])

    npars = set()
    for n in [t["npar"] for t in nodes_timings]:
        npars.add(n)
    npars = list(npars)
    npars.sort()
    npars = npars[:9]

    cmap = cm.plasma._resample(len(npars))

    for n in npars:
        kpars = [t["kpar"] for t in nodes_timings if t["npar"] == n]
        timings = [t["timing"] for t in nodes_timings if t["npar"] == n]


        plt.plot(kpars, timings, "o-", color=cmap.colors[npars.index(n)])

    # Set axis scales
    if np.max([t["kpar"] for t in nodes_timings]) > 100:
        plt.xscale("log")
    plt.xlabel("KPAR")
    plt.yscale("log")
    plt.ylabel("Average time / electronic step")
    plt.legend(npars, bbox_to_anchor=(1, 1.025), loc="upper left", title="NPAR")
    

def ncore_line_plot(timing_list, nodes):
    
    import matplotlib.pyplot as plt
    
    nodes_timings = [timing for timing in timing_list if timing["nodes"] == nodes]
    nodes_timings = sorted(nodes_timings, key=lambda x: x["kpar"])

    npars = set()
    for n in [t["ncore"] for t in nodes_timings]:
        npars.add(n)
    npars = list(npars)
    npars.sort()
    npars = npars[:9]

    cmap = cm.plasma._resample(len(npars))

    for n in npars:
        kpars = [t["kpar"] for t in nodes_timings if t["ncore"] == n]
        timings = [t["timing"] for t in nodes_timings if t["ncore"] == n]


        plt.plot(kpars, timings, "o-", color=cmap.colors[npars.index(n)])

    # Set axis scales
    if np.max([t["kpar"] for t in nodes_timings]) > 100:
        plt.xscale("log")
    plt.xlabel("KPAR")
    plt.yscale("log")
    plt.ylabel("Average time / electronic step")
    plt.legend(npars, bbox_to_anchor=(1, 1.025), loc="upper left", title="NCORE")

