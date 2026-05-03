// Remove image background using macOS Vision framework's subject-lift ML
// (same model as Preview's "Remove Background" / Photos' subject lift).
// Requires macOS 14+ (Sonoma).
//
// Usage: swift removebg.swift input.png output.png
import Foundation
import Vision
import CoreImage
import AppKit

guard CommandLine.arguments.count == 3 else {
    FileHandle.standardError.write("Usage: removebg.swift input.png output.png\n".data(using: .utf8)!)
    exit(1)
}

let inputPath = CommandLine.arguments[1]
let outputPath = CommandLine.arguments[2]

guard let inputImage = CIImage(contentsOf: URL(fileURLWithPath: inputPath)) else {
    FileHandle.standardError.write("Could not load input\n".data(using: .utf8)!)
    exit(2)
}

let request = VNGenerateForegroundInstanceMaskRequest()
let handler = VNImageRequestHandler(ciImage: inputImage)

do {
    try handler.perform([request])
} catch {
    FileHandle.standardError.write("Vision request failed: \(error)\n".data(using: .utf8)!)
    exit(3)
}

guard let result = request.results?.first else {
    FileHandle.standardError.write("No subject detected\n".data(using: .utf8)!)
    exit(4)
}

do {
    let masked = try result.generateMaskedImage(
        ofInstances: result.allInstances,
        from: handler,
        croppedToInstancesExtent: false
    )
    let ciOut = CIImage(cvPixelBuffer: masked)
    let context = CIContext()
    guard let cgOut = context.createCGImage(ciOut, from: ciOut.extent) else {
        FileHandle.standardError.write("CGImage conversion failed\n".data(using: .utf8)!)
        exit(5)
    }
    let bitmap = NSBitmapImageRep(cgImage: cgOut)
    guard let data = bitmap.representation(using: .png, properties: [:]) else {
        FileHandle.standardError.write("PNG encode failed\n".data(using: .utf8)!)
        exit(6)
    }
    try data.write(to: URL(fileURLWithPath: outputPath))
    let w = Int(ciOut.extent.width), h = Int(ciOut.extent.height)
    print("OK: \(w)x\(h) saved to \(outputPath)")
} catch {
    FileHandle.standardError.write("Mask generation failed: \(error)\n".data(using: .utf8)!)
    exit(7)
}
