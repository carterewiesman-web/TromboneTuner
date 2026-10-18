import Foundation
import AVFoundation
import Accelerate

/// Real-time monophonic pitch detection using a windowed FFT with parabolic interpolation.
final class PitchDetector: NSObject {

    // MARK: - Audio

    private let engine = AVAudioEngine()
    private let bufferSize: UInt32 = 8192
    private var sampleRate: Double = 44100

    // MARK: - FFT buffers (reused to avoid allocations)

    private var window: [Float] = []
    private var realIn: [Float] = []
    private var imagIn: [Float] = []
    private var realOut: [Float] = []
    private var imagOut: [Float] = []

    // MARK: - Configuration

    /// Tunable frequency window (trombone ~ E2 to Bb5, with headroom).
    let minFrequency: Double = 50.0
    let maxFrequency: Double = 1300.0

    /// Cents tolerance considered "in tune".
    let inTuneCents: Double = 12.0

    var onPitch: ((_ frequency: Double, _ note: Note, _ cents: Double) -> Void)?

    private var isRunning = false

    override init() {
        super.init()
        resetBuffers()
    }

    deinit {
        stop()
    }

    // MARK: - Lifecycle

    func start() throws {
        guard !isRunning else { return }
        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)
        sampleRate = format.sampleRate

        inputNode.installTap(onBus: 0, bufferSize: bufferSize, format: format) { [weak self] buffer, _ in
            self?.process(buffer: buffer, sampleRate: format.sampleRate)
        }

        try engine.start()
        isRunning = true
    }

    func stop() {
        guard isRunning else { return }
        engine.inputNode.removeTap(onBus: 0)
        engine.stop()
        isRunning = false
    }

    // MARK: - Processing

    private func process(buffer: AVAudioPCMBuffer, sampleRate: Double) {
        guard let channelData = buffer.floatChannelData?.pointee else { return }
        let frameCount = Int(buffer.frameLength)
        guard frameCount > 0 else { return }

        // Copy mono samples into the windowed input buffer.
        let count = min(frameCount, realIn.count)
        for i in 0..<count {
            realIn[i] = channelData[i] * window[i]
        }
        for i in count..<realIn.count {
            realIn[i] = 0
        }

        // Forward FFT.
        guard let fftSetup = fftSetup else { return }
        var input = vDSP_DFT_SplitComplex(realp: &realIn, imagp: &imagIn)
        var output = vDSP_DFT_SplitComplex(realp: &realOut, imagp: &imagOut)
        vDSP_DFT_zop(fftSetup, &input, &output)

        let nyquist = sampleRate / 2.0
        let binWidth = nyquist / Double(realOut.count / 2)

        // Find peak magnitude in the target frequency range.
        var bestBin = -1
        var bestMag: Float = 0
        let minBin = max(1, Int(minFrequency / binWidth))
        let maxBin = min(realOut.count / 2 - 2, Int(maxFrequency / binWidth))

        for bin in minBin...maxBin {
            let r = realOut[bin]
            let i = imagOut[bin]
            let mag = sqrtf(r * r + i * i)
            if mag > bestMag {
                bestMag = mag
                bestBin = bin
            }
        }

        guard bestBin > 0, bestMag > 0.0001 else { return }

        // Parabolic interpolation for sub-bin accuracy.
        let y0 = realOut[bestBin - 1] * realOut[bestBin - 1] + imagOut[bestBin - 1] * imagOut[bestBin - 1]
        let y1 = realOut[bestBin] * realOut[bestBin] + imagOut[bestBin] * imagOut[bestBin]
        let y2 = realOut[bestBin + 1] * realOut[bestBin + 1] + imagOut[bestBin + 1] * imagOut[bestBin + 1]

        var fraction = 0.0
        let denom = (y0 - 2 * y1 + y2)
        if denom != 0 {
            fraction = 0.5 * Double(y0 - y2) / Double(denom)
        }
        // Clamp interpolation to reasonable range.
        let clampedFraction = max(-1.0, min(1.0, fraction))

        let frequency = Double(bestBin) * binWidth + clampedFraction * binWidth

        let result = Note.nearest(to: frequency)

        DispatchQueue.main.async { [weak self] in
            self?.onPitch?(frequency, result.note, result.cents)
        }
    }

    // MARK: - Setup

    private func resetBuffers() {
        let n = Int(bufferSize)
        window = [Float](repeating: 0, count: n)
        realIn = [Float](repeating: 0, count: n)
        imagIn = [Float](repeating: 0, count: n)
        realOut = [Float](repeating: 0, count: n)
        imagOut = [Float](repeating: 0, count: n)

        // Hann window.
        for i in 0..<n {
            window[i] = 0.5 * (1.0 - cos(2.0 * .pi * Float(i) / Float(n - 1)))
        }
    }

    /// Lazily created vDSP FFT setup.
    private lazy var fftSetup: vDSP_DFT_Setup? = {
        vDSP_DFT_zop_CreateSetup(nil, vDSP_Length(bufferSize), vDSP_DFT_Direction.FORWARD)
    }()
}
