import AppKit

let commandKey: CGKeyCode = 55
let optionKey: CGKeyCode = 58
let rightArrowKey: CGKeyCode = 124
let leftArrowKey: CGKeyCode = 123
let isPreviousTab = CommandLine.arguments.contains("--previous")

func postKey(_ key: CGKeyCode, _ isDown: Bool) {
    let event = CGEvent(
        keyboardEventSource: nil,
        virtualKey: key,
        keyDown: isDown
    )
    event?.post(tap: .cghidEventTap)
}

postKey(commandKey, true)
postKey(optionKey, true)
let tabDirectionKey = isPreviousTab ? leftArrowKey : rightArrowKey
postKey(tabDirectionKey, true)
postKey(tabDirectionKey, false)
postKey(optionKey, false)
postKey(commandKey, false)
