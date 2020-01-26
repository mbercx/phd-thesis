import os
%matplotlib inline

from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.electronic_structure.core import Orbital, OrbitalType
from pymatgen.electronic_structure.dos import Dos
from pymatgen.electronic_structure.plotter import DosPlotter
from pymatgen import Element, Spin

# Method for quickly obtaining the smeared dos, summed over both spins
def get_smeared_sum_dos(dos, smearing_sigma=0.05):
    """
    
    Args:

    """

    total_dos = Dos(
        efermi=dos.efermi, energies=dos.energies,
        densities={Spin.up:dos.get_smeared_densities(sigma=smearing_sigma)[Spin.up]
                   + dos.get_smeared_densities(sigma=smearing_sigma)[Spin.down]}
    )

    return total_dos

# Method for quickly obtaining the smeared dos for non-collinear calculations
def get_smeared_sum_dos_ncl(dos, smearing_sigma=0.05):
    """
    
    Args:

    """

    total_dos = Dos(
        efermi=dos.efermi, energies=dos.energies,
        densities={Spin.up:dos.get_smeared_densities(sigma=smearing_sigma)[Spin.up]}\
    )

    return total_dos

# Method for quickly plotting the element-projected DOS
def plot_el_total_dos(complete_dos, elements, smearing_sigma=0.05, xlim=None, ylim=None):
    """
    
    Args:
        complete_dos (CompleteDos):
        elements: list or tuple of string representations of the elements, e.g. ["Mn", "O"]
    
    """
    
    elements_dos = complete_dos.get_element_dos()

    total_dos_dict = dict()
    
    for el in elements:
        
        el_dos = elements_dos[Element(el)]
        
        total_dos_dict[el] = Dos(
            efermi=el_dos.efermi, energies=el_dos.energies,
            densities={Spin.up:el_dos.get_smeared_densities(sigma=smearing_sigma)[Spin.up] 
                       + el_dos.get_smeared_densities(sigma=smearing_sigma)[Spin.down]}
        )
        
    plotter = DosPlotter()
    plotter.add_dos_dict(total_dos_dict)
    plotter.show(xlim=xlim, ylim=ylim)
    