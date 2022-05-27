#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
import numpy as np
import sys
import os

from UDFManager import UDFManager

import polymer_setup.values as val
##########################################
# UDF の作成
##########################################
# UDFファイルを設定し、バッチ処理を作成
def rotate_pos():
	uobj, axis, outudf = select_udf()
	rotate_position(uobj, axis, outudf)
	return

##########################################
# 対象となる udf ファイルを選択
def select_udf():
	param = sys.argv
	if len(param) < 2:
		print("usage: python", param[0], "Honya_out.udf direction[x or y or z] Hetya_out.udf")
		print("Two parameter should be addressed !")
		exit(1)
	elif not os.access(param[1],os.R_OK):
		print(param[1], "not exists.")
		exit(1)
	#
	target = param[1]
	uobj = UDFManager(target)
	axis = param[2]
	outudf = param[3]
	return uobj, axis, outudf

# アトムのポジションを回転
def rotate_position(uobj, axis, outudf):
	#
	uobj.eraseRecord(0, uobj.totalRecord() - 2)
	#
	R = rotate(axis[0], np.pi/2.)
	uobj.jump(uobj.totalRecord() - 1)
	pos = uobj.get('Structure.Position.mol[].atom[]')
	for i, mol in enumerate(pos):
		for j, atom in enumerate(mol):
			tmp = list(np.array(R).dot(np.array(atom)))
			uobj.put(tmp, 'Structure.Position.mol[].atom[]', [i, j])
	#
	uobj.write(outudf)
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