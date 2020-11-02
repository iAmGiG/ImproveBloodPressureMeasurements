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
        super().__init__(face)
        self.sp = array('d')
        self.dp = array('d')
        self.avg_sp = array('d')
        self.avg_dp = array('d')

    def analyze_bp(self, t, greenIm):
        # P.analyze(self, t, greenIm)
        if not self._firstTime:
            self._firstTime = t
        if t < self._firstTime + conf.STARTUP_TIME:
            return
        for arr in (
                self.times, self.raw, self.corrected, self.bpm, self.avBpm):
            if len(arr) >= conf.MAX_SAMPLES:
                arr.pop(0)

        self.times.append(t)
        raw = self._getSignal(greenIm, self.face)
        self.raw.append(raw)

        if self.prevFace is not None:
            prev = self._getSignal(greenIm, self.prevFace)
            self.correction *= prev / raw
            self.prevFace = None
        self.corrected.append(raw * self.correction)

        fps = self._getFPS()
        nyquistFreq = 0.5 * fps
        self.filtered = self._filter(self.corrected, nyquistFreq)
        if not len(self.filtered):
            return

        self.freqs, self.spectrum = self._createSpectrum(
            self.filtered, nyquistFreq)
        bpm = self._findPeak(self.freqs, self.spectrum)
        if conf.MIN_BPM <= bpm <= conf.MAX_BPM:
            sp, dp = self._blood_preasure_calculator(bpm, 330, 73, 39)
            self.sp.append(sp)
            self.dp.append(dp)
            self.bpm.append(bpm)
            self._index += 1
            if fps:
                p = int(0.5 + conf.AV_BPM_PERIOD * fps)
                if len(self.bpm) == conf.MAX_SAMPLES and not self._index % p:
                    av = np.average(self.bpm[-p:])
                    self.avBpm.append(av)
                    self.avg_sp.append(sp)
                    self.avg_dp.append(dp)


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
