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
step_rfc = []
step_rfc_time = []
harmonicK = 0.
harmonic_time = []
#
kg_repeat = 1
kg_time = []
#
laos = ''
laos_repeat = 1
laos_n = 0.
laos_amp = 1.
laos_freq = 0.1
laos_period = 0.01
laos_time = []
#
heat = ''
heat_repeat = 1
heat_temp = 1.
heat_time = []
#
final_time = []
#
equilib_repeat = 1
equilib_time = []
greenkubo = ''
greenkubo_repeat = 0
greenkubo_time = []

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
template = ''
present_udf = ''
read_udf = ''
f_eval_py = 'evaluate_polymer'

rfc = 0.
