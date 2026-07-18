import AppKit

let playPauseKeyCode: Int32 = 16
let keyDownState: Int32 = 0xA00
let keyUpState: Int32 = 0xB00

func postMediaKey(_ state: Int32) {
    let data = (playPauseKeyCode << 16) | state
    let event = NSEvent.otherEvent(
        with: .systemDefined,
        location: .zero,
        modifierFlags: [],
        timestamp: 0,
        windowNumber: 0,
        context: nil,
        subtype: 8,
        data1: Int(data),
        data2: -1
    )
    event?.cgEvent?.post(tap: CGEventTapLocation.cghidEventTap)
}

postMediaKey(keyDownState)
postMediaKey(keyUpState)
