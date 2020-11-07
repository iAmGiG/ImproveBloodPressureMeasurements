import PyQt5.Qt as qt
import asyncio
import conf as conf
import datetime
from facetracker import FaceTracker
import functools
from pathlib import Path
from sceneanalyzer import SceneAnalyzer
import sys
import util as util
from videostream import VideoStream
from widgets import View, CurveWidget


class Window(qt.QMainWindow):

    def __init__(self):
        qt.QMainWindow.__init__(self)
        self.setWindowTitle('HeartWave')
        self.view = View(self)
        self.view.setMinimumSize(640, 480)
        self.setCentralWidget(self.view)
        self.curves = CurveWidget()
        self.curves.show()
        self.pheight, ok = qt.QInputDialog.getDouble(self.view, "Insert Weight", """weight in pounds""")
        self.pweight, ok = qt.QInputDialog.getDouble(self.view, "Insert Height", """height """)
        self.age, ok = qt.QInputDialog.getInt(self.view, "insert your age", """age testing:""")

        if not ok:
            sys.exit(qt.qApp.exec_())

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

    async def pipeline(self):
        self.video = VideoStream(conf.CAM_ID)
        scene = self.video | FaceTracker | SceneAnalyzer
        lastScene = scene.aiter(skip_to_last=True)
        async for frame, persons in lastScene:
            persons.setBoilerPlate(self.pweight, self.pweight, self.age)
            self.view.draw(frame.image, persons)
            if self.curves.isVisible():
                self.curves.plot(persons)


def pulse():
    if len(sys.argv) > 1:
        conf.CAM_ID = sys.argv[1]
    qApp = qt.QApplication(sys.argv)  # noqa
    win = Window()
    win.show()
    util.run()
