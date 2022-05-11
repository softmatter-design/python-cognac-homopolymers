#!/usr/bin/env python
# -*- coding: utf-8 -*-
#######################################################
import os
import sys
import codecs
import numpy as np
#
from UDFManager import UDFManager
#
import polymer_setup.values as val
#######################################################
#
def setupcondition():
	# check 'polymer_condition.udf' and make it.
	findudf()
	# Read udf and setup initial conditions.
	read_and_setcondition()

	return
	
###########################################
# check 'polymer_condition.udf' and make it.
def findudf():
	if not os.path.isfile('./polymer_condition.udf'):
		print()
		print('In this directory, no "polymer_condition.udf" is found !')
		print('New one will be generated.')
		print('Please, modify and save it !\n')
		makenewudf()
		input('Press ENTER to continue...')
	return

###########################################
# make new udf when not found.
def makenewudf():
	contents = '''
	\\begin{def}
		CalcConditions:{
			Cognac_ver:select{"cognac112"} "使用する Cognac のバージョン",
			Cores: int "計算に使用するコア数を指定"
			} "Cognac による計算の条件を設定"
		Target:{
			Model:{TargetModel:select{"Homo", "Blend"} "対象となるポリマーのモデルを選択",
				Homo:{N_Segments: int "ポリマー中のセグメント数", 
					M_Chains: int "ポリマーの本数"
					} "条件を入力",
				Blend:{NA_Segments: int "ポリマー中のセグメント数", 
					MA_Chains: int "ポリマーの本数",
					NB_Segments: int "ポリマー中のセグメント数", 
					MB_Chains: int "ポリマーの本数",
					epsilon_AB: float "相互作用パラメタ",
					} "条件を入力"
				} "シミュレーションの条件を設定"
			} "計算ターゲットの条件を設定"
		
		PreTreatment:{
			Initialize:{
				Type:select{"SlowPO", "Harmonic"} "初期化条件を選択",
					SlowPO:{
						Step_rfc[]: float "Slow Push Off での rfc 条件",
						Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力",
						}
					Harmonic:{
						HarmonicBond_K:float "HarmoncBond のばね定数",
						Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力"
						} 
				} "",
			Setup_KG:{
					Repeat: int "計算の繰り返し数",
					Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力"
				} "KG Polymer の時間条件を入力",
			} "前処理条件を設定"
		
		Relaxation:{
			LAOS:{
				Calc:select{"Yes", "No"},
				Yes:{
					Repeat:int "計算の繰り返し数",
					N_LAOS:int "LAOS の繰り返し数",
					LAOS_Amp:float "LAOS の歪み",
					LAOS_Freq:float "LAOS の周波数"
					} "LAOS により緩和"
				},
			HeatCycle:{
				Calc:select{"Yes", "No"},
				Yes:{
					Repeat:int "計算の繰り返し数",
					Temperature[]:float "昇温温度を設定",
					Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力"
					} "昇温により緩和"
				},
			Final_Relaxation:{
					Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力"
					} "緩和の時間条件"
			} "緩和条件を設定"
		
		SimulationCond:{
			
			Equilib_Condition:{
					Repeat: int "平衡化計算の繰り返し数",
					Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "平衡化計算の時間条件を入力"
				} "平衡化計算の時間条件を入力",
			GreenKubo:{
				Calc:select{"Yes", "No"},
				Yes:{
					Repeat:int "計算の繰り返し数",
					Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力"
					} "GreenKubo により、応力緩和関数を計算するかどうかを決める。"
				}
			} "シミュレーションの条件を設定"
	\end{def}


	\\begin{data}
	CalcConditions:{"cognac112",1}
	Target:{
		{"Homo", {20, 50}{20, 50, 20, 50, 1.}}
	}
	
	PreTreatment:{
		{"SlowPO",
			{[1.073,1.0,0.9,0.8], {1.0e-02,1000000,5000}},
			{1000., {1.0e-02,100000,1000}}
		}
		{1,{1.0e-02,100000,1000}}
	}
	Relaxation:{
	{"Yes",{2,3,1.0,0.001}}
	{"Yes",{2,[2.0, 1.5, 1.0],{1.0e-02,1000000,10000}}}
	{{1.0e-02,100000,1000}}
	}
	SimulationCond:{
		{4,{1.0e-02,1000000,10000}}
		{"Yes",{5,{1.0e-02,1000000,10000}}}
	}
	\end{data}
	'''
	###
	with codecs.open('./polymer_condition.udf', 'w', 'utf_8') as f:
		f.write(contents)
	return

#######################################
# # Read udf and setup initial conditions
def read_and_setcondition():
	dic={'y':True,'yes':True,'q':False,'quit':False}
	while True:
		# read udf
		readconditionudf()
		# select
		init_calc()
		print('Change UDF: type [r]eload')
		print('Quit input process: type [q]uit')
		inp = input('Condition is OK ==> [y]es >> ').lower()
		if inp in dic:
			inp = dic[inp]
			break
		print('##### \nRead Condition UDF again \n#####\n\n')
	if inp:
		print("\n\nSetting UP progress !!")
		# 計算用のディレクトリーを作成
		make_dir()

		return
	else:
		sys.exit("##### \nQuit !!")

####################################
# Read condition udf
def readconditionudf():
	u = UDFManager('polymer_condition.udf')
	u.jump(-1)
	##################
	# 使用するCognacのバージョン
	val.ver_cognac = u.get('CalcConditions.Cognac_ver')
	# 計算に使用するコア数
	val.core = u.get('CalcConditions.Cores')
	# ベースとするUDFの名前
	val.base_udf = "base_uin.udf"
	val.blank_udf = val.ver_cognac + '.udf'
	#######################################################
	## 計算ターゲット
	###################
	## Polymerモデルの設定
	val.model = u.get('Target.Model.TargetModel')
	if val.model == "Homo":
		val.na_segments = u.get('Target.Model.Homo.N_Segments')
		val.ma_polymers = u.get('Target.Model.Homo.M_Chains')
	elif val.model == "Blend":
		val.na_segments = u.get('Target.Model.Blend.NA_Segments')
		val.ma_polymers = u.get('Target.Model.Blend.MA_Chains')
		val.nb_segments = u.get('Target.Model.Blend.NB_Segments')
		val.mb_polymers = u.get('Target.Model.Blend.MB_Chains')
		val.epsilon = u.get('Target.Model.Blend.epsilon_AB')
	# 
	val.initialize = u.get('PreTreatment.Initialize.Type')
	if val.initialize == 'SlowPO':
		val.step_rfc = u.get('PreTreatment.Initialize.SlowPO.Step_rfc[]')
		val.step_rfc_time = u.get('PreTreatment.Initialize.SlowPO.Time')
	elif val.initialize == 'Harmonic':
		val.harmonicK = u.get('PreTreatment.Initialize.Harmonic.HarmonicBond_K')
		val.harmonic_time = u.get('PreTreatment.Initialize.Harmonic.Time')
	#
	val.kg_repeat = u.get('PreTreatment.Setup_KG.Repeat')
	val.kg_time = u.get('PreTreatment.Setup_KG.Time')
	# 
	val.laos = u.get('Relaxation.LAOS.Calc')
	if val.laos == 'Yes':
		val.laos_repeat = u.get('Relaxation.LAOS.Yes.Repeat')
		val.laos_n = u.get('Relaxation.LAOS.Yes.N_LAOS')
		val.laos_amp =  u.get('Relaxation.LAOS.Yes.LAOS_Amp')
		val.laos_freq =  u.get('Relaxation.LAOS.Yes.LAOS_Freq')
		val.laos_time = [val.laos_period, int(val.laos_n/val.laos_freq/val.laos_period), int(1/val.laos_freq/val.laos_period/100)]
	#
	val.heat = u.get('Relaxation.HeatCycle.Calc')
	if val.heat == 'Yes':
		val.heat_repeat = u.get('Relaxation.HeatCycle.Yes.Repeat')
		val.heat_temp = u.get('Relaxation.HeatCycle.Yes.Temperature[]')
		val.heat_time = u.get('Relaxation.HeatCycle.Yes.Time')
	#
	val.final_time = u.get('Relaxation.Final_Relaxation.Time')
	# シミュレーションの条件
	val.equilib_repeat = u.get('SimulationCond.Equilib_Condition.Repeat')
	val.equilib_time = u.get('SimulationCond.Equilib_Condition.Time')
	#
	val.greenkubo = u.get('SimulationCond.GreenKubo.Calc')
	if val.greenkubo == 'Yes':
		val.greenkubo_repeat = u.get('SimulationCond.GreenKubo.Yes.Repeat')
		val.greenkubo_time = u.get('SimulationCond.GreenKubo.Yes.Time')
	return

###############################################################
def init_calc():
	segments = val.na_segments*val.ma_polymers + val.nb_segments*val.mb_polymers
	text = "################################################" + "\n"
	text += "計算に使用するコア数\t\t\t" + str(val.core ) + "\n"
	text += "################################################" + "\n"
	text += "ターゲット\t\t\t\t" + str(val.model) + "\n"
	if val.model == "Homo":
		text += "ポリマーAのセグメント数:\t\t" + str(val.na_segments) + "\n"
		text += "ポリマーAの本数:\t\t\t" + str(val.ma_polymers) + "\n"
		val.mol_name = ["polymerA"]
		val.atom_name = ["A"]
		val.bond_name = ["bond_AA"]
		val.angle_name = ["angle_AAA"]
		val.site_name = ["site_A"]
		val.pair_name = ["site_A-site_A"]
		val.site_pair_name = [ 
						["site_A", "site_A"], 
						["site_B", "site_B"], 
						["site_A", "site_B"]
						]
	else:
		text += "ポリマーAのセグメント数:\t\t" + str(val.na_segments) + "\n"
		text += "ポリマーAの本数:\t\t\t" + str(val.ma_polymers) + "\n"
		text += "ポリマーBのセグメント数:\t\t" + str(val.nb_segments) + "\n"
		text += "ポリマーBの本数:\t\t\t" + str(val.mb_polymers) + "\n"
		text += "相互作用パラメタ:\t\t\t" + str(val.epsilon) + "\n"
		val.mol_name = ["polymerA", "polymerB"]
		val.atom_name = ["A", "B"]
		val.bond_name = ["bond_AA", "bond_BB"]
		val.angle_name = ["angle_AAA", "angle_BBB"]
		val.site_name = ["site_A", "site_B"]
		val.pair_name = ["site_A-site_A", "site_B-site_B", "site_A-site_B"]
		val.site_pair_name = [ 
						["site_A", "site_A"], 
						["site_B", "site_B"], 
						["site_A", "site_B"]
						]
	text += "全セグメント数:\t\t\t\t" + str(segments) + "\n"
	text += "################################################" + "\n"
	text += "初期化条件:\t\t\t\t" + val.initialize + "\n"
	if val.initialize == 'SlowPO':
		text += "Slow Push Off 条件:\t" + ', '.join(map(str, val.step_rfc)) + "\n"
		text += "Slow Push Off 時間条件:\t" + str(val.step_rfc_time) + "\n"
	else:
		text += "ばね定数:\t\t\t\t" + str(val.harmonicK) + "\n"
		text += "時間条件:\t\t" + str(val.harmonic_time) + "\n"
	text += "##\n"
	text += "KG初期化計算繰り返し:\t\t\t" + str(val.kg_repeat) + "\n"
	text += "KG初期化時間条件:\t" + str(val.kg_time) + "\n"
	if val.laos == 'Yes':
		text += "################################################" + "\n"
		text += "緩和条件:\n"
		text += "LAOS 操作の繰り返し:\t\t\t" + str(val.laos_repeat) + "\n"
		text += "LAOS 回数:\t\t\t\t" + str(val.laos_n) + "\n"
		text += "最大ひずみ:\t\t\t\t" + str(val.laos_amp) + "\n"
		text += "周波数:\t\t\t\t\t" + str(val.laos_freq) + "\n"
		text += "LAOS 計算の時間条件:\t" + str(val.laos_time) + "\n"
	if val.laos == 'No' and val.heat == 'Yes':
		text += "################################################" + "\n"
		text += "緩和条件:\n"
	if val.heat == 'Yes':
		text += "##\n"
		text += "昇温緩和の繰り返し:\t\t\t" + str(val.heat_repeat) + "\n"
		text += "昇温緩和の温度条件:\t\t" + str(val.heat_temp) + "\n"
		text += "昇温緩和の時間条件:\t" + str(val.heat_time) + "\n"
	text += "##\n"
	text += "最終緩和の時間条件:\t" + str(val.final_time) + "\n"
	text += "################################################" + "\n"
	text += "平衡化計算繰り返し:\t\t\t" + str(val.equilib_repeat) + "\n"
	text += "平衡化時間条件:\t\t" + str(val.equilib_time ) + "\n"
	if val.greenkubo == 'Yes':
		text += "##\n"
		text += "応力緩和計算繰り返し:\t\t\t" + str(val.greenkubo_repeat) + "\n"
		text += "応力緩和時間条件:\t" + str(val.greenkubo_time) + "\n"
	text += "################################################" + "\n"
	print(text)
	return

################################################################################
# 計算用のディレクトリーを作成
def make_dir():
	if val.model == "Homo":
		val.target_name = val.model + '_NA_' + str(val.na_segments) + "_" + val.initialize
	else:
		val.target_name = val.model + '_NA_' + str(val.na_segments) + '_NB_' + str(val.nb_segments) + '_epsilon_' + str(val.epsilon).replace('.', '_') + "_" + val.initialize
	if val.laos == 'Yes':
		val.target_name += '_wLAOS'
	if val.heat == 'Yes':
		val.target_name += '_wHeat'

	if os.path.exists(val.target_name):
		print('\nTarget Dir of ', val.target_name, 'exists !!')
		print('\nQuit: type [q]uit')
		inp = input('Overwrite ==> [y]es >> ').lower()
		if inp in ['q','quit']:
			sys.exit('bye')
		else:
			print("Overwrite ", val.target_name)
			os.makedirs(val.target_name, exist_ok=True)
	else:
		print("\nMake new dir of ", val.target_name)
		os.makedirs(val.target_name)
	return
