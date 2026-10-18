import Foundation

/// A musical note with its concert-pitch frequency and MIDI number.
struct Note: Equatable, CustomStringConvertible {
    let midi: Int
    let frequency: Double
    let name: String   // e.g. "B♭", "A", "C#"
    let octave: Int

    var displayName: String {
        "\(name)\(octave)"
    }

    var description: String {
        "\(displayName) (\(String(format: "%.2f", frequency)) Hz)"
    }

    static let names = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]

    /// Frequency of a MIDI note (A4 = 440 Hz).
    static func frequency(for midi: Int) -> Double {
        440.0 * pow(2.0, Double(midi - 69) / 12.0)
    }

    /// Nearest Note to a given frequency.
    static func nearest(to frequency: Double) -> (note: Note, cents: Double) {
        guard frequency > 0 else {
            return (Note(midi: 69, frequency: 440, name: "A", octave: 4), 0)
        }
        let midiDouble = 69.0 + 12.0 * log2(frequency / 440.0)
        let clamped = min(127, max(0, Int(midiDouble.rounded())))
        let freq = Note.frequency(for: clamped)
        let noteIndex = clamped % 12
        let octave = clamped / 12 - 1
        let note = Note(midi: clamped, frequency: freq, name: Note.names[noteIndex], octave: octave)
        let cents = 1200.0 * log2(frequency / freq)
        return (note, cents)
    }
}
