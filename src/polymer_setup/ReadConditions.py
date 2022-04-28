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
		CalcCond:{
			Cognac_ver:select{"cognac112"} "使用する Cognac のバージョン",
			Cores: int "計算に使用するコア数を指定"
			} "計算の条件を設定"
		TargetCond:{
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
			Initialize:{
				Type:select{"SlowPO", "Harmonic"} "初期化条件を選択",
					SlowPO:{
						Step_rfc[]: float "Slow Push Off での rfc 条件",
						Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力",
						}
					Harmonic:{
						HarmonicBond_K:float "計算の繰り返し数",
						Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力"
						} 
				} "uuu",
			} "計算ターゲットの条件を設定"
		SimulationCond:{
			Setup_KG:{
					Repeat: int "計算の繰り返し数",
					Time:{delta_T: double, Total_Steps: int, Output_Interval_Steps: int} "時間条件を入力"
				} "計算の時間条件を入力",
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
		CalcCond:{"cognac112",1}
		TargetCond:{
		{"Homo", {20, 50}{20, 50, 20, 50, 1.}}
	{"SlowPO",
		{[1.073,1.0,0.9,0.8], {1.0e-02,1000000,5000}},
		{1000., {1.0e-02,100000,1000}}
		}
	}
SimulationCond:{
	{2,{1.0e-02,100000,1000}}
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
	val.ver_cognac = u.get('CalcCond.Cognac_ver')
	# 計算に使用するコア数
	val.core = u.get('CalcCond.Cores')
	# ベースとするUDFの名前
	val.base_udf = "base_uin.udf"
	val.blank_udf = val.ver_cognac + '.udf'
	#######################################################
	## 計算ターゲット
	###################
	## Polymerモデルの設定
	val.model = u.get('TargetCond.Model.TargetModel')
	if val.model == "Homo":
		val.na_segments = u.get('TargetCond.Model.Homo.N_Segments')
		val.ma_polymers = u.get('TargetCond.Model.Homo.M_Chains')
	elif val.model == "Blend":
		val.na_segments = u.get('TargetCond.Model.Blend.NA_Segments')
		val.ma_polymers = u.get('TargetCond.Model.Blend.MA_Chains')
		val.nb_segments = u.get('TargetCond.Model.Blend.NB_Segments')
		val.mb_polymers = u.get('TargetCond.Model.Blend.MB_Chains')
		val.epsilon = u.get('TargetCond.Model.Blend.epsilon_AB')
	# 
	val.initialize = u.get('TargetCond.Initialize.Type')
	if val.initialize == 'SlowPO':
		val.step_rfc = u.get('TargetCond.Initialize.SlowPO.Step_rfc[]')
		val.step_rfc_time = u.get('TargetCond.Initialize.SlowPO.Time')
	elif val.initialize == 'Harmonic':
		val.harmonicK = u.get('TargetCond.Initialize.Harmonic.HarmonicBond_K')
		val.harmonic_time = u.get('TargetCond.Initialize.Harmonic.Time')
	# シミュレーションの条件
	val.kg_repeat = u.get('SimulationCond.Setup_KG.Repeat')
	val.kg_time = u.get('SimulationCond.Setup_KG.Time')
	#
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
	text += "################################################" + "\n"
	text += "KG初期化計算繰り返し:\t\t\t" + str(val.kg_repeat) + "\n"
	text += "KG初期化時間条件:\t" + str(val.kg_time) + "\n"
	text += "平衡化計算繰り返し:\t\t\t" + str(val.equilib_repeat) + "\n"
	text += "平衡化時間条件:\t\t" + str(val.equilib_time ) + "\n"
	if val.greenkubo == 'Yes':
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
	os.makedirs(val.target_name, exist_ok = True)
	return
