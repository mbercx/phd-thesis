import os, json
import numpy as np
import warnings

from xml.etree.cElementTree import ParseError
from pymatgen import Structure
from pybat.core import Cathode

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

# def get_en_list(material_dir):
    
#     energies = []
    
#     for configuration in [d for d in os.listdir(material_dir) 
#                           if os.path.isdir(os.path.join(material_dir, d))]:
        
#         static_directory = os.path.join(material_dir, configuration, "prim/scanVdW_static")
        
#         try:
#             energies.append(get_energy(os.path.join(static_directory, "data.json")))
#         except FileNotFoundError:
#             print("No data file found in: " + static_directory)
    
#     return energies

def set_up_convexhull_data(data_list, element, ref_composition, endpoint_energies):
    
    ref_natoms = ref_composition.num_atoms
    ref_concentration = ref_composition[element]
    
    for data in data_list:
        
        structure = data["initial_structure"]
        number_of_fu = len(structure) / ref_natoms
        concentration = structure.composition.element_composition[element] / number_of_fu
        
        energy = data["energy"] / number_of_fu
        
        data["concentration"] = concentration
        data["energy_per_fu"] = energy
        
        mixing_energy = (energy 
                      - (1 - concentration / ref_concentration) * endpoint_energies[0]
                      - concentration / ref_concentration * endpoint_energies[1])
        
        data["mixing_energy"] = mixing_energy
