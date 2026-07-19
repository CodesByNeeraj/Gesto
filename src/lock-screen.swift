import AppKit

let lockScreenKey: CGKeyCode = 12
let lockScreenModifiers: CGEventFlags = [.maskControl, .maskCommand]

func postKey(_ key: CGKeyCode, _ isDown: Bool) {
    guard let event = CGEvent(
        keyboardEventSource: nil,
        virtualKey: key,
        keyDown: isDown
    ) else {
        return
    }
    event.flags = lockScreenModifiers
    event.post(tap: .cghidEventTap)
}

postKey(lockScreenKey, true)
postKey(lockScreenKey, false)
