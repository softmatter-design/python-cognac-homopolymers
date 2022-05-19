#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
import numpy as np
import os

from UDFManager import UDFManager

import polymer_setup.values as val
##########################################
# Initial_UDF の作成
##########################################
def setup_baseudf():
	# 初期udfの内容を作成する
	make_base()
	# すべてのアトムの位置座標及びボンド情報を設定
	setup_atoms()
	return

################################################################################
def make_base():
	#--- create an empty UDF file ---
	val.target_udf = os.path.join(val.target_name, val.base_udf)
	with open(val.target_udf, 'w') as f:
		f.write(r'\include{"%s"}' % val.blank_udf)

	val.uobj = UDFManager(val.target_udf)
	# goto global data
	val.uobj.jump(-1)

	#--- Simulation_Conditions ---
	# Solver
	p = 'Simulation_Conditions.Solver.'
	val.uobj.put('Dynamics', p + 'Solver_Type')
	val.uobj.put('NVT_Kremer_Grest', 			p + 'Dynamics.Dynamics_Algorithm')
	val.uobj.put(0.5, 							p + 'Dynamics.NVT_Kremer_Grest.Friction')
	# Boundary_Conditions
	p = 'Simulation_Conditions.Boundary_Conditions'
	val.uobj.put(['PERIODIC', 'PERIODIC', 'PERIODIC', 1], p)
	#
	# p = "Simulation_Conditions.Dynamics_Conditions.Moment."
	# val.uobj.put(10000, p + "Interval_of_Calc_Moment")
	# val.uobj.put(1, p + "Calc_Moment")
	# val.uobj.put(1, p + "Stop_Translation")
	# val.uobj.put(1, p + "Stop_Rotation")

	# Calc_Potential_Flags
	p = 'Simulation_Conditions.Calc_Potential_Flags.'
	val.uobj.put(1, p + 'Bond')
	val.uobj.put(0, p + 'Angle')
	val.uobj.put(1, p + 'Non_Bonding_Interchain')
	val.uobj.put(1, p + 'Non_Bonding_1_3')
	val.uobj.put(1, p + 'Non_Bonding_1_4')
	val.uobj.put(1, p + 'Non_Bonding_Intrachain')

	# Output_Flags.Statistics
	p = 'Simulation_Conditions.Output_Flags.Statistics.'
	val.uobj.put(1, p + 'Energy')
	val.uobj.put(1, p + 'Temperature')
	val.uobj.put(1, p + 'Pressure')
	val.uobj.put(1, p + 'Stress')
	val.uobj.put(1, p + 'Volume')
	val.uobj.put(1, p + 'Density')
	val.uobj.put(1, p + 'Cell')
	val.uobj.put(0, p + 'Wall_Pressure')
	val.uobj.put(0, p + 'Energy_Flow')

	# Output_Flags.Structure
	p = 'Simulation_Conditions.Output_Flags.Structure.'
	val.uobj.put(1, p + 'Position')
	val.uobj.put(0, p + 'Velocity')
	val.uobj.put(0, p + 'Force')

	#--- Initial_Structure ---
	# Initial_Unit_Cell
	p = 'Initial_Structure.Initial_Unit_Cell.'
	val.uobj.put(val.density, p + 'Density')
	val.uobj.put([0, 0, 0, 90.0, 90.0, 90.0], p + 'Cell_Size')
	
	#--- Molecular_Attributes ---
	# Atomes
	for i, atomname in enumerate(val.atom_name):
		p = 'Molecular_Attributes.Atom_Type[].'
		val.uobj.put(atomname, 	p + 'Name', [i])
		val.uobj.put(1.0, 		p + 'Mass', [i])
	# Bond
	for i, bondname in enumerate(val.bond_name):
		p = 'Molecular_Attributes.Bond_Potential[].'
		val.uobj.put(bondname, 		p + 'Name', [i])
		val.uobj.put('Harmonic', 	p + 'Potential_Type', [i])
		val.uobj.put(0.97, 			p + 'R0', [i])
		val.uobj.put(1000, 			p + 'Harmonic.K', [i])
	# Angle
	for i, anglename in enumerate(val.angle_name):
		p = 'Molecular_Attributes.Angle_Potential[].'
		val.uobj.put(anglename, 			p + 'Name', [i])
		val.uobj.put(val.angle[0], 	p + 'Potential_Type', [i])
		val.uobj.put(val.angle[1], 	p + 'theta0', [i])
		val.uobj.put(val.angle[2], 	p + 'Theta2.K', [i])

	# Site
	for i, sitename in enumerate(val.site_name):
		p = 'Molecular_Attributes.Interaction_Site_Type[].'
		val.uobj.put(sitename, 		p + 'Name', [i])
		val.uobj.put(1, 				p + 'Num_of_Atoms', [i])
		val.uobj.put(val.lj_cond[4], 	p + 'Range', [i])

	#--- Pair_Interaction[] ---
	for i, pairname in enumerate(val.pair_name):
		p = 'Interactions.Pair_Interaction[].'
		val.uobj.put(pairname,   					p + 'Name', [i])
		val.uobj.put('Lennard_Jones', 				p + 'Potential_Type', [i])
		val.uobj.put(val.site_pair_name[i][0],	p + 'Site1_Name', [i])
		val.uobj.put(val.site_pair_name[i][1],	p + 'Site2_Name', [i])
		val.uobj.put(val.lj_cond[0],				p + 'Cutoff', [i])
		val.uobj.put(val.lj_cond[1],				p + 'Scale_1_4_Pair', [i])
		val.uobj.put(val.lj_cond[2],				p + 'Lennard_Jones.sigma', [i])
		val.uobj.put(val.lj_cond[3],				p + 'Lennard_Jones.epsilon', [i])

	#--- Write UDF ---
	val.uobj.write(val.target_udf)
	return

################################################################################
# すべてのアトムの位置座標及びボンド情報を設定
def setup_atoms():
	val.uobj.jump(-1)

	#--- Set_of_Molecules の入力
	p = 'Set_of_Molecules.molecule[].'
	pa = p + 'atom[].'
	pi = p + 'interaction_Site[].'
	pb = p + 'bond[].'
	pang = p +  'angle[].'
	#
	atom_id = 0
	for n_mol in range(val.ma_polymers):
		val.uobj.put(val.mol_name[0], p + 'Mol_Name', [n_mol])
		# beads
		for n_atom in range(val.na_segments):
			# atom
			val.uobj.put(atom_id, 			pa + 'Atom_ID', [n_mol, n_atom])
			val.uobj.put(val.atom_name[0], 	pa + 'Atom_Name', [n_mol, n_atom])
			val.uobj.put(val.atom_name[0], 	pa + 'Atom_Type_Name', [n_mol, n_atom])
			val.uobj.put(0, 				pa + 'Chirality', [n_mol, n_atom])
			val.uobj.put(1, 				pa + 'Main_Chain', [n_mol, n_atom])
			# interaction site
			val.uobj.put(val.site_name[0], 	pi + 'Type_Name', [n_mol, n_atom])
			val.uobj.put(n_atom, 			pi + 'atom[]', [n_mol, n_atom, 0])
			atom_id += 1
		# bonds
		atom1 = 0
		ang_list=[]
		for n_bond in range(val.na_segments - 1):
			val.uobj.put(val.bond_name[0], 	pb + 'Potential_Name', [n_mol, n_bond])
			val.uobj.put(atom1, 			pb + 'atom1', [n_mol, n_bond])
			ang_list.append(atom1)
			val.uobj.put(atom1 + 1, 		pb + 'atom2', [n_mol, n_bond])
			atom1 += 1
		# angles
		atom1 = 0
		for n_ang in range(val.na_segments - 2):
			val.uobj.put(val.angle_name[0], pang + 'Potential_Name', [n_mol, n_ang])
			val.uobj.put(atom1, 			pang + 'atom1', [n_mol, n_ang])
			val.uobj.put(atom1 + 1, 		pang + 'atom2', [n_mol, n_ang])
			val.uobj.put(atom1 + 2, 		pang + 'atom3', [n_mol, n_ang])
			atom1 += 1
	if val.model == 'Blend':
		for n_mol in range(val.ma_polymers, val.mb_polymers + val.ma_polymers):
			val.uobj.put(val.mol_name[1], p + 'Mol_Name', [n_mol])
			# beads
			for n_atom in range(val.nb_segments):
				# atom
				val.uobj.put(atom_id, 			pa + 'Atom_ID', [n_mol, n_atom])
				val.uobj.put(val.atom_name[1], 	pa + 'Atom_Name', [n_mol, n_atom])
				val.uobj.put(val.atom_name[1], 	pa + 'Atom_Type_Name', [n_mol, n_atom])
				val.uobj.put(0, 				pa + 'Chirality', [n_mol, n_atom])
				val.uobj.put(1, 				pa + 'Main_Chain', [n_mol, n_atom])
				# interaction site
				val.uobj.put(val.site_name[1], 	pi + 'Type_Name', [n_mol, n_atom])
				val.uobj.put(n_atom, 			pi + 'atom[]', [n_mol, n_atom, 0])
				atom_id += 1
			# bonds
			atom1 = 0
			ang_list=[]
			for n_bond in range(val.nb_segments - 1):
				val.uobj.put(val.bond_name[1], 	pb + 'Potential_Name', [n_mol, n_bond])
				val.uobj.put(atom1, 			pb + 'atom1', [n_mol, n_bond])
				ang_list.append(atom1)
				val.uobj.put(atom1 + 1, 		pb + 'atom2', [n_mol, n_bond])
				atom1 += 1
			# angles
			atom1 = 0
			for n_ang in range(val.nb_segments - 2):
				val.uobj.put(val.angle_name[1], pang + 'Potential_Name', [n_mol, n_ang])
				val.uobj.put(atom1, 			pang + 'atom1', [n_mol, n_ang])
				val.uobj.put(atom1 + 1, 		pang + 'atom2', [n_mol, n_ang])
				val.uobj.put(atom1 + 2, 		pang + 'atom3', [n_mol, n_ang])
				atom1 += 1
	
		# Draw_Attributes
		# color = ["Red", "Green", "Blue", "Magenta", "Cyan", "Yellow", "White", "Black", "Gray"]
		# mm = mul % 9
		# val.uobj.put([self.nw_name + '_' + str(mul), color[mm], 1.0, 1.0], 'Draw_Attributes.Molecule[]', [count])
		# count += 1

	#--- Write UDF ---
	val.uobj.write(val.target_udf)

	return
