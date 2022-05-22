#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
import numpy as np
import platform
import os

from UDFManager import UDFManager

import polymer_setup.values as val
##########################################
# UDF の作成
##########################################
# UDFファイルを設定し、バッチ処理を作成
def setup_all():
	# バッチファイルの初期化
	pre_batch()
	# UDF ファイルを設定
	setup_udf()
	# バッチファイルを作成
	write_batch()
	return

##############################################
# 各種バッチ条件を設定
def pre_batch():
	if platform.system() == "Windows":
		val.batch = ""
	elif platform.system() == "Linux":
		val.batch = "#!/bin/bash\n"
	return

def add_batch():
	# ターミナルのタイトルを設定
	if platform.system() == "Windows":
		val.batch += "title " + val.title + "\n"
	elif platform.system() == "Linux":
		val.batch += r'echo -ne "\033]0; ' + val.title + ' \007"' + '\n'
	# ファイル名を変更してバッチファイルに追加
	val.present_udf = val.file_name
	val.out_udf = val.present_udf.replace("uin", "out")
	val.batch += val.ver_cognac + ' -I ' + val.present_udf + ' -O ' + val.out_udf + ' -n ' + str(val.core) + ' \n'
	if val.f_eval:
		val.batch += val.f_eval_py + ' ' + val.out_udf + '\n'
	return

def write_batch():
	f_batch = os.path.join(val.target_name, '_Calc_all.bat')
	with open(f_batch, 'w') as f:
		f.write(val.batch)
	if platform.system() == "Linux":
		os.chmod(f_batch, 0o777)
	return

#####################
def setup_udf():
	val.template = val.base_udf
	val.read_udf = ''
	# Initial_Structure に応じて計算条件を選択
	initial()
	# PreTreatment に応じて計算条件を選択
	preTreatment()
	# Relaxation に応じて緩和計算を設定
	relaxation()
	# SimulationCond に応じて設定
	simulation()
	return
######################################################################
# 初期化条件の設定
def initial():
	val.title = "Calculating-Initial_Structure"
	if val.init_fixangle == 'Fix' and val.init_nonbond == 'LJ':
		val.file_name = "Initial_fixangle_LJ_uin.udf"
	elif val.init_fixangle == 'Fix':
		val.file_name = "Initial_fixangle_noLJ_uin.udf"
	elif val.init_nonbond == 'LJ':
		val.file_name = "Initial_LJ_uin.udf"
	else:
		val.file_name = "Initial_noLJ_uin.udf"
	val.f_eval = val.initial_eval
	add_batch()
	initial_random()
	val.read_udf, val.template = val.out_udf, val.present_udf
	return

# 前処理条件
def preTreatment():
	if val.spo == "Calc":
		# Force Capped LJ によりステップワイズに初期化
		for val.rfc in val.spo_r:
			val.title = "Calculating-Pre_SlowPushOff_r_" + str(round(val.rfc, 3)).replace('.', '_')
			val.file_name = 'Pre_rfc_' + str(round(val.rfc, 3)).replace('.', '_') + "_uin.udf"
			val.f_eval = val.spo_eval
			add_batch()
			slowpushoff()
			val.read_udf, val.template = val.out_udf, val.present_udf
	# KG鎖へと変換
	for i in range(val.kg_repeat):
		val.title = "Calculating-Pre_KG_" + str(i)
		val.file_name = 'Pre_KG_' + str(i)  + "_uin.udf"
		val.f_eval = val.kg_eval
		add_batch()
		kg_setup()
		val.read_udf, val.template = val.out_udf, val.present_udf
	return

# 緩和条件の設定
def relaxation():
	if val.laos == "Calc":
		# LAOS により構造緩和
		val.title = "Calculating-Relax_LAOS"
		val.file_name = 'Relax_LAOS_uin.udf'
		val.f_eval = val.laos_eval
		add_batch()
		#
		laos()
		val.read_udf, val.template = val.out_udf, val.present_udf
			
	if val.heat == "Calc":
		# 加温することにより構造緩和
		for i in range(val.heat_repeat):
			for val.temp in val.heat_temp:
				val.title = "Calculating-Relax_Heat" + str(i+1) + '_in_' + str(val.heat_repeat) + '_Temp_' + str(val.temp).replace('.', '_')
				val.file_name = 'Relax_Temp_' + str(val.temp).replace('.', '_') + '_rep_' + str(i+1) + "_uin.udf"
				val.f_eval = val.heat_eval
				add_batch()
				#
				heat()
				val.read_udf, val.template = val.out_udf, val.present_udf

	# 放置することにより緩和
	val.title = "Calculating-Relax"
	val.file_name = 'Relax_final_uin.udf'
	val.f_eval = val.final_eval
	add_batch()
	#
	cont(val.final_time)
	val.read_udf, val.template = val.out_udf, val.present_udf
	return

# SimulationCond に応じて設定
def simulation():
	# 平衡状態でのサンプリング
	for i in range(val.equilib_repeat):
		val.title = 'Calculating-Simulation_Equilibrium_' + str(i)
		val.file_name = 'Equilibrium_' + str(i) + '_uin.udf'
		val.f_eval = val.final_eval
		add_batch()
		#
		cont(val.equilib_time)
		val.read_udf, val.template = val.out_udf, val.present_udf
	for i in range(val.greenkubo_repeat):
		val.title = "Calculating-GreenKubo"
		val.file_name = 'GK_' + str(i) + '_uin.udf'
		val.f_eval = val.final_eval
		add_batch()
		#
		greenkubo()
		val.read_udf, val.template = val.out_udf, val.present_udf
	return

##############################################################################
# UDF 作成条件
#
def initial_random():
	time = [0.005, 10000, 100]
	u = UDFManager(os.path.join(val.target_name, val.template))
	# goto global data
	u.jump(-1)
	#--- Simulation_Conditions ---
	# Dynamics_Conditions
	p = 'Simulation_Conditions.Dynamics_Conditions.'
	u.put(100000000., 	p + 'Max_Force')
	u.put(time[0], p + 'Time.delta_T')
	u.put(time[1], p + 'Time.Total_Steps')
	u.put(time[2], p + 'Time.Output_Interval_Steps')
	u.put(1.0, 					p + 'Temperature.Temperature')
	u.put(0., 					p + 'Pressure_Stress.Pressure')
	# Calc_Potential_Flags
	p = 'Simulation_Conditions.Calc_Potential_Flags.'
	u.put(1, p + 'Bond')
	u.put(0, p + 'Angle')
	if val.init_nonbond == 'LJ':
		u.put(1, p + 'Non_Bonding_Interchain')
		u.put(1, p + 'Non_Bonding_1_3')
		u.put(1, p + 'Non_Bonding_1_4')
		u.put(1, p + 'Non_Bonding_Intrachain')
	else:
		u.put(0, p + 'Non_Bonding_Interchain')
		u.put(0, p + 'Non_Bonding_1_3')
		u.put(0, p + 'Non_Bonding_1_4')
		u.put(0, p + 'Non_Bonding_Intrachain')
	#--- Initial_Structure ---
	# Initial_Unit_Cell
	p = 'Initial_Structure.Initial_Unit_Cell.'
	u.put(val.density, p + 'Density')
	u.put([0, 0, 0, 90.0, 90.0, 90.0], p + 'Cell_Size')
	# Generate_Method
	# Set atoms
	p = 'Initial_Structure.Generate_Method.'
	u.put('Random', p + 'Method')
	u.put('Fix', p + 'Random.Angle.Constraint')
	# Relaxation
	p = 'Initial_Structure.Relaxation.'
	u.put(1, p + 'Relaxation')
	u.put('DYNAMICS', p + 'Method')
	u.put(200, p + 'Max_Relax_Force')
	u.put(100000, p + 'Max_Relax_Steps')
	#--- Simulation_Conditions ---
	# bond
	for i, b_name in enumerate(val.bond_name):
		p = 'Molecular_Attributes.Bond_Potential[].'
		u.put(b_name, 		p + 'Name', [i])
		u.put('Harmonic', 	p + 'Potential_Type', [i])
		u.put(0.97,			p + 'R0', [i])
		u.put(1000, 		p + 'Harmonic.K', [i])
	# Angle
	for i, anglename in enumerate(val.angle_name):
		p = 'Molecular_Attributes.Angle_Potential[].'
		u.put(anglename, 		p + 'Name', [i])
		u.put('Theta2', 		p + 'Potential_Type', [i])
		u.put(val.fix_angle, 	p + 'theta0', [i])
		u.put(10.0, 			p + 'Theta2.K', [i])
	#--- Pair_Interaction[] ---
	for i, pairname in enumerate(val.pair_name):
		p = 'Interactions.Pair_Interaction[].'
		u.put(pairname,   				p + 'Name', [i])
		u.put('Lennard_Jones', 			p + 'Potential_Type', [i])
		u.put(val.site_pair_name[i][0],	p + 'Site1_Name', [i])
		u.put(val.site_pair_name[i][1],	p + 'Site2_Name', [i])
		u.put(2**(1/6),					p + 'Cutoff', [i])
		u.put(1.0,						p + 'Scale_1_4_Pair', [i])
		u.put(1.0,						p + 'Lennard_Jones.sigma', [i])
		u.put(1.0,					p + 'Lennard_Jones.epsilon', [i])
	#--- Write UDF ---
	u.write(os.path.join(val.target_name, val.present_udf))
	
	return

# ユーザーポテンシャルにより、Force Capped LJ で、ステップワイズにノンボンドを増加
def slowpushoff():
	time = val.spo_time
	u = UDFManager(os.path.join(val.target_name, val.template))
	# goto global data
	u.jump(-1)
	#--- Simulation_Conditions ---
	# Dynamics_Conditions
	p = 'Simulation_Conditions.Dynamics_Conditions.'
	u.put(100000000., 	p + 'Max_Force')
	u.put(time[0], p + 'Time.delta_T')
	u.put(time[1], p + 'Time.Total_Steps')
	u.put(time[2], p + 'Time.Output_Interval_Steps')
	u.put(1.0, 					p + 'Temperature.Temperature')
	u.put(0., 					p + 'Pressure_Stress.Pressure')
	# Calc_Potential_Flags
	p = 'Simulation_Conditions.Calc_Potential_Flags.'
	u.put(1, p + 'Bond')
	u.put(1, p + 'Angle')
	u.put(1, p + 'Non_Bonding_Interchain')
	u.put(1, p + 'Non_Bonding_1_3')
	u.put(1, p + 'Non_Bonding_1_4')
	u.put(1, p + 'Non_Bonding_Intrachain')
	#--- Initial_Structure ---
	# Initial_Unit_Cell
	p = 'Initial_Structure.Initial_Unit_Cell.'
	u.put(val.density, p + 'Density')
	u.put([0, 0, 0, 90.0, 90.0, 90.0], p + 'Cell_Size')
	# Generate_Method
	if val.read_udf == '':
		# Set atoms
		p = 'Initial_Structure.Generate_Method.'
		u.put('Random', p + 'Method')
		# Relaxation
		p = 'Initial_Structure.Relaxation.'
		u.put(1, p + 'Relaxation')
		u.put('DYNAMICS', p + 'Method')
		u.put(200, p + 'Max_Relax_Force')
		u.put(100000, p + 'Max_Relax_Steps')
	else:
		p = 'Initial_Structure.Generate_Method.'
		u.put('Restart', p+'Method')
		u.put([val.read_udf, -1, 1, 0], p+'Restart')
		# Relaxation
		p = 'Initial_Structure.Relaxation.'
		u.put(1, p + 'Relaxation')
	#--- Simulation_Conditions ---
	# bond
	for i, b_name in enumerate(val.bond_name):
		p = 'Molecular_Attributes.Bond_Potential[].'
		u.put(b_name, 				p + 'Name', [i])
		u.put('Bond_Polynomial',	p + 'Potential_Type', [i])
		u.put(0.9609,				p + 'R0', [i])
		u.put(3,					p + 'Bond_Polynomial.N', [i])
		u.put(20.2026,				p + 'Bond_Polynomial.p[]', [i, 0])
		u.put(490.628,				p + 'Bond_Polynomial.p[]', [i, 1])
		u.put(2256.76,				p + 'Bond_Polynomial.p[]', [i, 2])
		u.put(9685.31,				p + 'Bond_Polynomial.p[]', [i, 3])
		u.put('YES',				p + 'Bond_Polynomial.Use_Equilibrated_Value', [i])
	# Angle
	for i, anglename in enumerate(val.angle_name):
		p = 'Molecular_Attributes.Angle_Potential[].'
		u.put(anglename, 		p + 'Name', [i])
		u.put('Force_Cap_LJ', 	p + 'Potential_Type', [i])
		u.put(73.0, 			p + 'theta0', [i])
		u.put(1.0, 				p + 'Force_Cap_LJ.sigma', [i])
		u.put(1.0, 				p + 'Force_Cap_LJ.epsilon', [i])
		u.put(1.122462, 		p + 'Force_Cap_LJ.cutoff', [i])
		u.put(0.8, 				p + 'Force_Cap_LJ.r_FC', [i])
	#--- Pair_Interaction[] ---
	for i, pairname in enumerate(val.pair_name):
		p = 'Interactions.Pair_Interaction[].'
		u.put(pairname,   				p + 'Name', [i])
		u.put('Force_Cap_LJ', 			p + 'Potential_Type', [i])
		u.put(val.site_pair_name[i][0],	p + 'Site1_Name', [i])
		u.put(val.site_pair_name[i][1],	p + 'Site2_Name', [i])
		u.put(1.12246204830937,			p + 'Cutoff', [i])
		u.put(1.0,						p + 'Scale_1_4_Pair', [i])
		u.put(1.0,						p + 'Force_Cap_LJ.sigma', [i])
		u.put(1.0,						p + 'Force_Cap_LJ.epsilon', [i])
		u.put(val.rfc,						p + 'Force_Cap_LJ.r_FC', [i])
	#--- Write UDF ---
	u.write(os.path.join(val.target_name, val.present_udf))
	
	return

# ボンドをFENE、ノンボンドをLJとしてKG鎖を設定
def kg_setup():
	time = val.kg_time
	u = UDFManager(os.path.join(val.target_name, val.template))
	# goto global data
	u.jump(-1)
	#--- Simulation_Conditions ---
	# Dynamics_Conditions
	p = 'Simulation_Conditions.Dynamics_Conditions.'
	u.put(time[0], p + 'Time.delta_T')
	u.put(time[1], p + 'Time.Total_Steps')
	u.put(time[2], p + 'Time.Output_Interval_Steps')
	# Calc_Potential_Flags
	p = 'Simulation_Conditions.Calc_Potential_Flags.'
	u.put(1, p + 'Bond')
	u.put(0, p + 'Angle')
	u.put(1, p + 'Non_Bonding_Interchain')
	u.put(1, p + 'Non_Bonding_1_3')
	u.put(1, p + 'Non_Bonding_1_4')
	u.put(1, p + 'Non_Bonding_Intrachain')
	#--- Initial_Structure ---
	# Initial_Unit_Cell
	p = 'Initial_Structure.Initial_Unit_Cell.'
	u.put(val.density, p + 'Density')
	u.put([0, 0, 0, 90.0, 90.0, 90.0], p + 'Cell_Size')
	# Generate_Method
	p = 'Initial_Structure.Generate_Method.'
	u.put('Restart', p+'Method')
	u.put([val.read_udf, -1, 1, 0], p+'Restart')
	# Relaxation
	p = 'Initial_Structure.Relaxation.'
	u.put(1, p + 'Relaxation')
	u.put('DYNAMICS', p + 'Method')
	u.put(200, p + 'Max_Relax_Force')
	u.put(100000, p + 'Max_Relax_Steps')
	#--- Simulation_Conditions ---
	# bond
	for i, b_name in enumerate(val.bond_name):
		p = 'Molecular_Attributes.Bond_Potential[].'
		u.put(b_name, 		p + 'Name', [i])
		u.put('FENE_LJ', 	p + 'Potential_Type', [i])
		u.put(1.0,			p + 'R0', [i])
		u.put(1.5,			p + 'FENE_LJ.R_max', [i])
		u.put(30,			p + 'FENE_LJ.K', [i])
		u.put(1.0,			p + 'FENE_LJ.sigma', [i])
		u.put(1.0,			p + 'FENE_LJ.epsilon', [i])
	#--- Pair_Interaction[] ---
	for i, pairname in enumerate(val.pair_name):
		p = 'Interactions.Pair_Interaction[].'
		u.put(pairname,   				p + 'Name', [i])
		u.put('Lennard_Jones', 			p + 'Potential_Type', [i])
		u.put(val.site_pair_name[i][0],	p + 'Site1_Name', [i])
		u.put(val.site_pair_name[i][1],	p + 'Site2_Name', [i])
		u.put(2**(1/6),					p + 'Cutoff', [i])
		u.put(1.0,						p + 'Scale_1_4_Pair', [i])
		u.put(1.0,						p + 'Lennard_Jones.sigma', [i])
		if pairname == "site_A-site_B":
			u.put(1.0 + val.epsilon,	p + 'Lennard_Jones.epsilon', [i])
		else:
			u.put(1.0,					p + 'Lennard_Jones.epsilon', [i])
	#--- Write UDF ---
	u.write(os.path.join(val.target_name, val.present_udf))

	return

# LAOS による緩和
def laos():
	time = val.laos_time
	u = UDFManager(os.path.join(val.target_name, val.template))
	# goto global data
	u.jump(-1)
	#--- Simulation_Conditions ---
	# Dynamics_Conditions
	p = 'Simulation_Conditions.Dynamics_Conditions.'
	u.put(time[0], 	p + 'Time.delta_T')
	u.put(time[1], 	p + 'Time.Total_Steps')
	u.put(time[2], 	p + 'Time.Output_Interval_Steps')
	#
	u.put('Lees_Edwards', 	p + 'Deformation.Method')
	u.put('Dynamic', 		p + 'Deformation.Lees_Edwards.Method')
	u.put(val.laos_amp, 	p + 'Deformation.Lees_Edwards.Dynamic.Amplitude')
	u.put(val.laos_freq, 	p + 'Deformation.Lees_Edwards.Dynamic.Frequency')
	# Generate_Method
	p = 'Initial_Structure.Generate_Method.'
	u.put('Restart', p+'Method')
	u.put([val.read_udf, -1, 1, 0], p+'Restart')
	# Relaxation
	p = 'Initial_Structure.Relaxation.'
	u.put(1, p + 'Relaxation')
	#--- Write UDF ---
	u.write(os.path.join(val.target_name, val.present_udf))

	return

# 加温による緩和
def heat():
	time = val.heat_time
	u = UDFManager(os.path.join(val.target_name, val.template))
	# goto global data
	u.jump(-1)
	#--- Simulation_Conditions ---
	# Dynamics_Conditions
	p = 'Simulation_Conditions.Dynamics_Conditions.'
	u.put(time[0], p + 'Time.delta_T')
	u.put(time[1], p + 'Time.Total_Steps')
	u.put(time[2], p + 'Time.Output_Interval_Steps')
	u.put(val.temp, 		p + 'Temperature.Temperature')
	# Generate_Method
	p = 'Initial_Structure.Generate_Method.'
	u.put('Restart', p+'Method')
	u.put([val.read_udf, -1, 1, 0], p+'Restart')
	# Relaxation
	p = 'Initial_Structure.Relaxation.'
	u.put(1, p + 'Relaxation')
	#--- Write UDF ---
	u.write(os.path.join(val.target_name, val.present_udf))
	return

# 直前の条件を維持して平衡化
def cont(time):
	u = UDFManager(os.path.join(val.target_name, val.template))
	u.jump(-1)
	#--- Simulation_Conditions ---
	# Dynamics_Conditions
	p = 'Simulation_Conditions.Dynamics_Conditions.'
	u.put(time[0],  p+'Time.delta_T')
	u.put(time[1],  p+'Time.Total_Steps')
	u.put(time[2],  p+'Time.Output_Interval_Steps')
	# Generate_Method
	p = 'Initial_Structure.Generate_Method.'
	u.put('Restart', p+'Method')
	u.put([val.read_udf, -1, 1, 0], p+'Restart')
	# Relaxation
	p = 'Initial_Structure.Relaxation.'
	u.put(1, p + 'Relaxation')
	#--- Write UDF ---
	u.write(os.path.join(val.target_name, val.present_udf))
	return

# グリーン久保計算
def greenkubo():
	time = val.greenkubo_time
	u = UDFManager(os.path.join(val.target_name, val.template))
	u.jump(-1)
	#--- Simulation_Conditions ---
	# Dynamics_Conditions
	p = 'Simulation_Conditions.Dynamics_Conditions.'
	u.put(time[0],  p+'Time.delta_T')
	u.put(time[1],  p+'Time.Total_Steps')
	u.put(time[2],  p+'Time.Output_Interval_Steps')
	# Calc Correlation
	u.put(1, 'Simulation_Conditions.Output_Flags.Correlation_Function.Stress')
	# Generate_Method
	p = 'Initial_Structure.Generate_Method.'
	u.put('Restart', p+'Method')
	u.put([val.read_udf, -1, 1, 0], p+'Restart')
	# Relaxation
	p = 'Initial_Structure.Relaxation.'
	u.put(1, p + 'Relaxation')
	#--- Write UDF ---
	u.write(os.path.join(val.target_name, val.present_udf))
	return


#################################################

# アトムのポジションを回転
def rotate_position(u, axis):
	R = rotate(axis, np.pi/2.)
	u.jump(u.totalRecord() - 1)
	pos = u.get('Structure.Position.mol[].atom[]')
	for i, mol in enumerate(pos):
		for j, atom in enumerate(mol):
			tmp = list(np.array(R).dot(np.array(atom)))
			u.put(tmp, 'Structure.Position.mol[].atom[]', [i, j])
	return

def rotate(axis, deg):
	if axis == 'x':
		R = [
			[1., 0., 0.],
			[0., np.cos(deg), -1*np.sin(deg)],
			[0., np.sin(deg), np.cos(deg)]
		]
	elif axis == 'y':
		R = [
			[np.cos(deg), 0., np.sin(deg)],
			[0., 1., 0.],
			[-1*np.sin(deg), 0., np.cos(deg)]
		]
	elif axis == 'z':
		R = [
			[np.cos(deg), -1*np.sin(deg), 0.],
			[np.sin(deg), np.cos(deg), 0.],
			[0., 0., 1.]
		]
	return R