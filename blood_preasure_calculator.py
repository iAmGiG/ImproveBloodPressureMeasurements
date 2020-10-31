def blood_preasure_calculator(avg_bpm, weight, height, age) 

kgs = weight*0.45359237 #lbs to kgs
cm = height/0.39370 #in to cm
q = 4.5 #constant

rob = 18.5
et = (364.5 - 1.23 * avg_bpm)
bsa = 0.007184 * (kgs**0.425) * (cm**0.725)
sv = (-6.6 + (0.25 * (et - 35)) - (0.62 * avg_bpm) + (40.4 * bsa) - (0.51 * age))
pp = sv / ((0.013 * kgs - 0.007 * age - 0.004 * avg_bpm) + 1.307)
mpp = Q * rob

sp = int(mpp + 3 / 2 * pp)
dp = int(mpp - pp / 3)

return sp, dp