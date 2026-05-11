using System.Diagnostics;
using System.IO.Pipes;

namespace AvrSimPipeBridge;

internal static class Program
{
    private sealed record Options(
        string PipeName,
        string AvrSimExe,
        string Firmware,
        string Mcu,
        string Freq,
        string ExtraArgs,
        string LogPath);

    private static readonly object LogLock = new();

    private static int Main(string[] args)
    {
        try
        {
            var options = ParseArgs(args);
            Directory.CreateDirectory(Path.GetDirectoryName(options.LogPath)!);

            using var logWriter = new StreamWriter(options.LogPath, append: true) { AutoFlush = true };
            Log(logWriter, $"[bridge] pipe=\\\\.\\pipe\\{options.PipeName}");
            Log(logWriter, $"[bridge] firmware={options.Firmware}");
            Log(logWriter, $"[bridge] avrsim={options.AvrSimExe}");

            if (!File.Exists(options.AvrSimExe))
            {
                Log(logWriter, "[bridge] missing avrsim executable");
                return 1;
            }

            if (!File.Exists(options.Firmware))
            {
                Log(logWriter, "[bridge] missing firmware image");
                return 1;
            }

            using var pipe = new NamedPipeServerStream(
                options.PipeName,
                PipeDirection.InOut,
                1,
                PipeTransmissionMode.Byte,
                PipeOptions.Asynchronous | PipeOptions.CurrentUserOnly);

            Log(logWriter, "[bridge] waiting for Tera Term");
            pipe.WaitForConnection();
            Log(logWriter, "[bridge] Tera Term connected");

            using var process = StartAvrSim(options);
            Log(logWriter, $"[bridge] avrsim pid={process.Id}");

            var stdoutTask = Task.Run(() => Relay(process.StandardOutput.BaseStream, pipe, logWriter, "stdout"));
            var stdinTask = Task.Run(() => Relay(pipe, process.StandardInput.BaseStream, logWriter, "stdin"));
            var stderrTask = Task.Run(() => Relay(process.StandardError.BaseStream, null, logWriter, "stderr"));

            while (!process.HasExited)
            {
                if (stdoutTask.IsFaulted || stdinTask.IsFaulted || stderrTask.IsFaulted)
                {
                    Log(logWriter, "[bridge] relay faulted; stopping avrsim");
                    TryKill(process);
                    break;
                }

                Thread.Sleep(200);
            }

            process.WaitForExit();
            Log(logWriter, $"[bridge] avrsim exited with code {process.ExitCode}");
            return process.ExitCode;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex);
            return 1;
        }
    }

    private static Options ParseArgs(string[] args)
    {
        string? pipeName = null;
        string? avrsimExe = null;
        string? firmware = null;
        string mcu = "atmega2560";
        string freq = "16000000";
        var extraArgs = new List<string>();
        string? logPath = null;

        for (int i = 0; i < args.Length; ++i)
        {
            switch (args[i])
            {
                case "--pipe-name":
                    pipeName = RequireValue(args, ref i, "--pipe-name");
                    break;
                case "--avrsim-exe":
                    avrsimExe = RequireValue(args, ref i, "--avrsim-exe");
                    break;
                case "--firmware":
                    firmware = RequireValue(args, ref i, "--firmware");
                    break;
                case "--mcu":
                    mcu = RequireValue(args, ref i, "--mcu");
                    break;
                case "--freq":
                    freq = RequireValue(args, ref i, "--freq");
                    break;
                case "--extra-args":
                    extraArgs.AddRange(ReadRemainder(args, ref i));
                    break;
                case "--log-path":
                    logPath = RequireValue(args, ref i, "--log-path");
                    break;
                case "-h":
                case "--help":
                    PrintUsage();
                    Environment.Exit(0);
                    break;
                default:
                    throw new ArgumentException($"Unknown argument: {args[i]}");
            }
        }

        if (pipeName is null)
        {
            pipeName = "PDR16_AT_UART0";
        }
        if (avrsimExe is null)
        {
            throw new ArgumentException("Missing --avrsim-exe");
        }
        if (firmware is null)
        {
            throw new ArgumentException("Missing --firmware");
        }
        logPath ??= Path.Combine(AppContext.BaseDirectory, "AvrSimPipeBridge.log");

        return new Options(pipeName, avrsimExe, firmware, mcu, freq, string.Join(' ', extraArgs).Trim(), logPath);
    }

    private static string RequireValue(string[] args, ref int index, string option)
    {
        if (index + 1 >= args.Length)
        {
            throw new ArgumentException($"Missing value for {option}");
        }

        ++index;
        return args[index];
    }

    private static IEnumerable<string> ReadRemainder(string[] args, ref int index)
    {
        if (index + 1 >= args.Length)
        {
            return Array.Empty<string>();
        }

        var remainder = new string[args.Length - index - 1];
        Array.Copy(args, index + 1, remainder, 0, remainder.Length);
        index = args.Length;
        return remainder;
    }

    private static void PrintUsage()
    {
        Console.WriteLine(
            "Usage: AvrSimPipeBridge --pipe-name <name> --avrsim-exe <path> --firmware <path> [--mcu <name>] [--freq <hz>] [--extra-args <args>] [--log-path <path>]");
    }

    private static Process StartAvrSim(Options options)
    {
        var psi = new ProcessStartInfo
        {
            FileName = options.AvrSimExe,
            UseShellExecute = false,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
            WorkingDirectory = Path.GetDirectoryName(options.AvrSimExe) ?? Environment.CurrentDirectory,
        };

        psi.ArgumentList.Add("-m");
        psi.ArgumentList.Add(options.Mcu);
        psi.ArgumentList.Add("-f");
        psi.ArgumentList.Add(options.Freq);
        psi.ArgumentList.Add(options.Firmware);

        if (!string.IsNullOrWhiteSpace(options.ExtraArgs))
        {
            foreach (var token in SplitArgs(options.ExtraArgs))
            {
                psi.ArgumentList.Add(token);
            }
        }

        return Process.Start(psi) ?? throw new InvalidOperationException("Failed to start avrsim.");
    }

    private static IEnumerable<string> SplitArgs(string commandLine)
    {
        var current = new System.Text.StringBuilder();
        var inQuotes = false;

        foreach (var ch in commandLine)
        {
            if (ch == '"')
            {
                inQuotes = !inQuotes;
                continue;
            }

            if (char.IsWhiteSpace(ch) && !inQuotes)
            {
                if (current.Length > 0)
                {
                    yield return current.ToString();
                    current.Clear();
                }
                continue;
            }

            current.Append(ch);
        }

        if (current.Length > 0)
        {
            yield return current.ToString();
        }
    }

    private static void Relay(Stream source, Stream? destination, StreamWriter logWriter, string label)
    {
        var buffer = new byte[4096];
        try
        {
            while (true)
            {
                var read = source.Read(buffer, 0, buffer.Length);
                if (read <= 0)
                {
                    break;
                }

                destination?.Write(buffer, 0, read);
                destination?.Flush();

                var text = System.Text.Encoding.UTF8.GetString(buffer, 0, read);
                lock (LogLock)
                {
                    logWriter.Write($"[bridge:{label}] ");
                    logWriter.Write(text);
                    if (!text.EndsWith('\n'))
                    {
                        logWriter.WriteLine();
                    }
                    logWriter.Flush();
                }
            }
        }
        catch (Exception ex)
        {
            Log(logWriter, $"[bridge:{label}] relay ended: {ex.Message}");
        }
    }

    private static void Log(StreamWriter writer, string message)
    {
        var line = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} {message}";
        Console.WriteLine(line);
        lock (LogLock)
        {
            writer.WriteLine(line);
            writer.Flush();
        }
    }

    private static void TryKill(Process process)
    {
        try
        {
            if (!process.HasExited)
            {
                process.Kill(entireProcessTree: true);
            }
        }
        catch
        {
            // Best-effort cleanup only.
        }
    }
}
