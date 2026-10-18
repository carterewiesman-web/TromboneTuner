import SwiftUI
import UIKit

@MainActor
final class TunerViewModel: ObservableObject {
    enum Direction {
        case pushIn, pullOut, inTune, silent
    }

    @Published private(set) var noteName = "–"
    @Published private(set) var octave = 4
    @Published private(set) var cents = 0.0
    @Published private(set) var frequency = 0.0
    @Published private(set) var direction: Direction = .silent
    @Published private(set) var permissionDenied = false

    private let detector = PitchDetector()
    private var midiHistory: [Double] = []
    private let historySize = 7
    private let deadZoneCents = 6.0
    private var running = false

    func start() {
        guard !running else { return }
        detector.onMeasurement = { [weak self] measurement in
            Task { @MainActor [weak self] in
                self?.process(measurement)
            }
        }
        detector.requestPermission { [weak self] in
            self?.permissionDenied = true
        } onGranted: { [weak self] in
            guard let self else { return }
            do {
                try self.detector.start()
                self.running = true
            } catch {
                self.permissionDenied = true
            }
        }
    }

    func stop() {
        guard running else { return }
        detector.stop()
        running = false
        direction = .silent
        midiHistory.removeAll()
    }

    func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }

    private func process(_ measurement: PitchMeasurement) {
        guard measurement.valid, measurement.frequency > 0 else {
            midiHistory.removeAll()
            direction = .silent
            return
        }

        let midi = NoteCalculator.midi(from: measurement.frequency)
        midiHistory.append(midi)
        if midiHistory.count > historySize {
            midiHistory.removeFirst()
        }

        // Median of recent MIDI values stabilizes against jitter and octave glitches.
        let sorted = midiHistory.sorted()
        let median = sorted[sorted.count / 2]
        let nearest = Int(median.rounded())
        let centsOff = (median - Double(nearest)) * 100.0

        frequency = measurement.frequency
        noteName = NoteCalculator.name(forMidi: nearest)
        octave = NoteCalculator.octave(forMidi: nearest)
        cents = centsOff

        if centsOff < -deadZoneCents {
            direction = .pushIn
        } else if centsOff > deadZoneCents {
            direction = .pullOut
        } else {
            direction = .inTune
        }
    }
}
