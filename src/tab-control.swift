import AppKit

let controlKey: CGKeyCode = 59
let shiftKey: CGKeyCode = 56
let tabKey: CGKeyCode = 48
let isPreviousTab = CommandLine.arguments.contains("--previous")

func postKey(_ key: CGKeyCode, _ isDown: Bool) {
    let event = CGEvent(
        keyboardEventSource: nil,
        virtualKey: key,
        keyDown: isDown
    )
    event?.post(tap: .cghidEventTap)
}

postKey(controlKey, true)
if isPreviousTab {
    postKey(shiftKey, true)
}
postKey(tabKey, true)
postKey(tabKey, false)
if isPreviousTab {
    postKey(shiftKey, false)
}
postKey(controlKey, false)
