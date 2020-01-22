import os
import numpy as np
import warnings

from vscworkflows.setup.sets import BulkStaticSet
from vscworkflows.workflows.core import get_wf_parallel
from vscworkflows.config import load_config
from pymatgen import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from ipywidgets import interact, interactive, Select, IntSlider, Button, Output, \
    BoundedIntText, SelectMultiple, Text, VBox, HBox, Layout, FileUpload, fixed, IntRangeSlider
from ipyfilechooser import FileChooser


def selection_interface(structure, fworker, kpt_density, functional, 
                        nodes_list, nbands, max_kpt_range):
    
    selection_dict = {}
    selection_dict["structure"] = structure
    selection_dict["scratch_dir"] = CLUSTER_DICT[fworker]["scratch_dir"]
    selection_dict["cores_per_node"] = CLUSTER_DICT[fworker]["cores_per_node"]
    selection_dict["lpad"] = load_config("launchpad", fworker)
    selection_dict["functional"] = (functional, {})
    selection_dict["kpt_density"] = kpt_density
    selection_dict["nbands"] = nbands
    selection_dict["max_kpt_range"] = max_kpt_range
    try:
        selection_dict["nodes_list"] = [int(i) for i in nodes_list.strip(', ').split(',')]
    except ValueError:
        selection_dict["nodes_list"] = None
    
    return selection_dict

def file_interface(fu, fworker, kpt_density):

    try:
        for filename in fu.keys():
            file_str = list(fu.values())[0]["content"].decode("utf-8")
            spl = filename.split(".")
        if len(spl) == 1:
            file_fmt = "poscar"
        else:
            file_fmt = spl[-1]
            
        structure = Structure.from_str(input_string=file_str, fmt=file_fmt)
        
    except UnboundLocalError:
        print("Please select an input file.")
        return
    except ValueError:
        print("Incorrect format for input file.")
        return
    
    static = BulkStaticSet(
        structure, user_incar_settings=user_incar_settings,
        user_kpoints_settings={"reciprocal_density": kpt_density}
    )
    
    nions = len(structure)
    nelect = static.nelect
    ispin = int(static.incar.get("ISPIN", 1))

    if ispin == 1:
        nbands = int(round(nelect / 2 + nions / 2))
    elif ispin == 2:
        nbands = int(nelect * 3 / 5 + nions)
    else:
        raise ValueError("ISPIN Value is not set to 1 or 2!")
    
    cores_per_node = CLUSTER_DICT[fworker]["cores_per_node"]
    nbands = (nbands // cores_per_node + 1) * cores_per_node
    
    kpoints = static.kpoints
    spg = SpacegroupAnalyzer(structure, symprec=1e-5)
    kpts = len(spg.get_ir_reciprocal_mesh(kpoints.kpts))

    selection = interactive(selection_interface, structure=fixed(structure),
                            fworker=fixed(fworker), kpt_density=fixed(kpt_density),
                            functional=Select(
                                options=['pbe', 'hse06'],
                                value='pbe',
                                rows=2,
                                description='Functional:',
                            ), 
                            nodes_list=Text(
                                value="1, 2, 4",
                                placeholder='Nodes (comma separated)',
                                description='Node List:',
                            ),
                            nbands=BoundedIntText(
                                value=nbands,
                                min=1,
                                max=10000,
                                step=1,
                                description='NBANDS:'
                            ),
                            max_kpt_range=IntRangeSlider(
                                value=[1, kpts],
                                min=1,
                                max=kpts + cores_per_node//2,
                                step=1,
                                description='Max KPAR range:',
                            ))
    display(HBox(selection.children[:2]))
    display(HBox(selection.children[2:])) 
    display(button)
    
    return selection

def submit_workflows(b):
    
    with output:
        
        output.clear_output()
        selection = file.result
        selection.update()
        
        structure = selection.result["structure"]
        
        static = BulkStaticSet(
            structure, user_incar_settings=user_incar_settings,
            user_kpoints_settings={
                "reciprocal_density": selection.result["kpt_density"]
            }
        )
        ispin = int(static.incar.get("ISPIN", 1))

        if ispin == 2:
            warnings.warn("The number of irreducible points might "
                          "be incorrect for spin-polarized calculations!")

        kpoints = static.kpoints
        spg = SpacegroupAnalyzer(structure, symprec=1e-5)
        kpts = len(spg.get_ir_reciprocal_mesh(kpoints.kpts))
        
        try:
            parallelization_dir = os.path.join(
                selection.result["scratch_dir"], "parallel",
                selection.result["functional"][0] + "_" + static.incar.get("ALGO", "Fast"),
                (str(structure.composition).replace(" ", "") + "_B" 
                 + str(selection.result["nbands"]) + "_K" + str(kpts))
            )
            user_incar_settings.update({"NBANDS": selection.result["nbands"]})
            user_kpoints_settings = {"reciprocal_density": selection.result["kpt_density"]}

            for nodes in selection.result["nodes_list"]:
                selection.result["lpad"].add_wf(
                    get_wf_parallel(
                        structure=structure,
                        directory=parallelization_dir,
                        nodes=nodes,
                        nbands=selection.result["nbands"],
                        functional=selection.result["functional"],
                        user_kpoints_settings=user_kpoints_settings,
                        user_incar_settings=user_incar_settings,
                        handlers=handlers,
                        cores_per_node=selection.result["cores_per_node"],
                        kpar_range=selection.result["max_kpt_range"]
                    )
                )
        except TypeError as t:
            print(t)
            print("Incorrect node list input!")

style = {'description_width': 'initial'}

file = interactive(file_interface, fu=FileUpload(), 
                   fworker=Select(options=CLUSTER_DICT.keys(),
                                  value='breniac',
                                  rows=3,
                                  description='Fworker:'),
                   kpt_density=IntSlider(value=300,
                                         min=100,
                                         max=10000,
                                         step=100,
                                         description='k-point density:',
                                         style = {'description_width': 'initial'}))

button = Button(description="Submit Workflow")
button.on_click(submit_workflows)
output = Output()

display(HBox(file.children[:3]))
display(file.children[-1])
display(output)
