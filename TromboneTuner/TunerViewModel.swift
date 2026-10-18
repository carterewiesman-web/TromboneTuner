import Foundation
import SwiftUI

final class TunerViewModel: ObservableObject {

    // MARK: - Published UI state

    @Published var noteName: String = "–"
    @Published var cents: Double = 0
    @Published var frequency: Double = 0
    @Published var instruction: String = "Play a note"
    @Published var instructionColor: Color = .gray
    @Published var isListening: Bool = false

    // MARK: - Tuning logic

    /// Cents tolerance considered "in tune".
    let inTuneCents: Double = 12.0

    private let detector = PitchDetector()

    func start() {
        stop()
        isListening = true
        noteName = "–"
        cents = 0
        frequency = 0
        instruction = "Play a note"
        instructionColor = .gray

        do {
            try detector.start()
        } catch {
            print("Tuner audio start failed: \(error)")
            isListening = false
            instruction = "Mic access needed"
            instructionColor = .red
            return
        }

        detector.onPitch = { [weak self] freq, note, cents in
            guard let self = self else { return }
            DispatchQueue.main.async {
                self.frequency = freq
                self.noteName = note.displayName
                self.cents = cents
                self.updateInstruction(cents: cents)
            }
        }
    }

    func stop() {
        detector.stop()
        isListening = false
        noteName = "–"
        cents = 0
        frequency = 0
        instruction = "Play a note"
        instructionColor = .gray
    }

    private func updateInstruction(cents: Double) {
        if abs(cents) <= inTuneCents {
            instruction = "In tune"
            instructionColor = .green
        } else if cents > inTuneCents {
            // Sharp (too high) → lengthen tube → pull slide out
            instruction = "Pull out"
            instructionColor = .blue
        } else {
            // Flat (too low) → shorten tube → push slide in
            instruction = "Push in"
            instructionColor = .orange
        }
    }
}
