import os

import numpy as np
import matplotlib.pyplot as plt

def plot_min_energy_profile(landscapes, facet_angles, 
                            reference_energies, x_axis="distance",
                            ylim=None):
    
    colors = ["b", "r"]
    
    if x_axis == "shared_angle":
        facet_angles = len(facet_angles)*[facet_angles[0]]
        shared_flag = True
    
    for landscape, facet_angs, ref_energy, color in zip(
        landscapes, facet_angles, reference_energies, colors):
        
        x = landscape["x_coords"].copy()
        y = landscape["y_coords"].copy()
        e = landscape["energy"].copy()
        e -= ref_energy

        path = [[x[i, j], y[i, j], e[i, j]] 
                for i, j in zip(range(x.shape[0]), np.argmin(e, 1))
                if min(facet_angs) < x[i, j] < max(facet_angs)]

        if x_axis == "distance":
            dist = [0,]
            energy = [path[0][2]]
            for i in range(1, len(path)):
                dist.append(dist[-1] + distance(path[i-1][0:2], path[i][0:2]))
                energy.append(path[i][2])
            plt.plot(dist, energy, color=color)
            plt.xlabel('Distance ($\mathrm{\AA}$)', size='x-large')
            plt.xticks(size='x-large')
            plt.xlim([0, max(dist)])

        elif x_axis == "angle" or x_axis == "shared_angle":
            
            path = np.array(path)
            
            if x_axis == "shared_angle":
                if shared_flag:
                    angles = path[:, 0]
                    shared_flag = True
            else:
                angles = path[:, 0]
            
            energy = path[:, 2]
            plt.plot(angles, energy, color=color)
            plt.xlabel('Angle', size='x-large') 
            xticks = []
            for i, angle in enumerate(facet_angs):
                plt.axvline(angle, color='k', linestyle='-', linewidth=1)
                xticks.append('$\Omega_' + str(i + 2) + '$')
            plt.xticks(facet_angs, xticks, size='x-large')
            plt.xlim([min(facet_angles[0]), max(facet_angles[0])])

        plt.ylabel('Energy (eV)', size='x-large')
        plt.yticks(size="x-large")
        ylim = ylim or [min(energy)-0.1, max(energy)+0.1]
        plt.ylim(ylim)
        plt.subplots_adjust(left=0.15, right=0.95, top=0.95, bottom=0.15)
        
    return plt