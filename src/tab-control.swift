import AppKit

let rightArrowKey: CGKeyCode = 124
let leftArrowKey: CGKeyCode = 123
let commandKey: CGKeyCode = 55
let optionKey: CGKeyCode = 58
let isPreviousTab = CommandLine.arguments.contains("--previous")
let navigationModifiers: CGEventFlags = [.maskCommand, .maskAlternate]

func postKey(
    _ key: CGKeyCode,
    _ isDown: Bool,
    flags: CGEventFlags = []
) {
    guard let event = CGEvent(
        keyboardEventSource: nil,
        virtualKey: key,
        keyDown: isDown
    ) else {
        return
    }
    event.flags = flags
    event.post(tap: .cghidEventTap)
}

let tabDirectionKey = isPreviousTab ? leftArrowKey : rightArrowKey
postKey(commandKey, true)
postKey(optionKey, true)
postKey(tabDirectionKey, true, flags: navigationModifiers)
postKey(tabDirectionKey, false, flags: navigationModifiers)
postKey(optionKey, false)
postKey(commandKey, false)
