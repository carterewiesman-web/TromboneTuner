import AVFoundation
import Accelerate

struct PitchMeasurement {
    let frequency: Double
    let rms: Double
    let valid: Bool
}

/// Microphone pitch detector: AVAudioEngine input tap -> ring buffer -> Hann window -> real FFT (Accelerate)
/// -> peak bin with parabolic interpolation -> fundamental frequency.
final class PitchDetector {
    private let audioEngine = AVAudioEngine()
    private var isRunning = false
    private let n = 4096
    private let log2n: vDSP_Length
    private let fftSetup: FFTSetup
    private let magnitudes: [Float]

    private var window: [Float]
    private var ring: [Float]
    private var writeIndex = 0
    private var available = 0

    private let analysisQueue = DispatchQueue(label: "PitchDetector.analysis", qos: .userInitiated)

    var onMeasurement: ((PitchMeasurement) -> Void)?

    /// Trombone-relevant range: E1 fundamental territory up past high Bb5.
    private let minFreq = 40.0
    private let maxFreq = 1400.0
    /// RMS silence gate.
    private let silenceThreshold: Float = 0.006

    init() {
        log2n = vDSP_Length(Int(log2(Double(n))))
        fftSetup = vDSP_create_fftsetup(log2n, FFTRadix(kFFTRadix2))!
        magnitudes = [Float](repeating: 0, count: n / 2)
        window = [Float](repeating: 0, count: n)
        for i in 0..<n {
            window[i] = 0.5 * (1.0 - cos(2.0 * .pi * Float(i) / Float(n - 1)))
        }
        ring = [Float](repeating: 0, count: n * 2)
    }

    deinit {
        vDSP_destroy_fftsetup(fftSetup)
    }

    // MARK: - Permission + lifecycle

    func requestPermission(onDenied: @escaping () -> Void, onGranted: @escaping () -> Void) {
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            DispatchQueue.main.async { granted ? onGranted() : onDenied() }
        }
    }

    private var lastKnownSampleRate: Double = 48000

    func start() throws {
        // Idempotency: a second installTap on the same bus crashes AVFAudio
        // ("required condition is false: nullptr == Tap()").
        guard !isRunning else { return }

        let session = AVAudioSession.sharedInstance()
        try session.setCategory(.playAndRecord, mode: .measurement, options: [.defaultToSpeaker])
        try session.setActive(true)

        let input = audioEngine.inputNode
        let format = input.outputFormat(forBus: 0)
        lastKnownSampleRate = format.sampleRate > 0 ? format.sampleRate : 48000
        input.installTap(onBus: 0, bufferSize: UInt32(n), format: format) { [weak self] buffer, _ in
            self?.handle(buffer)
        }
        audioEngine.prepare()
        try audioEngine.start()
        isRunning = true
    }

    func stop() {
        guard isRunning else { return }
        isRunning = false
        audioEngine.inputNode.removeTap(onBus: 0)
        audioEngine.stop()
        try? AVAudioSession.sharedInstance().setActive(false, options: .notifyOthersOnDeactivation)
        analysisQueue.async { [weak self] in
            self?.available = 0
            self?.writeIndex = 0
        }
    }

    // MARK: - Capture

    private func handle(_ buffer: AVAudioPCMBuffer) {
        guard buffer.format.commonFormat == .pcmFormatFloat32,
              let channelData = buffer.floatChannelData,
              buffer.frameLength > 0 else { return }
        let chunk = Array(UnsafeBufferPointer(start: channelData[0], count: Int(buffer.frameLength)))
        analysisQueue.async { [weak self] in
            self?.accumulate(chunk)
        }
    }

    private func accumulate(_ chunk: [Float]) {
        let capacity = ring.count
        for sample in chunk {
            ring[writeIndex] = sample
            writeIndex = (writeIndex + 1) % capacity
        }
        available = min(available + chunk.count, capacity)
        guard available >= n else { return }

        var frame = [Float](repeating: 0, count: n)
        let start = (writeIndex - n + capacity) % capacity
        for i in 0..<n {
            frame[i] = ring[(start + i) % capacity]
        }
        analyze(frame)
    }

    // MARK: - FFT analysis

    private func analyze(_ frame: [Float]) {
        var rms: Float = 0
        vDSP_rmsqv(frame, 1, &rms, vDSP_Length(n))

        guard rms > silenceThreshold else {
            emit(frequency: 0, rms: Double(rms), valid: false)
            return
        }

        var windowed = [Float](repeating: 0, count: n)
        vDSP_vmul(frame, 1, window, 1, &windowed, 1, vDSP_Length(n))

        var real = [Float](repeating: 0, count: n / 2)
        var imag = [Float](repeating: 0, count: n / 2)
        var mags = magnitudes

        real.withUnsafeMutableBufferPointer { realPtr in
            imag.withUnsafeMutableBufferPointer { imagPtr in
                var split = DSPSplitComplex(realp: realPtr.baseAddress!, imagp: imagPtr.baseAddress!)
                windowed.withUnsafeBufferPointer { wp in
                    wp.baseAddress!.withMemoryRebound(to: DSPComplex.self, capacity: n / 2) { cp in
                        vDSP_ctoz(cp, 2, &split, 1, vDSP_Length(n / 2))
                    }
                }
                vDSP_fft_zrip(fftSetup, &split, 1, log2n, FFTDirection(FFT_FORWARD))
                vDSP_zvmags(&split, 1, &mags, 1, vDSP_Length(n / 2))
            }
        }

        let sampleRate = lastKnownSampleRate
        let minBin = max(2, Int(minFreq * Double(n) / sampleRate))
        let maxBin = min(n / 2 - 2, Int(maxFreq * Double(n) / sampleRate))
        guard minBin < maxBin else {
            emit(frequency: 0, rms: Double(rms), valid: false)
            return
        }

        // Peak bin
        var peakBin = minBin
        var peakValue: Float = 0
        for i in minBin...maxBin where mags[i] > peakValue {
            peakValue = mags[i]
            peakBin = i
        }

        // Prominence check: peak must stand out from band average.
        var bandSum: Float = 0
        mags.withUnsafeBufferPointer { buf in
            vDSP_sve(buf.baseAddress! + minBin, 1, &bandSum, vDSP_Length(maxBin - minBin + 1))
        }
        let bandMean = bandSum / Float(maxBin - minBin + 1)
        guard peakValue > max(1e-8, bandMean * 4), peakBin > minBin, peakBin < maxBin else {
            emit(frequency: 0, rms: Double(rms), valid: false)
            return
        }

        // Parabolic interpolation around the peak for sub-bin accuracy.
        let yMinus1 = mags[peakBin - 1]
        let yZero = mags[peakBin]
        let yPlus1 = mags[peakBin + 1]
        let denom = yMinus1 - 2 * yZero + yPlus1
        var delta: Float = 0
        if denom != 0 {
            delta = 0.5 * (yMinus1 - yPlus1) / denom
            delta = max(-0.5, min(0.5, delta))
        }

        let frequency = (Double(peakBin) + Double(delta)) * sampleRate / Double(n)
        guard frequency >= minFreq, frequency <= maxFreq else {
            emit(frequency: 0, rms: Double(rms), valid: false)
            return
        }
        emit(frequency: frequency, rms: Double(rms), valid: true)
    }

    private func emit(frequency: Double, rms: Double, valid: Bool) {
        let measurement = PitchMeasurement(frequency: frequency, rms: rms, valid: valid)
        let callback = onMeasurement
        DispatchQueue.main.async {
            callback?(measurement)
        }
    }
}
