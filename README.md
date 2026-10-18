# Trombone Tuner

iOS trombone tuner built with SwiftUI. Listens to the microphone, shows the nearest
note and octave, and tells you whether to **push in** or **pull out** the slide.

- Note + octave display (scientific pitch notation, flat names — B♭ is B♭)
- Push in / pull out / in tune indicator with a dead zone of ±6 cents
- Cents meter (-50 to +50)
- Pitch detection: AVAudioEngine input tap → 4096-sample Hann window → real FFT
  (Accelerate vDSP) → peak bin + parabolic interpolation, median-filtered

## Build (GitHub Actions)

Every push to `main` builds an unsigned IPA via `.github/workflows/build.yml`
(XcodeGen + xcodebuild archive, `CODE_SIGNING_ALLOWED=NO`). Download the
`TromboneTuner-ipa` artifact from the Actions run — it contains
`TromboneTuner.ipa`, ready for LiveContainer.

## Local build

```sh
brew install xcodegen
xcodegen generate
xcodebuild -project TromboneTuner.xcodeproj -scheme TromboneTuner \
  -configuration Release -sdk iphoneos \
  -archivePath build/TromboneTuner.xcarchive archive CODE_SIGNING_ALLOWED=NO
mkdir -p build/Payload
cp -R build/TromboneTuner.xcarchive/Products/Applications/TromboneTuner.app build/Payload/
cd build && zip -qry TromboneTuner.ipa Payload
```
