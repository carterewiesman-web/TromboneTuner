import Foundation

enum NoteCalculator {
    /// Flat-based names, trombone convention (Bb is the instrument's key).
    static let flatNames = ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"]

    /// MIDI note number as a float (A4 = 69 = 440 Hz).
    static func midi(from frequency: Double) -> Double {
        69.0 + 12.0 * log2(frequency / 440.0)
    }

    static func name(forMidi midi: Int) -> String {
        flatNames[((midi % 12) + 12) % 12]
    }

    /// Scientific pitch notation: C4 = middle C.
    static func octave(forMidi midi: Int) -> Int {
        midi / 12 - 1
    }
}
