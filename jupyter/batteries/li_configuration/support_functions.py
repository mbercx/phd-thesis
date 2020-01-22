import os, json
import numpy as np
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rcParams['figure.dpi']= 200

from xml.etree.cElementTree import ParseError
from pymatgen import Structure
from pybat.core import Cathode
from icet.tools.convex_hull import ConvexHull

def get_energy(file):
    
    with open(file, "r") as f:
        d = json.loads(f.read())
        
    return d["energy"]

def get_structure(file):
    
    with open(file, "r") as f:
        d = json.loads(f.read())
        
    return Structure.from_dict(json.loads(d["structure"]))

def get_configuration_data_list(directory, functional, calculation):
    
    data_list = []

    for configuration in os.listdir(directory):

        if os.path.isdir(os.path.join(directory, configuration)):

            try:
                cathode = Cathode.from_file(
                    os.path.join(directory, configuration, "prim", "configuration.json")
                )

                energy = get_energy(
                    os.path.join(directory, configuration, "prim",
                                 functional + "_" + calculation, "data.json")
                )
                if calculation == "static":
                    final_cathode = Cathode.from_file(
                        os.path.join(directory, configuration, "prim",
                                     functional + "_" + calculation, "initial_cathode.json")
                )
                else:
                    final_cathode = Cathode.from_file(
                        os.path.join(directory, configuration, "prim",
                                     functional + "_" + calculation, "final_cathode.json")
                )

                data_list.append({
                    "tag": configuration,
                    "initial_structure": cathode,
                    "final_structure": final_cathode,
                    "energy": energy
                })

            except FileNotFoundError:
                warnings.warn("Could not find required output in directory: " 
                              + configuration)
            except ParseError:
                warnings.warn("Parse error when extracting output in directory: " 
                              + configuration)
                
    return data_list

def set_up_convexhull_data(data_list, element, ref_composition, endpoint_energies):
    
    ref_natoms = ref_composition.num_atoms
    ref_concentration = ref_composition[element]
    
    for data in data_list:
        
        structure = data["initial_structure"]
        number_of_fu = len(structure) / ref_natoms
        concentration = structure.composition.element_composition[element] / number_of_fu
        
        energy_per_fu = data["energy"] / number_of_fu
        
        data["concentration"] = concentration
        data["energy_per_fu"] = energy_per_fu
        
        mixing_energy = (energy_per_fu
                      - (1 - concentration / ref_concentration) * endpoint_energies[0]
                      - concentration / ref_concentration * endpoint_energies[1])
        
        data["mixing_energy"] = mixing_energy

def clean_data_list(data_list, max_angle_diff=5, angles_tolerance=1, verbose=False):
    
    new_data_list = []
    
    removed_configurations = False
    
    for i, data in enumerate(data_list):
    
        if (sum(abs(np.array(data["initial_structure"].lattice.angles) 
                   - np.array(data["final_structure"].lattice.angles)) 
                > max_angle_diff * np.array([1, 1, 1])) < angles_tolerance + 1):
            new_data_list.append(data)
        else:
            if verbose:
                if not removed_configurations:
                    print("Removed configurations: ")
                    removed_configurations = True
                print("Configuration " + str(i) + " with concentration " 
                      + str(data["concentration"]) + ".")
            
    return new_data_list

def draw_convex_hull(data_list):
    
    fig, ax = mpl.pyplot.subplots(figsize=(6, 4))
    ax.set_xlabel(r'% Li', fontsize=18)
    ax.set_ylabel(r'Mixing energy (meV/atom)', fontsize=16)
    ax.set_xlim([0, 2])
    # ax.set_ylim([-69, 15])
    
    concentrations = [d["concentration"] for d in data_list]
    mixing_energies = [d["mixing_energy"] for d in data_list]
    hull = ConvexHull(concentrations, mixing_energies)
    ax.scatter(concentrations, 1e3 * np.array(mixing_energies),
                   marker='x')
    ax.plot(hull.concentrations, 1e3 * hull.energies, '-o')