import sys
import asyncio
import functools
import datetime
from pathlib import Path

import PyQt5.Qt as qt

from widgets import View_us, CurveWidget_bp
from videostream import VideoStream
from facetracker import FaceTracker
from sceneanalyzer import SceneAnalyzer
import conf
import util


class Window(qt.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Our app')
        self.view = View_us(self)
        self.view.setMinimumSize(640, 480)
        self.setCentralWidget(self.view)
        self.curves = CurveWidget_bp()
        self.curves.show()
        self.pheight = 0.0
        self.pweight = 0.0
        self.age = 0

        def addAction(menu, name, shortcut, cb):
            action = qt.QAction(name, self)
            action.setShortcut(shortcut)
            action.triggered.connect(cb)
            menu.addAction(action)

        menu = self.menuBar()
        fileMenu = menu.addMenu('Source')
        camMenu = fileMenu.addMenu('Camera')
        addAction(fileMenu, 'File', 'Ctrl-F', self.onOpenFile)
        addAction(fileMenu, 'URL', 'Ctrl-U', self.onOpenURL)
        addAction(fileMenu, 'Exit', 'Esc', self.close)
        for i in range(10):
            addAction(camMenu, str(i), '', functools.partial(self.onCamera, i))
        addAction(menu, 'Snapshot', 'Space', self.onSnapshot)
        addAction(menu, 'Toggle curves', 'T', self.onToggleCurves)

        self.pipe = None
        self.video = None
        self.start()

    def onOpenFile(self):
        path, _filter = qt.QFileDialog.getOpenFileName(self)
        if path:
            self.stop()
            conf.CAM_ID = path
            self.start()

    def onOpenURL(self):
        url, ok = qt.QInputDialog.getText(None, 'Open URL', 'URL:')
        if ok:
            self.stop()
            conf.CAM_ID = url
            self.start()

    def onCamera(self, camId):
        self.stop()
        conf.CAM_ID = camId
        self.start()

    def onSnapshot(self):
        timeStamp = datetime.datetime.now().strftime('%Y%m%d%_H%M%S_%f')
        name = f'heartwave_{timeStamp}_im.png'
        self.view.image.save(str(Path.home() / name))
        if self.curves.isVisible():
            name = f'heartwave_{timeStamp}_curve.png'
            self.curves.grab().save(str(Path.home() / name))

    def onToggleCurves(self):
        self.curves.setVisible(not self.curves.isVisible())

    def closeEvent(self, ev):
        self.stop()
        self.curves.close()

    def start(self):
        self.pipe = asyncio.ensure_future(self.pipeline())

    def stop(self):
        self.video.stop()

    def set_boiler_plate(self, weight, height, age):
        self.pheight = height
        self.pweight = weight
        self.age = age

    async def pipeline(self):
        self.video = VideoStream(conf.CAM_ID)
        scene = self.video | FaceTracker | SceneAnalyzer
        lastScene = scene.aiter(skip_to_last=True)
        _, person = lastScene
        person.set_boiler_plate(self.pweight, self.pheight, self.age)
        async for frame, persons in lastScene:
            self.view.draw(frame.image, persons)
            if self.curves.isVisible():
                self.curves.plot(persons)


def pulse():
    if len(sys.argv) > 1:
        conf.CAM_ID = sys.argv[1]
    qApp = qt.QApplication(sys.argv)  # noqa
    weight, ok = qt.QInputDialog.getDouble(None, "Insert Weight", """weight in pounds""")
    height, ok = qt.QInputDialog.getDouble(None, "Insert Height", """height """)
    age, ok = qt.QInputDialog.getInt(None, "insert your age", """age testing:""")
    if not ok:
        sys.exit(qApp.exec_())
    win = Window()
    win.set_boiler_plate(weight=weight, height=height, age=age)
    win.show()
    util.run()
