# Solar Cells

> _Note that the calculations performed via these notebooks do not currently match with the results presented in the thesis. As solar cells was the first topic I worked on, the results presented in the thesis were obtained before I started using workflows and Jupyter notebooks. However, the results should be largely reproducible based on these notebooks, save for the G0W0 calculations. These may still be added in the future._

## CuAu-likes

For the calculation of the optical properties of the CuAu-like (#115) and chalcopyrite (#122) structures, we start from the provided template files of the AlCuS$_2$ compound. Based on these templates, we generate all structures in the [structures.ipynb notebook](./structures.ipynb).

### Structure and formation energy

Both the geometry optimization and the calculation of the dielectric function are performed in a single workflow for each structure. The workflows are set up and sent to the mongoDB server in the [workflows notebook](workflows.ipynb).

### Absorber layer efficiency

> [_Work in Progress_](../../figures/moss_fire.gif)

## SLME Analysis

### The curious case of CA-CuInSe$_2$

> [_Work in Progress_](../../figures/moss_fire.gif)

### Logistic function model

> [_Work in Progress_](../../figures/moss_fire.gif)

### Indirect band gap absorbers

> [_Work in Progress_](../../figures/moss_fire.gif)
