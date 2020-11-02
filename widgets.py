from heartwave.widgets import View, CurveWidget
from heartwave.plot import Plot


class View_us(View):
    def __init__(self, parent):
            View.__init__(self, parent)


class CurveWidget_us(CurveWidget):
    def __init__(self, parent=None):
        CurveWidget.__init__(self,parent)
        self.bp_plots = [Plot(title=t) for t in ('SP', 'DP')]
        for plot in self.bp_plots:
            self.addWidget(plot)

    def plot_bp(self, persons):
        CurveWidget.plot(self. persons)
        for plot in self.bp_plots:
            plot.clear()
        sp, dp = self.bp_plots
        for person in persons:
            sp.plot(person.sp)
        for person in persons:
            dp.plot(person.dp)