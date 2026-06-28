import AppKit
import CoreGraphics
import Foundation

func intRect(_ rect: NSRect) -> [String: Int] {
    return [
        "x": Int(rect.origin.x.rounded()),
        "y": Int(rect.origin.y.rounded()),
        "width": Int(rect.size.width.rounded()),
        "height": Int(rect.size.height.rounded())
    ]
}

let mainNumber = NSScreen.main?.deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as? NSNumber
var displays: [[String: Any]] = []

for screen in NSScreen.screens {
    let number = screen.deviceDescription[NSDeviceDescriptionKey("NSScreenNumber")] as? NSNumber
    let displayID = CGDirectDisplayID(number?.uint32Value ?? 0)
    let cgBounds = displayID == 0 ? NSRect.zero : CGDisplayBounds(displayID)
    let bounds = cgBounds == .zero ? screen.frame : NSRect(
        x: cgBounds.origin.x,
        y: cgBounds.origin.y,
        width: cgBounds.size.width,
        height: cgBounds.size.height
    )
    displays.append([
        "id": number?.intValue ?? displays.count + 1,
        "main": number == mainNumber,
        "x": Int(bounds.origin.x.rounded()),
        "y": Int(bounds.origin.y.rounded()),
        "width": Int(bounds.size.width.rounded()),
        "height": Int(bounds.size.height.rounded()),
        "appKitX": Int(screen.frame.origin.x.rounded()),
        "appKitY": Int(screen.frame.origin.y.rounded()),
        "appKitWidth": Int(screen.frame.size.width.rounded()),
        "appKitHeight": Int(screen.frame.size.height.rounded()),
        "usableX": Int(screen.visibleFrame.origin.x.rounded()),
        "usableY": Int(screen.visibleFrame.origin.y.rounded()),
        "usableWidth": Int(screen.visibleFrame.size.width.rounded()),
        "usableHeight": Int(screen.visibleFrame.size.height.rounded())
    ])
}

if displays.isEmpty {
    var count: UInt32 = 0
    let first = CGGetActiveDisplayList(0, nil, &count)
    if first != .success {
        print("{\"ok\":false,\"error\":\"CGGetActiveDisplayList failed: \(first.rawValue)\",\"displays\":[]}")
        exit(0)
    }

    var ids = Array(repeating: CGDirectDisplayID(0), count: Int(count))
    let second = CGGetActiveDisplayList(count, &ids, &count)
    if second != .success {
        print("{\"ok\":false,\"error\":\"CGGetActiveDisplayList failed: \(second.rawValue)\",\"displays\":[]}")
        exit(0)
    }

    let mainID = CGMainDisplayID()
    for id in ids {
        let bounds = CGDisplayBounds(id)
        displays.append([
            "id": Int(id),
            "main": id == mainID,
            "x": Int(bounds.origin.x),
            "y": Int(bounds.origin.y),
            "width": Int(bounds.size.width),
            "height": Int(bounds.size.height)
        ])
    }
}

let payload: [String: Any] = [
    "ok": true,
    "error": NSNull(),
    "displays": displays
]

let data = try! JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
print(String(data: data, encoding: .utf8)!)
