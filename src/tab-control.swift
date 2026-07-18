import AppKit

let rightArrowKey: CGKeyCode = 124
let leftArrowKey: CGKeyCode = 123
let isPreviousTab = CommandLine.arguments.contains("--previous")
let navigationModifiers: CGEventFlags = [.maskCommand, .maskAlternate]

func postKey(_ key: CGKeyCode, _ isDown: Bool) {
    guard let event = CGEvent(
        keyboardEventSource: nil,
        virtualKey: key,
        keyDown: isDown
    ) else {
        return
    }
    event.flags = navigationModifiers
    event.post(tap: .cghidEventTap)
}

let tabDirectionKey = isPreviousTab ? leftArrowKey : rightArrowKey
postKey(tabDirectionKey, true)
postKey(tabDirectionKey, false)
