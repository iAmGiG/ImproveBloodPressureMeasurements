from array import array

import numpy as np
from heartwave.person import Person as P
#import heartwave.conf as conf
import conf

class Person_us (P):
    """
    State and heart rate calculations for one person.
    """
    def __init__(self, face):
        P.__init__(self, face)
        self.sp = array('d')
        self.dp = array('d')

    def analyze_us(self, t, greenIm):
        P.analyze(self, t, greenIm)
        fps = self._getFPS()
        if fps:
            p = int(0.5 + conf.AV_BPM_PERIOD * fps)
            if len(self.bpm) == conf.MAX_SAMPLES and not self._index % p:
                av = np.average(self.bpm[-p:])
                sp, dp = self._blood_preasure_calculator(av, 330, 73, 39)
                self.sp.append(sp)
                self.dp.append(dp)


    def _blood_preasure_calculator(self, avg_bpm, weight, height, age):

        kgs = weight * 0.45359237  # lbs to kgs
        cm = height / 0.39370  # in to cm
        q = 4.5  # constant

        rob = 18.5
        et = (364.5 - 1.23 * avg_bpm)
        bsa = 0.007184 * (kgs ** 0.425) * (cm ** 0.725)
        sv = (-6.6 + (0.25 * (et - 35)) - (0.62 * avg_bpm) + (40.4 * bsa) - (0.51 * age))
        pp = sv / ((0.013 * kgs - 0.007 * age - 0.004 * avg_bpm) + 1.307)
        mpp = q * rob

        sp = int(mpp + 3 / 2 * pp)
        dp = int(mpp - pp / 3)

        return sp, dp
