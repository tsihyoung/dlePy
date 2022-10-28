#!/usr/bin/env python3
from dlePy.vasp.chgcar import *

# read in charge densities
rho, atoms = read_chgcar("CHGCAR")

# CHGCAR may contain charge density from multiple steps
rho0 = rho.chg[0]
write_vtk("CHGCAR.vtk", atoms, data=rho0)
