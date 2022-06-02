#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
# Import Modules
################################################################################
from UDFManager import UDFManager
import os
import sys
import math
import cmath
import numpy as np
import platform
import subprocess
import scipy.signal as signal
#
import CognacUtility as CU
from CognacBasicAnalysis import *
from CognacGeometryAnalysis import CognacGeometryAnalysis

import chain_evaluation.values as val
################################################################################
################################################################################
def sqcalc():
	# 対象となる udf ファイルを選択
	select_udf()
	# ポリマー鎖関連の特性情報を計算
	evaluate()
	# 計算結果を出力
	make_output()
	return

##########################################
# 対象となる udf ファイルを選択
def select_udf():
	param = sys.argv
	if len(param) == 1:
		print("usage: python", param[0], "Honya_out.udf")
		exit(1)
	elif not os.access(param[1],os.R_OK):
		print(param[1], "not exists.")
		exit(1)
	elif len(param) > 2:
		val.blend_a = param[2]
	val.target = param[1]
	val.target_name = val.target.split('.')[0]
	val.uobj = UDFManager(val.target)
	return

###############################################################################
# ポリマー鎖関連の特性情報を計算
###############################################################################
def evaluate():
	rec_size = val.uobj.totalRecord()
	for rec in range(1, rec_size):
		print("Reading Rec=", rec, '/', rec_size - 1)
		read_chain(rec)
	#
	calc_sq()
	return

def read_chain(rec):
	val.uobj.jump(rec)
	val.systemsize = val.uobj.get('Structure.Unit_Cell.Cell_Size.a')
	mols = val.uobj.get('Structure.Position.mol[].atom[]')
	step_sq(mols)

	return

##############################
# 
def step_sq(mols):
	n = 20
	unitq = 2.*np.pi/val.systemsize
	qsize = int(val.systemsize)
	val.q_list = [unitq + unitq*i/5 for i in range(qsize*5)]
	sq = [[] for i in range(len(val.q_list))]
	for i, data in enumerate(sq):
		count = 0
		tmpcos = 0
		tmpsin = 0
		for chain in mols:
			for ri in chain:
				uvec = randvec(n)
				
				for uvec_i in uvec:
					qvec = val.q_list[i]*np.array(uvec_i)
					vecdot = np.dot(np.array(ri), qvec)
					tmpcos += np.cos(vecdot)
					tmpsin += np.sin(vecdot)
					count += 1
					data.append((tmpcos**2 + tmpsin**2)/count)
	val.sq_step.append(np.average(sq, axis = 1))
	return

def randvec(n):
	uvec = []
	for i in range(n):
		z = 2.*np.random.rand() - 1.
		radT = np.radians(360.*np.random.rand())
		x = np.sqrt(1-z**2)*np.cos(radT)
		y = np.sqrt(1-z**2)*np.sin(radT)
		uvec.append([x, y, z])
	return uvec


def calc_sq():
	tmp_sq = np.average(np.array(val.sq_step), axis = 0)
	for i, q in enumerate(val.q_list):
		val.sq_list.append([q, tmp_sq[i]])
	return



###############################################################################
# 計算結果を出力
###############################################################################
def make_output():
	# マルチ形式での出力
	multi_list = [
			["Sq", val.sq_list, ['q', 'S(q)']],
			["Guinier", val.sq_list, ['q2', 'ln S(q)']]
			]
			# ["gr", val.gr_list, ['Distance', 'g(r)']],
	for cond in multi_list:
		make_multi(cond)
	return

##########################
# マルチリストのグラフの作成
def make_multi(cond_list):
	val.base_name = cond_list[0]
	val.data_list = cond_list[1]
	val.leg = cond_list[2]
	val.target_dir = os.path.join(val.target_name, val.base_name)
	val.f_dat = val.base_name + "_hist.dat"
	val.f_plt = val.base_name + ".plt"
	val.f_png = val.base_name + ".png"

	# データを書き出し 
	write_multi_data()
	# グラフを作成
	make_multi_graph()
	return

# データを書き出し 
def write_multi_data():
	os.makedirs(val.target_dir, exist_ok=True)
	with open(os.path.join(val.target_dir, val.f_dat), 'w') as f:
		f.write("# data:\n")
		if val.base_name == 'Sq' or val.base_name == 'Guinier':
			for line in val.data_list:
				for data in line:
					f.write(str(data) + '\t')
				f.write('\n')
		else:
			for i, data in enumerate(val.data_list):
				f.write("\n\n# " + str(i) +":\n\n")
				for line in data:
					f.write(str(line[0]) + '\t' + str(line[1])  + '\n')
	return

# グラフを作成
def make_multi_graph():
	make_multi_script()
	cwd = os.getcwd()
	os.chdir(val.target_dir)
	if platform.system() == "Windows":
		subprocess.call(val.f_plt, shell=True)
	elif platform.system() == "Linux":
		subprocess.call('gnuplot ' + val.f_plt, shell=True)
	os.chdir(cwd)
	return

# 必要なスクリプトを作成
def make_multi_script():
	with open(os.path.join(val.target_dir, val.f_plt), 'w') as f:
		script = multi_script_content()
		f.write(script)
	return

# スクリプトの中身
def multi_script_content():
	repeat = len(val.data_list )
	#
	script = 'set term pngcairo font "Arial,14" \nset colorsequence classic \n'
	script += '# \ndata = "' + val.f_dat + '" \nset output "' + val.f_png + ' "\n'
	script += '#\nset size square\n#set xrange [1:]\n#set yrange [1:]\n'
	script += '#\nset xlabel "' + val.leg[0] + '"\nset ylabel "' + val.leg[1] + '"\n\n'
	#
	if val.base_name == "CN" or val.base_name == "CN_ave" or val.base_name == "CN_part":
		script += '#\nset xrange [1:]\nset yrange [1:]\n'
		script += 'set key bottom\n\n'
		script += 'ct = 0.274\n'
		script += "f(x) = (1+ct)/(1-ct) -(2*ct*(1-ct**x))/(1-ct)**2/x\n\n"
		script += 'plot '
		if val.base_name == "CN":
			for i in range(repeat):
				script += 'data ind ' + str(i) + ' w l lc ' + str(i) + ' noti, \\\n'
		elif val.base_name == "CN_part":
			for i in range(repeat):
				script += 'data ind ' + str(i) + ' w l lc ' + str(i) + ' ti "part:' + str(i) + '", \\\n'
		else:
			script += 'data w l ti "averaged", \\\n'
		script += 'f(x) w l lw 2 ti "FreeRotationalModel"'
	elif val.base_name == 'Corr_stress' or val.base_name == 'Corr_stress_mod':
		script += 'set logscale xy \n\nset format x "10^{%L}" \nset format y "10^{%L}"\n\n'
		script += 'plot '
		script += 'data w l ti "Stress" \\\n'
	elif val.base_name == 'Corr_stress_semi':
		script += 'set logscale y \n\n#set format x "10^{%L}" \nset format y "10^{%L}"\n\n'
		script += 'a = 1\ntau =1000\n\ns = 100\ne = 1000\n\n'
		script += 'f(x) = a*exp(-1*x/tau) \n'
		script += 'fit [s:e] f(x) data usi 1:2 via a,tau\n\n'
		script += 'set label 1 sprintf("Fitted \\nA = %.1e \\n{/Symbol t} = %.1e \\nFitting Region: %d to %d", a, tau, s, e) at graph 0.35, 0.75\n\n'
		script += 'plot '
		script += 'data w l ti "Stress", \\\n'
		script += '[s:e] f(x) noti'
	elif val.base_name == 'Corr_stress_all':
		script += 'set logscale xy \n\nset format x "10^{%L}" \nset format y "10^{%L}"\n\n'
		script += 'plot data u 1:2 w l ti "G_t", \\\n'
		script += 'data u 1:3 w l ti "xy", \\\n'
		script += 'data u 1:4 w l ti "yz", \\\n'
		script += 'data u 1:5 w l ti "zx", \\\n'
		script += 'data u 1:6 w l ti "xx-yy", \\\n'
		script += 'data u 1:7 w l ti "yy-zz"'
	elif val.base_name == 'Sq':
		script += 'plot data u 1:2 w l ti "S(q)"'
	elif val.base_name == 'Guinier':
		script += 'rg=3\ni0=1\ns=0.\ne=1.0\n\n'
		script += 'f(x) = (-1*rg**2/3)*x + i0\n'
		script += 'fit [s:e] f(x) data u ($1**2):(log($2)) via rg, i0\n\n'
		script += 'set label 1 sprintf("Rg = %.2f \nI_0 = %.2f \nRegion: %.2f to %.2f", rg, i0, s, e) at graph 0.35, 0.75'
		script += 'plot [0:1] data u ($1**2):(log($2)) w l noti, \\\nf(x)'
	else:
		script += 'plot '
		for i in range(repeat):
			script += 'data ind ' + str(i) + ' w l lc ' + str(i) + 'noti, \\\n'

	return script











