import { useState, useEffect, useMemo } from "react";
import { useInterview } from "@/entities/interview/hooks/useInterview";
import { InterviewChat } from "@/features/interview/ui/interviewChat";
import { AntiCheatProvider } from "@/shared/lib/antiCheat/antiCheatProvider";
import { AntiCheatRulesDialog } from "@/features/interview/ui/antiCheatRulesDialog";
import {
  hasAcceptedRules,
  setRulesAccepted,
} from "@/shared/lib/antiCheat/rulesStorage";
import { InterviewStatus } from "@/entities/interview/types/types";

const InterviewPage = () => {
  const { data: interview } = useInterview();
  const [showRulesDialog, setShowRulesDialog] = useState(false);
  const [rulesAccepted, setRulesAcceptedState] = useState(false);

  const isInterviewCompleted = useMemo(
    () =>
      interview
        ? interview.status === InterviewStatus.COMPLETED ||
          (interview.overall_feedback !== null &&
            interview.total_score !== null)
        : false,
    [interview]
  );

  useEffect(() => {
    if (interview) {
      const accepted = hasAcceptedRules(interview.id);
      setRulesAcceptedState(accepted);
      if (!accepted && !isInterviewCompleted) {
        setShowRulesDialog(true);
      }
    }
  }, [interview, isInterviewCompleted]);

  const handleAcceptRules = () => {
    if (interview) {
      setRulesAccepted(interview.id);
      setRulesAcceptedState(true);
    }
  };

  if (!interview) return null;

  const isAntiCheatEnabled = rulesAccepted && !isInterviewCompleted;

  return (
    <AntiCheatProvider interviewId={interview.id} enabled={false}>
      <AntiCheatRulesDialog
        open={showRulesDialog}
        onOpenChange={setShowRulesDialog}
        onAccept={handleAcceptRules}
      />
      <div className="flex flex-col items-center h-full justify-center bg-gradient-to-br from-[#e0f2f7] to-[#fce4ec]">
        <div className="absolute inset-0 z-0 pointer-events-none">
          <div className="absolute top-10 left-10 w-48 h-48 bg-purple-500 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
          <div className="absolute bottom-10 right-10 w-48 h-48 bg-pink-400 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
        </div>
        <div className="w-full flex flex-col items-center">
          <InterviewChat initialInterview={interview} />
        </div>
      </div>
    </AntiCheatProvider>
  );
};

export default InterviewPage;
