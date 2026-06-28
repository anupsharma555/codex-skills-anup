import CoreGraphics
import Foundation

let payload: [String: Any] = [
    "ok": true,
    "screenRecording": CGPreflightScreenCaptureAccess()
]

let data = try! JSONSerialization.data(withJSONObject: payload, options: [.sortedKeys])
print(String(data: data, encoding: .utf8)!)
