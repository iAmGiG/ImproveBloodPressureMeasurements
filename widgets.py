from heartwave.widgets import View, CurveWidget
from heartwave.plot import Plot
import heartwave.util as util
import PyQt5.Qt as qt


class View_us(View):
    def __init__(self, parent):
            super().__init__(parent)

    def draw(self, im, persons):
        qim = util.qImage(im)
        with qt.QPainter(qim) as p:
            for person in persons:
                x, y, w, h = person.face
                p.setPen(qt.QColor(255, 255, 255, 64))
                p.drawRect(x, y, w, h / 4)
                p.drawRect(x, y + h / 2, w, h / 4)
                font = p.font()
                font.setPixelSize(28)
                p.setFont(font)
                p.setPen(qt.QColor(255, 255, 255))
                bpm = person.avBpm[-1] if len(person.avBpm) else 0
                p.drawText(
                    x, y, w, h, qt.Qt.AlignHCenter, '♡' + str(int(bpm)))
        self.image = qim
        self.setMinimumSize(qim.size())
        self.update()


class CurveWidget_bp(CurveWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(640)
        self.image = None
        self.bp_plots = [Plot(title=t) for t in ('SP', 'DP')]
        for plot in self.bp_plots:
            self.addWidget(plot)

    def plot(self, persons):
        super().plot(persons)
        for plot in self.bp_plots:
            plot.clear()
        sp, dp = self.bp_plots
        for person in persons:
            sp.plot(person.sp)
            sp.plot(person.avg_sp, pen=qt.Qt.red)
        for person in persons:
            dp.plot(person.dp)
            dp.plot(person.avg_dp, pen=qt.Qt.red)