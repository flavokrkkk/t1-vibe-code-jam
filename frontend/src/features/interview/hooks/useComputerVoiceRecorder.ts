import { useCallback, useEffect, useRef, useState } from "react";

interface UseComputerVoiceRecorderReturn {
  isRecording: boolean;
  isPaused: boolean;
  elapsedSec: number;
  progressPct: number;
  error: string | null;
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  togglePause: () => void;
}

export const useComputerVoiceRecorder = (opts?: {
  maxDurationSec?: number;
  sendCallback?: (blob: Blob) => void;
}): UseComputerVoiceRecorderReturn => {
  const maxDuration = opts?.maxDurationSec ?? 300;

  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [elapsedSec, setElapsedSec] = useState(0);
  const [progressPct, setProgressPct] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);

  const intervalRef = useRef<number | null>(null);

  const sendAudio = useCallback(async (blob: Blob) => {
    try {
      opts?.sendCallback?.(blob);
    } catch (err) {
      setError("Ошибка при отправке аудио");
      console.error("Audio upload error:", err);
    }
  }, []);

  useEffect(() => {
    if (intervalRef.current) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (isRecording && !isPaused) {
      intervalRef.current = window.setInterval(() => {
        setElapsedSec((s) => {
          const next = s + 1;
          setProgressPct(Math.min(100, Math.round((next / maxDuration) * 100)));
          if (next >= maxDuration) {
            setTimeout(() => {
              try {
                if (
                  mediaRecorderRef.current &&
                  mediaRecorderRef.current.state !== "inactive"
                )
                  mediaRecorderRef.current.stop();
              } catch (e) {
                console.error(e);
              }
            }, 0);
          }
          return next;
        });
      }, 1000);
    }

    return () => {
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isRecording, isPaused, maxDuration]);

  const startRecording = useCallback(async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();

      const systemAudioDevice = devices.find(
        (device) =>
          device.kind === "audioinput" &&
          (device.label.toLowerCase().includes("stereo mix") ||
            device.label.toLowerCase().includes("cable input") ||
            device.label.toLowerCase().includes("blackhole"))
      );

      const constraints: MediaStreamConstraints = {
        audio: systemAudioDevice
          ? { deviceId: systemAudioDevice.deviceId }
          : true,
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
      mediaRecorderRef.current = mr;
      chunksRef.current = [];

      mr.ondataavailable = (e: BlobEvent) => {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      mr.onstop = async () => {
        try {
          const blob = new Blob(chunksRef.current, { type: "audio/webm" });
          await sendAudio(blob);
        } finally {
          chunksRef.current = [];
          if (streamRef.current) {
            streamRef.current.getTracks().forEach((t) => t.stop());
            streamRef.current = null;
          }
          mediaRecorderRef.current = null;
          setIsRecording(false);
          setIsPaused(false);
        }
      };

      setElapsedSec(0);
      setProgressPct(0);
      setError(null);

      mr.start();
      setIsRecording(true);
      setIsPaused(false);
    } catch (err) {
      setError("Не удалось начать запись. Проверьте доступ к устройствам.");
      console.error("Recording start error:", err);
      throw err;
    }
  }, [sendAudio]);

  const stopRecording = useCallback(() => {
    try {
      if (
        mediaRecorderRef.current &&
        mediaRecorderRef.current.state !== "inactive"
      ) {
        mediaRecorderRef.current.stop();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRecording(false);
      setIsPaused(false);
    }
  }, []);

  const pauseRecording = useCallback(() => {
    try {
      if (
        mediaRecorderRef.current &&
        typeof mediaRecorderRef.current.pause === "function" &&
        mediaRecorderRef.current.state === "recording"
      ) {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
      } else {
        console.warn(
          "MediaRecorder.pause not available or invalid state; using soft pause"
        );
        setIsPaused(true);
      }
    } catch (e) {
      console.error("pause error", e);
      setError("Ошибка при попытке поставить запись на паузу");
    }
  }, []);

  const resumeRecording = useCallback(() => {
    try {
      if (
        mediaRecorderRef.current &&
        typeof mediaRecorderRef.current.resume === "function" &&
        mediaRecorderRef.current.state === "paused"
      ) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
      } else {
        console.warn(
          "MediaRecorder.resume not available or invalid state; using soft resume"
        );
        setIsPaused(false);
      }
    } catch (e) {
      console.error("resume error", e);
      setError("Ошибка при попытке возобновить запись");
    }
  }, []);

  const togglePause = () => {
    if (!isRecording) return;
    if (isPaused) resumeRecording();
    else pauseRecording();
  };

  useEffect(() => {
    return () => {
      try {
        if (
          mediaRecorderRef.current &&
          mediaRecorderRef.current.state !== "inactive"
        )
          mediaRecorderRef.current.stop();
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((t) => t.stop());
          streamRef.current = null;
        }
      } catch (e) {}
    };
  }, []);

  return {
    isRecording,
    isPaused,
    elapsedSec,
    progressPct,
    error,
    startRecording,
    stopRecording,
    togglePause,
  };
};
