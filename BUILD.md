# Trombone Tuner — iOS App

Fast, ad-free trombone tuner built in SwiftUI + AVFoundation + Accelerate (FFT).

## What it does
- Listens via the microphone and detects pitch in real time (FFT with parabolic interpolation).
- Shows the detected **note** (concert pitch) and **cents** offset.
- Tells you exactly what to do with the tuning slide:
  - **Sharp (too high)** → "Pull out" (lengthen the tube to lower pitch)
  - **Flat (too low)** → "Push in" (shorten the tube to raise pitch)
  - Within ±12¢ → "In tune"
- No ads, no network, loads instantly.

## Files (drop these into an Xcode iOS App project)
| File | Purpose |
|------|---------|
| `TromboneTunerApp.swift` | `@main` entry point |
| `ContentView.swift` | Needle gauge + note + push/pull UI |
| `TunerViewModel.swift` | Audio session + pitch-to-instruction logic |
| `PitchDetector.swift` | Real-time FFT pitch detector (Accelerate vDSP) |
| `Note.swift` | Frequency ↔ note name ↔ cents math |

## How to build the .ipa (macOS only)

An `.ipa` is a signed iOS bundle. You **must** build it on a Mac with Xcode.

1. **Install Xcode** from the App Store (includes the iOS SDK & toolchain).
2. **Create the project:**
   - Open Xcode → File → New → Project → **App** (iOS).
   - Product Name: `TromboneTuner`
   - Interface: **SwiftUI**, Language: **Swift**, Storage: None.
3. **Add the source files:** Drag the five `.swift` files above into the project (Copy items if needed).
4. **Microphone permission:** Open `Info.plist` and add:
   - Key: `NSMicrophoneUsageDescription`
   - Value: `"TromboneTuner needs microphone access to detect your instrument's pitch."`
5. **Select a real device** (Generic iOS Device or a connected iPhone) — the simulator cannot access the mic reliably and cannot produce a device IPA.
6. **Signing:** In the project settings → Signing & Capabilities, select your Apple Developer account/team. A free Apple ID can sideload to your own device; a paid Developer account is needed to distribute the `.ipa`.
7. **Build:** Product → Build (⌘B). Fix any warnings.
8. **Archive:** Product → Archive.
9. **Export IPA:** In the Organizer, select the archive → Distribute App → Ad Hoc or Development → export the `.ipa`.

## Install on your iPhone
- Connect the iPhone via USB, trust the computer, and install the exported `.ipa` via Xcode (Window → Devices and Simulators → drag `.ipa` onto the device) or Apple Configurator.

## Notes
- Tuning tolerance is ±12 cents (adjust `inTuneCents` in `TunerViewModel.swift`).
- Detection range: 50 Hz – 1300 Hz (covers trombone pedal B♭1 up through the high register).
- The note label uses sharp enharmonics (e.g. B♭ shows as A♯); the pitch and cents are exact.
- No third-party dependencies — only Apple frameworks (`SwiftUI`, `AVFoundation`, `Accelerate`).
