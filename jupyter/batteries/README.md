# Batteries

> Note that as the workflows do not currently support non-collinear calculations, the results for Li$_2$IrO$_3$ were obtained the old-fashioned way.

## Li-rich battery cathodes

Here I will describe the calculations for the oxygen framework stability analysis and provide links to the corresponding notebooks.

### Structure and Li configuration

The workflows for the calculation of the Li configuration are set up and sent to the mongoDB server in the [workflows notebook](li_configuration/workflows.ipynb). Once complete, the output of the calculations was processed into the `.json` files in the `data` directory using the [process data notebook](li_configuration/process_data.ipynb).
The final analysis is performed in the [analysis notebook](li_configuration/analysis.ipynb).

### Oxidation

> [_Work in Progress_](../../figures/moss_fire.gif)

### Dimer Analysis

> [_Work in Progress_](../../figures/moss_fire.gif)

## Substitutions

Here I will describe the calculations for the substitution analysis and provide links to the corresponding notebooks.

### Thermodynamic stability of Sn substitution

The workflows for the Sn-substituted configurations are set up in the corresponding [workflows notebook](Sn_substitution/workflows.ipynb), whereas those of the Sn-phase structures are set up in a [different workflow notebook](Sn_substitution/Sn_workflows.ipynb). The subsequent analysis is performed in the [analysis notebook](Sn_substitution/analysis.ipynb).

### Influence of Mn$^{4+}$ substitution on oxygen stability

A brief explanation of our initial choices for the dimers we wanted to investigate is provided in [the dimer choices notebook](substitutions/dimer_choices.ipynb). However, due to issues with the NEB convergence and time constraints, we decided to focus on the `49-80` dimer, i.e. the dimer across the Li-layer that has one oxygen which is a part of the octahedral environment of the substitution site. The VASP output was processed in the [process data notebook](substitutions/process_data.ipynb).

Interactive tools for exploring the oxidation and dimerization results were set up in the [oxidation analysis](substitutions/oxidation_analysis.ipynb) and [barrier analysis](substitutions/barrier_analysis.ipynb) notebooks. The figures for both the projected density of states and the nudged elastic band barrier were set up in the [figures notebook](substitutions/figures.ipynb).

## Polyborane solid electrolytes

### Energy landscape of [CB$_{11}$H$_{12}$]^-

The workflows were started using the command line interface of the `cage` package (which was the method I used before switching entirely to notebooks). The data was similarly gather using the `cage util gather` command. Finally, the analysis was performed using the corresponding [analysis notebook](landscapes/analysis.ipynb).

