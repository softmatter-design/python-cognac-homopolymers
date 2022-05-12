# 'polymer_condition.udf' からの入力値
ver_cognac = ''
blank_udf = ''
base_udf = ''
core = ''
#
model = ''
na_segments = 0
ma_polymers = 0
nb_segments = 0
mb_polymers = 0
epsilon = 0.
#
initialize = ''
spo_r = []
spo_time = []
spo_eval = 1
harmonicK = 0.
harmonic_time = []
harmonic_eval = 1
#
kg_repeat = 1
kg_time = []
kg_eval = 1
#
laos = ''
laos_repeat = 1
laos_n = 0.
laos_amp = 1.
laos_freq = 0.1
laos_period = 0.01
laos_time = []
laos_eval = 0
#
heat = ''
heat_repeat = 1
heat_temp = 1.
heat_time = []
heat_eval = 1
#
final_time = []
final_eval = 1
#
equilib_repeat = 1
equilib_time = []
equilib_eval = 1
greenkubo = ''
greenkubo_repeat = 0
greenkubo_time = []
greenkubo_eval = 1

#
target_name = ''
target_udf = ''
uobj = ''

# Cognac用の名称設定
mol_name = []
atom_name = []
bond_name = []
angle_name = []
site_name = []
pair_name = []
site_pair_name = []
density = 0.85
# Set [R0, K]
harmonic = [0.97, 1000]
# [Potential_Type, theta0, K]		
angle = ['Theta2', 74, 10.0]
# [Cutoff, Scale_1_4_Pair, sigma, epsilon, range]
lj_cond = [2**(1/6), 1.0, 1.0, 1.0, 1.0]

batch = ''
title = ''
file_name = ''
f_eval = 0
f_eval_py = 'evaluate_polymer'

template = ''
present_udf = ''
out_udf = ''
read_udf = ''

rfc = 0.

temp = 1.
