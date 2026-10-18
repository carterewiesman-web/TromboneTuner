# GitHub Actions Build — Trombone Tuner IPA

This workflow compiles the Swift source into an **unsigned** `.ipa` using GitHub's macOS runner. No Mac, no Apple Developer account, no signing required.

## What you need to commit to GitHub

The Swift files alone aren't enough — `xcodebuild` needs an Xcode project file (`.xcodeproj`) with the files added and a shared scheme.

**One-time setup (requires access to any Mac with Xcode — borrow one, use a friend's, etc.):**

1. Open Xcode → File → New → Project → **App** (iOS).
   - Product Name: `TromboneTuner`
   - Interface: **SwiftUI**, Language: **Swift**
2. Drag the five `.swift` files from `TromboneTuner/TromboneTuner/` into the project.
3. Add microphone permission: `Info.plist` → `NSMicrophoneUsageDescription` = `"TromboneTuner needs microphone access to detect pitch."`
4. **Share the scheme:** Product → Scheme → Manage Schemes → check **Shared** next to `TromboneTuner`.
5. Set **Minimum Deployments** to iOS 16.0 or higher (project settings → General).
6. Save and close.

**Commit these to your repo:**
```
.github/workflows/ios.yml
TromboneTunerApp.swift
ContentView.swift
TunerViewModel.swift
PitchDetector.swift
Note.swift
TromboneTuner.xcodeproj/        (the whole folder)
TromboneTuner.xcworkspace/       (if created)
Info.plist
```

## Push and run

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOURUSER/TromboneTuner.git
git push -u origin main
```

Then go to the **Actions** tab in GitHub → **Build Trombone Tuner IPA** → **Run workflow**.

## Download the IPA

When the workflow finishes, go to the **Artifacts** section of the run page and download `TromboneTuner-ipa`.

The downloaded `.ipa` is unsigned. Sideload it with LiveContainer on your iPhone.

## Notes

- `macos-latest` runners include Xcode. The workflow switches to `Xcode_15` explicitly; change to `Xcode_16` if that's what's installed on the runner at runtime.
- Build takes ~3–6 minutes on the macOS runner.
- The IPA is unsigned because `CODE_SIGNING_ALLOWED=NO`. If LiveContainer rejects unsigned apps, you can re-sign it later with `ios-app-signer` or a similar tool on any computer.
- No ads, no network, no SDK dependencies beyond Apple frameworks.
