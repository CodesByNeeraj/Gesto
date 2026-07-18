"""Launch the Gesto desktop application."""

import importlib.util
import threading
from pathlib import Path
from types import ModuleType


SOURCE_DIRECTORY = Path(__file__).parent


class GestoApplication:
    """Compose Gesto's local services and run the settings window."""

    def __init__(self) -> None:
        self.configLoader = loadModule("config-loader.py", "configLoader")
        cameraModule = loadModule("camera-handler.py", "cameraHandler")
        detectorModule = loadModule("gesture-detector.py", "gestureDetector")
        mapperModule = loadModule("action-mapper.py", "actionMapper")
        executorModule = loadModule("action-executor.py", "actionExecutor")
        loopModule = loadModule("detection-loop.py", "detectionLoop")
        controllerModule = loadModule(
            "ui/mapping-controller.py", "mappingController"
        )
        self.windowModule = loadModule("ui/main-window.py", "mainWindow")

        self.config = self.configLoader.loadConfig()
        self.cameraHandler = cameraModule.CameraHandler()
        self.gestureDetector = detectorModule.GestureDetector()
        self.actionExecutor = executorModule.ActionExecutor()
        self.statusLock = threading.Lock()
        self.detectionStatus = "Ready to start detection"
        self.detectionLoop = loopModule.DetectionLoop(
            self.cameraHandler,
            self.gestureDetector,
            mapperModule.mapGestureToAction,
            self.actionExecutor.executeAction,
            self.config,
            onDetection=self.recordDetection,
        )
        self.mappingController = controllerModule.MainWindowController(
            self.config,
            self.configLoader.upsertGestureMapping,
            self.configLoader.deleteGestureMapping,
        )
        self.stopEvent = threading.Event()
        self.detectionThread: threading.Thread | None = None

    def run(self) -> None:
        """Open the settings window and begin handling user interactions."""
        window = self.windowModule.MainWindow(
            self.mappingController,
            self.startDetection,
            self.stopDetection,
            self.getDetectionStatus,
        )
        window.mainloop()

    def startDetection(self) -> bool:
        """Open the camera and start the background detection loop."""
        if (
            self.detectionThread is not None
            and self.detectionThread.is_alive()
        ):
            return True

        if not self.detectionLoop.startDetection():
            return False

        self.stopEvent.clear()
        with self.statusLock:
            self.detectionStatus = "Waiting for a recognized gesture"
        self.detectionThread = threading.Thread(
            target=self.runDetectionLoop,
            daemon=True,
        )
        self.detectionThread.start()
        return True

    def stopDetection(self) -> None:
        """Stop detection and release the camera."""
        self.stopEvent.set()
        self.detectionLoop.stopDetection()

    def runDetectionLoop(self) -> None:
        """Process camera frames until the user stops detection."""
        try:
            while not self.stopEvent.is_set():
                self.detectionLoop.processNextFrame()
        except Exception as error:
            with self.statusLock:
                self.detectionStatus = f"Detection error: {error}"
            self.stopEvent.set()
            self.detectionLoop.stopDetection()

    def recordDetection(
        self, gestureLabel: str, confidenceScore: float
    ) -> None:
        """Store the latest gesture for the settings-window status area."""
        with self.statusLock:
            self.detectionStatus = (
                f"Detected {gestureLabel} at {confidenceScore:.0%} confidence"
            )

    def getDetectionStatus(self) -> str:
        """Return a thread-safe snapshot of the latest detector status."""
        with self.statusLock:
            return self.detectionStatus


def loadModule(modulePath: str, moduleName: str) -> ModuleType:
    """Load a kebab-case Gesto module from the local source tree."""
    filePath = SOURCE_DIRECTORY / modulePath
    moduleSpec = importlib.util.spec_from_file_location(moduleName, filePath)
    if moduleSpec is None or moduleSpec.loader is None:
        raise ImportError(f"Unable to load Gesto module: {modulePath}")

    module = importlib.util.module_from_spec(moduleSpec)
    moduleSpec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    GestoApplication().run()
