import SwiftUI

struct ContentView: View {
    @StateObject private var vm = TunerViewModel()

    var body: some View {
        ZStack {
            // Background
            Color.black.ignoresSafeArea()

            VStack(spacing: 24) {
                // Header / status
                HStack {
                    Text("TROMBONE TUNER")
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                        .foregroundColor(.secondary)
                    Spacer()
                    Circle()
                        .fill(vm.isListening ? Color.green : Color.gray.opacity(0.4))
                        .frame(width: 10, height: 10)
                    Text(vm.isListening ? "LISTENING" : "STOPPED")
                        .font(.system(size: 12, weight: .bold, design: .monospaced))
                        .foregroundColor(vm.isListening ? .green : .gray)
                }
                .padding(.horizontal, 40)
                .padding(.top, 44)

                Spacer(minLength: 40)

                // Note name (large)
                Text(vm.noteName)
                    .font(.system(size: 130, weight: .thin, design: .rounded))
                    .foregroundColor(.white)
                    .monospacedDigit()
                    .contentTransition(.numericText())

                // Cents readout
                Text(String(format: "%+0.0f ¢", vm.cents))
                    .font(.system(size: 34, weight: .medium, design: .monospaced))
                    .foregroundColor(vm.instructionColor.opacity(0.9))

                // Needle gauge
                NeedleGauge(cents: vm.cents, range: 50)
                    .frame(height: 120)
                    .padding(.horizontal, 60)

                // Instruction (the core ask: push in / pull out / in tune)
                Text(vm.instruction)
                    .font(.system(size: 40, weight: .bold, design: .rounded))
                    .foregroundColor(vm.instructionColor)
                    .animation(.easeInOut(duration: 0.15), value: vm.instruction)

                // Frequency (small, subtle)
                Text(String(format: "%.2f Hz", vm.frequency))
                    .font(.system(size: 16, weight: .regular, design: .monospaced))
                    .foregroundColor(.secondary)

                Spacer(minLength: 40)

                // Start / stop button
                Button(action: {
                    if vm.isListening { vm.stop() } else { vm.start() }
                }) {
                    Text(vm.isListening ? "STOP" : "START")
                        .font(.system(size: 17, weight: .semibold, design: .rounded))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(vm.isListening ? Color.red : Color.blue)
                        .clipShape(Capsule())
                }
                .padding(.horizontal, 60)
                .padding(.bottom, 40)
            }
        }
        .onAppear {
            vm.start()
        }
        .onDisappear {
            vm.stop()
        }
    }
}

/// Arc needle gauge: center = in tune, left = flat (push in), right = sharp (pull out).
struct NeedleGauge: View {
    let cents: Double
    let range: Double

    private var degrees: Double {
        let clamped = max(-range, min(range, cents))
        return (clamped / range) * 35.0 // ±35° swing
    }

    var body: some View {
        ZStack {
            // Arc track
            ArcShape(startAngle: .degrees(-35), endAngle: .degrees(35), clockwise: false)
                .stroke(Color.gray.opacity(0.25), lineWidth: 10)

            // Zone markers
            HStack(spacing: 0) {
                Text("PUSH IN")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(.orange.opacity(0.7))
                    .frame(maxWidth: .infinity)
                Text("IN TUNE")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(.green.opacity(0.7))
                    .frame(maxWidth: .infinity)
                Text("PULL OUT")
                    .font(.system(size: 11, weight: .bold, design: .monospaced))
                    .foregroundColor(.blue.opacity(0.7))
                    .frame(maxWidth: .infinity)
            }
            .padding(.horizontal, 30)

            // Needle
            Needle(angle: .degrees(degrees))
                .frame(width: 4, height: 90)
                .offset(y: -40)

            // Center pivot
            Circle()
                .fill(Color.white)
                .frame(width: 10, height: 10)
        }
    }
}

/// Simple arc.
struct ArcShape: Shape {
    let startAngle: Angle
    let endAngle: Angle
    let clockwise: Bool

    func path(in rect: CGRect) -> Path {
        var p = Path()
        let center = CGPoint(x: rect.midX, y: rect.midY)
        let radius = min(rect.width, rect.height) / 2 * 0.85
        p.addArc(center: center,
                 radius: radius,
                 startAngle: startAngle,
                 endAngle: endAngle,
                 clockwise: clockwise)
        return p.strokedPath(.init(lineWidth: 10, lineCap: .round))
    }
}

/// Rotating needle.
struct Needle: View {
    let angle: Angle

    var body: some View {
        RoundedRectangle(cornerRadius: 2)
            .fill(Color.white)
            .rotationEffect(angle, anchor: .bottom)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
