import Foundation
import AVFoundation
import Accelerate

/// Real-time monophonic pitch detection using a windowed FFT with parabolic interpolation.
final class PitchDetector: NSObject {

    // MARK: - Audio

    private let engine = AVAudioEngine()
    private let bufferSize: UInt32 = 8192
    private var sampleRate: Double = 44100

    // MARK: - FFT state

    private var fftSetup: FFTSetup?
    private var log2n: vDSP_Length = 0
    private var window: [Float] = []
    private var realp: [Float] = []
    private var imagp: [Float] = []
    private var magnitudes: [Float] = []

    // MARK: - Configuration

    let minFrequency: Double = 50.0
    let maxFrequency: Double = 1300.0
    let inTuneCents: Double = 12.0

    var onPitch: ((_ frequency: Double, _ note: Note, _ cents: Double) -> Void)?

    private var isRunning = false

    override init() {
        super.init()
        setupFFT()
    }

    deinit {
        stop()
        if let setup = fftSetup {
            vDSP_destroy_fftsetup(setup)
        }
    }

    private func setupFFT() {
        let n = Int(bufferSize)
        log2n = vDSP_Length(log2(Float(n)))
        fftSetup = vDSP_create_fftsetup(log2n, FFTRadix(kFFTRadix2))

        window = [Float](repeating: 0, count: n)
        for i in 0..<n {
            window[i] = 0.5 * (1.0 - cos(2.0 * .pi * Float(i) / Float(n - 1)))
        }

        let half = n / 2
        realp = [Float](repeating: 0, count: half)
        imagp = [Float](repeating: 0, count: half)
        magnitudes = [Float](repeating: 0, count: half)
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
        guard frameCount > 0, let setup = fftSetup else { return }

        let n = Int(bufferSize)
        let half = n / 2

        // Window the input and pack into split-complex (real, imag=0) for real FFT.
        var windowed = [Float](repeating: 0, count: n)
        let copyCount = min(frameCount, n)
        for i in 0..<copyCount {
            windowed[i] = channelData[i] * window[i]
        }

        // vDSP_fft_zrip expects split complex: even samples -> realp, odd -> imagp (packed format)
        windowed.withUnsafeBufferPointer { ptr in
            let buf = UnsafeRawBufferPointer(ptr)
            realp.withUnsafeMutableBufferPointer { rBuf in
                imagp.withUnsafeMutableBufferPointer { iBuf in
                    var split = DSPSplitComplex(realp: rBuf.baseAddress!, imagp: iBuf.baseAddress!)
                    // Copy packed: real[i] = windowed[2i], imag[i] = windowed[2i+1] for real-input FFT
                    for i in 0..<half {
                        rBuf.baseAddress![i] = windowed[2 * i]
                        iBuf.baseAddress![i] = windowed[2 * i + 1]
                    }
                    vDSP_fft_zrip(setup, &split, 1, log2n, FFTDirection(FFT_FORWARD))
                }
            }
        }

        // Compute magnitudes for bins 0..half-1
        var split = DSPSplitComplex(realp: &realp, imagp: &imagp)
        vDSP_zvmags(&split, 1, &magnitudes, 1, vDSP_Length(half))

        // binWidth = sampleRate / n (for real FFT, each bin spans sampleRate/n)
        let binWidth = sampleRate / Double(n)

        let minBin = max(1, Int(minFrequency / binWidth))
        let maxBin = min(half - 2, Int(maxFrequency / binWidth))
        guard minBin < maxBin else { return }

        var bestBin = minBin
        var bestMag = magnitudes[minBin]
        for bin in (minBin + 1)...maxBin {
            if magnitudes[bin] > bestMag {
                bestMag = magnitudes[bin]
                bestBin = bin
            }
        }

        guard bestMag > 0.0001 else { return }

        // Parabolic interpolation using magnitudes (energy).
        let y0 = magnitudes[bestBin - 1]
        let y1 = magnitudes[bestBin]
        let y2 = magnitudes[bestBin + 1]
        let denom = y0 - 2 * y1 + y2
        var fraction: Float = 0
        if denom != 0 {
            fraction = 0.5 * (y0 - y2) / denom
        }
        fraction = max(-1.0, min(1.0, fraction))

        let frequency = Double(bestBin) * binWidth + Double(fraction) * binWidth

        let result = Note.nearest(to: frequency)

        DispatchQueue.main.async { [weak self] in
            self?.onPitch?(frequency, result.note, result.cents)
        }
    }
}
