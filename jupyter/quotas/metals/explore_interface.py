# Explore notebook

import json
import ruamel.yaml as yaml
import matplotlib.pyplot as plt

from pymatgen.electronic_structure.plotter import DosPlotter
from monty.json import MontyDecoder, MontyEncoder

from ipywidgets import SelectMultiple, FloatSlider, FloatRangeSlider, SelectionSlider, Combobox
from ipywidgets import interact, fixed

# Define the effective ionization energies of the rare gas ions
ionization_energies = {
    "He": 24.56 - 2,
    "Ne": 21.56 - 1,
    "Ar": 15.76 - 0.5,
    "Kr": 12.00,
    "Xe": 10.13
}

# Load the dictionary of all the structures for which we have calculated the required properties
try:
    results_dict = results_dict
except NameError:
    try:
        with open("../data/results.json", "r") as file:
            results_dict = json.loads(file.read(), cls=MontyDecoder)
    except FileNotFoundError:
        with open("../data/structure_dict.yaml", "r") as file:
            structure_dict = yaml.safe_load(file.read())

def display_results(element, surface, calculation):
    
    workfunction_data = results_dict[element][surface]["workfunction_data"]

    print("Surface work function = " 
          + str(round(workfunction_data.work_function, 3)))
    
    if calculation == "Secondary Electron Emission":
        interact(display_see, element=fixed(element), surface=fixed(surface), 
                    ion=ionization_energies.keys())
        
    elif calculation == "DOS":
        display_dos(element=element, surface=surface)
        
    elif calculation == "Projected DOS":
        interact(display_pdos, element=fixed(element), 
                 surface=fixed(surface), max_dos=FloatSlider(value=100, min=0, max=300))
        
    elif calculation == "Local Potential":
        display_locpot(element=element, surface=surface)
        
    elif calculation == "Loss Function":
        try:
            dieltensor = results_dict[element]["bulk"]["dieltensor"]

            interact(display_loss_function, dieltensor=fixed(dieltensor),
                     surface=False,
                     xlim=FloatRangeSlider(value=[min(dieltensor.energies), 
                                            max(dieltensor.energies)],
                                          min=min(dieltensor.energies),
                                          max=max(dieltensor.energies)))
        except KeyError:
            print("Requested element/surface combination is not available")
    else:
        print("Requested results not available.")
        

def display_see(element, surface, ion):
    
    try:

        energy = results_dict[element][surface]["yield_results"][ion]["energy"]
        yield_spectrum = results_dict[element][surface]["yield_results"][ion]["yield"]
        total_yield = results_dict[element][surface]["yield_results"][ion]["total_yield"]
        
        print("Total Yield = " + str(round(total_yield, 3)))
        print()
         
        # Plot the yield spectrum
        plt.rcParams["font.size"] = 16
        plt.plot(energy, yield_spectrum)
        plt.xlabel("Energy (eV)")
        plt.ylabel("$\gamma$ (#electrons/ion)")
        
    except KeyError:
        print("Requested element/surface combination is not available")
        
def display_dos(element, surface, max_dos=100):
    try:
        cdos = results_dict[element][surface]["complete_dos"]
         
        # Plot the DOS
        plt.rcParams["font.size"] = 16
        plt.plot(cdos.energies, cdos.get_densities())
        plt.xlabel("Energy (eV)")
        plt.ylabel("DOS")
        
    except KeyError:
        print("Requested element/surface combination is not available")
        
def display_pdos(element, surface, max_dos=100):
    
    cdos = results_dict[element][surface]["complete_dos"]
    dpl = DosPlotter()

    dpl.add_dos_dict(cdos.get_element_spd_dos(element.split("_")[0]))
    plt = dpl.get_plot(ylim=[0, max_dos])
    
def display_locpot(element, surface):
    
    try:
        workfunction_data = results_dict[element][surface]["workfunction_data"]
        workfunction_data.get_locpot_along_slab_plot(plt=plt);
        
    except KeyError:
        print("Requested element/surface combination is not available")
        
def display_loss_function(dieltensor, surface=False, xlim=None):
    
    # Plot the loss function
    plt.rcParams["font.size"] = 16
    plt.plot(dieltensor.energies, dieltensor.get_loss_function(surface=surface))
    plt.xlabel("Energy (eV)")
    plt.ylabel("Loss Function")
    if xlim is not None:
        plt.xlim(xlim)
        
def element_interface(element, calculation):
    
    interact(display_results, element=fixed(element), 
             surface=structure_dict[element]["slabs"].keys(), 
             calculation=fixed(calculation)
             )
