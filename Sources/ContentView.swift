import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = TunerViewModel()
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [
                    Color(red: 0.07, green: 0.09, blue: 0.15),
                    Color(red: 0.02, green: 0.03, blue: 0.06),
                ],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            VStack(spacing: 26) {
                Text("TROMBONE TUNER")
                    .font(.system(.caption, design: .monospaced).weight(.semibold))
                    .tracking(4)
                    .foregroundColor(.white.opacity(0.55))

                Spacer(minLength: 8)

                if viewModel.permissionDenied {
                    permissionView
                } else {
                    noteView
                    directionCard
                    centsMeter
                    Spacer(minLength: 8)
                    Text("Play a steady note into the mic")
                        .font(.footnote)
                        .foregroundColor(.white.opacity(0.4))
                }
            }
            .padding(26)
        }
        .onAppear { viewModel.start() }
        .onDisappear { viewModel.stop() }
        .onChange(of: scenePhase) { phase in
            switch phase {
            case .active:
                viewModel.start()
            case .background, .inactive:
                viewModel.stop()
            @unknown default:
                break
            }
        }
    }

    // MARK: - Note display

    private var noteView: some View {
        let silent = viewModel.direction == .silent
        return VStack(spacing: 10) {
            HStack(alignment: .firstTextBaseline, spacing: 2) {
                Text(silent ? "—" : viewModel.noteName)
                    .font(.system(size: 116, weight: .bold, design: .rounded))
                if !silent {
                    Text("\(viewModel.octave)")
                        .font(.system(size: 56, weight: .bold, design: .rounded))
                        .foregroundColor(.white.opacity(0.7))
                }
            }
            .foregroundColor(.white)
            .minimumScaleFactor(0.5)
            .lineLimit(1)
            .animation(.easeOut(duration: 0.15), value: viewModel.noteName)
            .animation(.easeOut(duration: 0.15), value: viewModel.octave)

            HStack(spacing: 14) {
                if !silent {
                    Text(String(format: "%.1f Hz", viewModel.frequency))
                    Text("·")
                    Text(String(format: "%+.0f ¢", viewModel.cents))
                }
            }
            .font(.system(.body, design: .monospaced))
            .foregroundColor(.white.opacity(0.6))
        }
    }

    // MARK: - Push / pull card

    private var directionCard: some View {
        let config = directionConfig(viewModel.direction)
        return HStack(spacing: 14) {
            Image(systemName: config.icon)
                .font(.system(size: 32, weight: .bold))
                .frame(width: 44)
            VStack(alignment: .leading, spacing: 3) {
                Text(config.title)
                    .font(.system(size: 26, weight: .heavy, design: .rounded))
                Text(config.subtitle)
                    .font(.footnote)
                    .opacity(0.8)
            }
            Spacer(minLength: 0)
        }
        .foregroundColor(.white)
        .padding(.horizontal, 22)
        .padding(.vertical, 18)
        .background(config.color.opacity(0.18))
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(config.color.opacity(0.6), lineWidth: 1.5)
        )
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .animation(.easeInOut(duration: 0.12), value: viewModel.direction)
    }

    private func directionConfig(_ direction: TunerViewModel.Direction) -> (icon: String, title: String, subtitle: String, color: Color) {
        switch direction {
        case .pushIn:
            return (
                "arrow.up",
                "PUSH IN",
                "Flat — shorten the slide to raise the pitch",
                Color(red: 0.30, green: 0.70, blue: 1.00)
            )
        case .pullOut:
            return (
                "arrow.down",
                "PULL OUT",
                "Sharp — extend the slide to lower the pitch",
                Color(red: 1.00, green: 0.60, blue: 0.25)
            )
        case .inTune:
            return (
                "checkmark",
                "IN TUNE",
                "Right where it should be",
                Color(red: 0.35, green: 0.90, blue: 0.50)
            )
        case .silent:
            return (
                "ear",
                "LISTENING",
                "Play a note when you are ready",
                Color(white: 0.6)
            )
        }
    }

    // MARK: - Cents meter

    private var centsMeter: some View {
        let clamped = max(-50.0, min(50.0, viewModel.cents))
        let accent = accentColor

        return VStack(spacing: 4) {
            GeometryReader { geo in
                let x = (clamped / 100.0 + 0.5) * geo.size.width
                ZStack {
                    Capsule()
                        .fill(Color.white.opacity(0.10))
                        .frame(height: 8)

                    HStack(spacing: 0) {
                        ForEach(0..<11, id: \.self) { i in
                            Rectangle()
                                .fill(Color.white.opacity(i == 5 ? 0.65 : 0.25))
                                .frame(width: 1.5, height: i % 5 == 0 ? 18 : 10)
                            if i < 10 {
                                Spacer()
                            }
                        }
                    }

                    Circle()
                        .fill(accent)
                        .frame(width: 22, height: 22)
                        .shadow(color: accent.opacity(0.85), radius: 9)
                        .position(x: x, y: geo.size.height / 2)
                        .animation(.spring(response: 0.25, dampingFraction: 0.85), value: clamped)
                }
            }
            .frame(height: 56)

            HStack {
                Text("-50")
                Spacer()
                Text("0")
                Spacer()
                Text("+50")
            }
            .font(.system(.caption2, design: .monospaced))
            .foregroundColor(.white.opacity(0.45))
        }
    }

    private var accentColor: Color {
        switch viewModel.direction {
        case .pushIn: return Color(red: 0.30, green: 0.70, blue: 1.00)
        case .pullOut: return Color(red: 1.00, green: 0.60, blue: 0.25)
        case .inTune: return Color(red: 0.35, green: 0.90, blue: 0.50)
        case .silent: return Color(white: 0.6)
        }
    }

    // MARK: - Permission

    private var permissionView: some View {
        VStack(spacing: 18) {
            Image(systemName: "mic.slash.fill")
                .font(.system(size: 46))
                .foregroundColor(.orange)
            Text("Microphone access is needed to hear your trombone.")
                .multilineTextAlignment(.center)
                .foregroundColor(.white.opacity(0.8))
            Button {
                viewModel.openSettings()
            } label: {
                Text("Open Settings")
                    .fontWeight(.semibold)
                    .foregroundColor(.white)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 12)
                    .background(Color.blue.opacity(0.85))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
        }
        .padding(.top, 60)
    }
}

#Preview {
    ContentView()
}
