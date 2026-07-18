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
        catalogModule = loadModule(
            "application-catalog.py", "applicationCatalog"
        )
        trainerModule = loadModule("custom-trainer.py", "customTrainer")
        trainingModule = loadModule("training-session.py", "trainingSession")
        loopModule = loadModule("detection-loop.py", "detectionLoop")
        controllerModule = loadModule(
            "ui/mapping-controller.py", "mappingController"
        )
        self.windowModule = loadModule("ui/main-window.py", "mainWindow")

        self.config = self.configLoader.loadConfig()
        self.cameraHandler = cameraModule.CameraHandler()
        self.gestureDetector = detectorModule.GestureDetector()
        self.actionExecutor = executorModule.ActionExecutor()
        self.applicationCatalog = catalogModule
        self.customTrainer = trainerModule
        self.trainingSession = trainingModule.TrainingSession(
            self.cameraHandler,
            self.gestureDetector.extractLandmarks,
            self.customTrainer.trainCustomGesture,
        )
        self.statusLock = threading.Lock()
        self.detectionStatus = "Ready to start detection"
        self.detectionLoop = loopModule.DetectionLoop(
            self.cameraHandler,
            self.gestureDetector,
            mapperModule.mapGestureToAction,
            self.actionExecutor.executeAction,
            self.config,
            onDetection=self.recordDetection,
            onActionExecuted=self.recordActionExecution,
            onObservation=self.recordObservation,
            onActionFailed=self.recordActionFailure,
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
            self.startCustomTraining,
            self.customTrainer.listCustomGestureLabels,
            self.applicationCatalog.listInstalledApplicationNames,
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

    def startCustomTraining(self, gestureLabel: str) -> Path:
        """Stop live detection and train one locally named custom gesture."""
        self.stopDetection()
        if self.detectionThread is not None:
            self.detectionThread.join(timeout=1)
        return self.trainingSession.train(gestureLabel)

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

    def recordObservation(self, observation: str) -> None:
        """Show the current camera/classifier state when no action is ready."""
        with self.statusLock:
            self.detectionStatus = observation

    def recordActionExecution(
        self, gestureLabel: str, action: dict[str, object]
    ) -> None:
        """Display the action that was actually executed for a short period."""
        actionName = str(action["action"]).replace("-", " ")
        with self.statusLock:
            self.detectionStatus = (
                f"Triggered {actionName} with {gestureLabel}"
            )

    def recordActionFailure(
        self,
        gestureLabel: str,
        action: dict[str, object],
        error: Exception,
    ) -> None:
        """Show an action error while keeping live detection available."""
        if action.get("action") == "open-app":
            applicationName = action.get("value")
            message = f"Couldn't open {applicationName}. Check the app name."
        else:
            message = f"Couldn't run action for {gestureLabel}: {error}"
        with self.statusLock:
            self.detectionStatus = message

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
