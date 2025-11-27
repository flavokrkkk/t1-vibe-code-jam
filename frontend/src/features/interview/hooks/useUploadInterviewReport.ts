import { useCallback, useState } from "react";
import { supabase } from "@/shared/lib/supabase/client";
import { useUpdateInterviewResult } from "@/entities/interview/hooks/useUpdateInterviewResult";

interface UploadInterviewReportParams {
  interviewId: string;
  file: Blob;
  fileName: string;
}

interface UseUploadInterviewReportResult {
  uploadInterviewReport: (
    params: UploadInterviewReportParams
  ) => Promise<string | null>;
  isUploading: boolean;
}

const REPORTS_BUCKET_NAME = "blimfy";

export const useUploadInterviewReport = (): UseUploadInterviewReportResult => {
  const [isUploading, setIsUploading] = useState(false);
  const updateInterviewResultMutation = useUpdateInterviewResult();

  const uploadInterviewReport = useCallback(
    async ({ interviewId, file, fileName }: UploadInterviewReportParams) => {
      if (!file) return null;

      setIsUploading(true);
      try {
        // Приводим имя файла к безопасному для Supabase Storage виду:
        // - убираем пробелы и спецсимволы
        // - избавляемся от потенциально проблемной кириллицы
        const safeFileName = fileName
          .normalize("NFKD")
          .replace(/[^\w.-]+/g, "_")
          .replace(/_+/g, "_")
          .toLowerCase();

        const path = `${interviewId}/${Date.now()}_${safeFileName}`;

        const { error: uploadError } = await supabase.storage
          .from(REPORTS_BUCKET_NAME)
          .upload(path, file, {
            cacheControl: "3600",
            upsert: false,
            contentType: "application/pdf",
          });

        if (uploadError) {
          // eslint-disable-next-line no-console
          console.error(
            "Error uploading interview report to Supabase",
            uploadError
          );
          throw uploadError;
        }

        const { data } = supabase.storage
          .from(REPORTS_BUCKET_NAME)
          .getPublicUrl(path);

        const publicUrl = data.publicUrl;

        if (!publicUrl) {
          // eslint-disable-next-line no-console
          console.error("Failed to get public URL for uploaded report");
          return null;
        }

        await updateInterviewResultMutation.mutateAsync({
          interviewId,
          resultUrl: publicUrl,
        });

        return publicUrl;
      } catch (error) {
        // eslint-disable-next-line no-console
        console.error("Failed to upload and save interview report", error);
        return null;
      } finally {
        setIsUploading(false);
      }
    },
    [updateInterviewResultMutation]
  );

  return {
    uploadInterviewReport,
    isUploading,
  };
};
