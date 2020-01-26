import os, re
import numpy as np

from quotas import QSlab
from fnmatch import fnmatch

from pymatgen import Structure
from pymatgen.core.surface import SlabGenerator

from scipy.ndimage.filters import gaussian_filter1d

# Workflows notebook

def load_slab_from_file(filename):
    """
    Load a QSlab from a .cif or POSCAR file. Note that the filename must 
    contain ONLY the miller indices as numerical characters.
    
    """
    if not fnmatch(filename, "*.cif") and not fnmatch(filename, "*POSCAR*"):
        raise IOError("Input file must be either a .cif or POSCAR file!")
        
    s = Structure.from_file(filename)
    
    miller_index = [int(i) for i in re.sub('[^0-9]','', filename)]
    
    if len(miller_index) != 3:
        raise("Found less/more than 3 numerical characters in input file. "
              "As the script uses the numericals in the filename to determine "
              "the miller indices, please try to use a filename along the lines "
              "of 'Al_100.cif' or 'Al_1_1_0_.cif'.")

    return QSlab(lattice=s.lattice, species=s.species, coords=s.frac_coords,
                 miller_index=miller_index, 
                 oriented_unit_cell=Structure.from_file(filename),
                 shift=0, scale_factor=np.diag([1, 1, 1]))

def get_dewaele_slab_list(element, structure_dict, directory):
    
    return [{"slab": load_slab_from_file(os.path.join(
                     directory, element, element + "_" + k + ".cif")), 
             "user_slab_settings": {"free_layers": v["free_layers"]}}
            for k, v in structure_dict[element]["slabs"].items()]

def get_generated_slab_list(element, structure_dict, directory):
    
    bulk_file = os.path.join(
        directory, element, structure_dict[element]["bulk"]
    )
    bulk = Structure.from_file(bulk_file)
    
    slab_list = list()
    
    for slab in structure_dict[element]["slabs"].keys():
        
        slabgen = SlabGenerator(
            initial_structure=bulk, 
            miller_index=[int(c) for c in slab],
            min_slab_size=10,
            min_vacuum_size=20
        )
        
        while len(QSlab.from_slab(slabgen.get_slab()).find_atomic_layers()) \
            < structure_dict[element]["slabs"][slab]["layers"]:
            slabgen.min_slab_size += 1
            
        slab_terminations = slabgen.get_slabs()
        
        if len(slab_terminations) == 1:        
                
            slab_list.append({
                "slab": QSlab.from_slab(slabgen.get_slab()),
                "user_slab_settings": {
                    "free_layers": structure_dict[element]["slabs"][slab]["free_layers"]
                }
            })
        elif len(slab_terminations) > 1:

            slab_list.append({
                "slab": slab,
                "user_slab_settings": {
                    "free_layers": structure_dict[element]["slabs"][slab]["free_layers"]
                },
                "min_slab_size": slabgen.min_slab_size,
                "min_vacuum_size": 20,
            })
    
    return slab_list

# Figures notebook

def get_smeared_densities(energies, densities, sigma):
    """
    Use a Gaussian kernel to smear a density distribution.

    Args:
        sigma: Std dev of Gaussian smearing function.

    Returns:
        Gaussian-smeared densities.
    """
    
    diff = np.diff(energies)
    avgdiff = sum(diff) / len(diff)
    
    smeared_dens = gaussian_filter1d(densities, sigma / avgdiff)
    return smeared_dens

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx