"""Gesto's desktop settings window and mapping controls."""

from collections.abc import Callable
import queue
import threading
from typing import Any

import customtkinter as ctk


CUSTOM_GESTURE_PLACEHOLDER = "train-a-custom-gesture-first"
SUPPORTED_ACTIONS = (
    "take-screenshot",
    "open-app",
    "media-play-pause",
    "switch-tab-next",
    "switch-tab-previous",
    "lock-screen",
)
GESTURES_KEY = "gestures"
OPEN_APPLICATION_ACTION = "open-app"


class MainWindow(ctk.CTk):
    """Provide a clean desktop interface for Gesto settings and controls."""

    def __init__(
        self,
        controller: Any,
        startDetection: Callable[[], bool],
        stopDetection: Callable[[], None],
        getDetectionStatus: Callable[[], str],
        startCustomTraining: Callable[[str], Any],
        getCustomGestureLabels: Callable[[], list[str]],
    ) -> None:
        super().__init__()
        self.controller = controller
        self.startDetection = startDetection
        self.stopDetection = stopDetection
        self.getDetectionStatus = getDetectionStatus
        self.startCustomTraining = startCustomTraining
        self.getCustomGestureLabels = getCustomGestureLabels
        self.trainingEvents: queue.Queue[tuple[str, Any]] = queue.Queue()
        self.isDetecting = False

        self.title("Gesto")
        self.geometry("860x560")
        self.minsize(760, 500)
        self.protocol("WM_DELETE_WINDOW", self.closeWindow)
        self.createLayout()
        self.refreshMappings()
        self.after(250, self.refreshDetectionStatus)
        self.after(250, self.refreshTrainingEvents)

    def createLayout(self) -> None:
        """Create the application header, mapping form, and status controls."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        headerFrame = ctk.CTkFrame(self, corner_radius=0)
        headerFrame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        headerFrame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            headerFrame,
            text="Gesto",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=28, pady=(20, 0))
        ctk.CTkLabel(
            headerFrame,
            text="Control your Mac with gestures.",
            text_color="gray70",
        ).grid(row=1, column=0, sticky="w", padx=28, pady=(2, 20))

        contentFrame = ctk.CTkFrame(self, fg_color="transparent")
        contentFrame.grid(row=1, column=0, sticky="nsew", padx=24, pady=24)
        contentFrame.grid_columnconfigure((0, 1), weight=1)
        contentFrame.grid_rowconfigure(0, weight=1)

        self.createMappingForm(contentFrame)
        self.createMappingsList(contentFrame)

        footerFrame = ctk.CTkFrame(self, corner_radius=12)
        footerFrame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        footerFrame.grid_columnconfigure(0, weight=1)
        self.statusLabel = ctk.CTkLabel(
            footerFrame,
            text="Detection is stopped",
            text_color="gray70",
        )
        self.statusLabel.grid(row=0, column=0, sticky="w", padx=18, pady=14)
        self.toggleButton = ctk.CTkButton(
            footerFrame,
            text="Start Detection",
            command=self.toggleDetection,
        )
        self.toggleButton.grid(row=0, column=1, padx=14, pady=12)

    def createMappingForm(self, parent: ctk.CTkFrame) -> None:
        """Create controls for adding or updating a mapping."""
        formFrame = ctk.CTkFrame(parent, corner_radius=12)
        formFrame.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        formFrame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            formFrame,
            text="Add a mapping",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))

        self.gestureMenu = ctk.CTkOptionMenu(
            formFrame,
            values=self.getGestureMenuValues(),
        )
        self.gestureMenu.grid(row=1, column=0, sticky="ew", padx=18, pady=8)
        self.actionMenu = ctk.CTkOptionMenu(
            formFrame,
            values=list(SUPPORTED_ACTIONS),
            command=self.updateActionValueField,
        )
        self.actionMenu.grid(row=2, column=0, sticky="ew", padx=18, pady=8)
        self.valueEntry = ctk.CTkEntry(
            formFrame,
            placeholder_text="Application name (only for open-app)",
        )
        self.valueEntry.grid(row=3, column=0, sticky="ew", padx=18, pady=8)
        self.updateActionValueField(self.actionMenu.get())
        ctk.CTkButton(
            formFrame,
            text="Save Mapping",
            command=self.saveMapping,
        ).grid(row=4, column=0, sticky="ew", padx=18, pady=(8, 18))
        ctk.CTkButton(
            formFrame,
            text="Train a custom gesture",
            fg_color="transparent",
            border_width=1,
            command=self.openTrainingDialog,
        ).grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 18))

    def createMappingsList(self, parent: ctk.CTkFrame) -> None:
        """Create the scrollable area that shows saved mappings."""
        listFrame = ctk.CTkFrame(parent, corner_radius=12)
        listFrame.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        listFrame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            listFrame,
            text="Your mappings",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 8))
        self.mappingsFrame = ctk.CTkScrollableFrame(
            listFrame,
            fg_color="transparent",
        )
        self.mappingsFrame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=8,
            pady=(0, 12),
        )
        listFrame.grid_rowconfigure(1, weight=1)

    def saveMapping(self) -> None:
        """Save the current form values and refresh the mappings list."""
        actionValue = self.valueEntry.get().strip() or None
        self.controller.saveMapping(
            self.gestureMenu.get(),
            self.actionMenu.get(),
            actionValue,
        )
        self.valueEntry.delete(0, "end")
        self.refreshMappings()

    def updateActionValueField(self, actionName: str) -> None:
        """Only accept an application name when opening a named app."""
        isApplicationAction = actionName == OPEN_APPLICATION_ACTION
        entryState = "normal" if isApplicationAction else "disabled"
        self.valueEntry.configure(state=entryState)
        if not isApplicationAction:
            self.valueEntry.delete(0, "end")

    def getGestureMenuValues(self) -> list[str]:
        """Show trained gestures, or a non-mappable training prompt."""
        return self.getCustomGestureLabels() or [CUSTOM_GESTURE_PLACEHOLDER]

    def openTrainingDialog(self) -> None:
        """Open a small local-only naming dialog for a training session."""
        dialog = ctk.CTkInputDialog(
            text="Name this gesture (for example: my-open-palm)",
            title="Train a custom gesture",
        )
        gestureLabel = dialog.get_input()
        if not gestureLabel:
            return

        self.statusLabel.configure(
            text="Capturing 40 samples…",
            text_color="#60a5fa",
        )
        threading.Thread(
            target=self.runCustomTraining,
            args=(gestureLabel,),
            daemon=True,
        ).start()

    def runCustomTraining(self, gestureLabel: str) -> None:
        """Run camera training outside the UI event loop."""
        try:
            self.startCustomTraining(gestureLabel)
            self.trainingEvents.put(("complete", gestureLabel))
        except Exception as error:
            self.trainingEvents.put(("error", str(error)))

    def refreshTrainingEvents(self) -> None:
        """Apply completed background-training results in the UI thread."""
        try:
            eventName, detail = self.trainingEvents.get_nowait()
        except queue.Empty:
            self.after(250, self.refreshTrainingEvents)
            return

        if eventName == "complete":
            gestureLabels = self.getGestureMenuValues()
            self.gestureMenu.configure(values=gestureLabels)
            self.gestureMenu.set(detail)
            self.statusLabel.configure(
                text=(
                    f"Trained {detail}. Choose an action and save its mapping."
                ),
                text_color="#4ade80",
            )
        else:
            self.statusLabel.configure(
                text=f"Training error: {detail}",
                text_color="#f87171",
            )

        self.after(250, self.refreshTrainingEvents)

    def refreshMappings(self) -> None:
        """Render the latest local gesture-to-action mappings."""
        for child in self.mappingsFrame.winfo_children():
            child.destroy()

        mappings = self.controller.config[GESTURES_KEY]
        if not mappings:
            ctk.CTkLabel(
                self.mappingsFrame,
                text="No mappings yet. Add your first gesture on the left.",
                text_color="gray70",
                wraplength=280,
            ).pack(fill="x", padx=10, pady=12)
            return

        for mapping in mappings:
            self.createMappingRow(mapping)

    def createMappingRow(self, mapping: dict[str, Any]) -> None:
        """Render a saved mapping with a deletion control."""
        rowFrame = ctk.CTkFrame(self.mappingsFrame)
        rowFrame.pack(fill="x", padx=6, pady=6)
        rowFrame.grid_columnconfigure(0, weight=1)
        actionText = mapping["action"]
        if mapping["value"]:
            actionText = f"{actionText}: {mapping['value']}"
        ctk.CTkLabel(
            rowFrame,
            text=f"{mapping['id']}  →  {actionText}",
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=12, pady=12)
        ctk.CTkButton(
            rowFrame,
            text="Remove",
            width=72,
            fg_color="transparent",
            border_width=1,
            command=lambda label=mapping["id"]: self.removeMapping(label),
        ).grid(row=0, column=1, padx=8, pady=8)

    def removeMapping(self, gestureLabel: str) -> None:
        """Delete a mapping selected from the rendered list."""
        self.controller.removeMapping(gestureLabel)
        self.refreshMappings()

    def toggleDetection(self) -> None:
        """Start or stop the background detection loop."""
        if self.isDetecting:
            self.stopDetection()
            self.isDetecting = False
            self.statusLabel.configure(
                text="Detection is stopped",
                text_color="gray70",
            )
            self.toggleButton.configure(text="Start Detection")
            return

        if self.startDetection():
            self.isDetecting = True
            self.statusLabel.configure(
                text="Detection is running",
                text_color="#4ade80",
            )
            self.toggleButton.configure(text="Stop Detection")
            return

        self.statusLabel.configure(
            text="Camera unavailable. Check macOS camera permissions.",
            text_color="#f87171",
        )

    def refreshDetectionStatus(self) -> None:
        """Show the latest background detector status in the UI thread."""
        if self.isDetecting:
            self.statusLabel.configure(
                text=self.getDetectionStatus(),
                text_color="#4ade80",
            )

        self.after(250, self.refreshDetectionStatus)

    def closeWindow(self) -> None:
        """Stop detection before closing the settings window."""
        if self.isDetecting:
            self.stopDetection()

        self.destroy()
