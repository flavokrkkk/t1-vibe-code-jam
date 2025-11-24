import { InterviewCreateForm } from "@/entities/interview/ui/interviewCreateForm";

const DashboardPage = () => {
  return (
    <div className="h-full flex items-center justify-center bg-gradient-to-br from-[#e0f2f7] to-[#fce4ec] relative">
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-10 left-10 w-48 h-48 bg-purple-500 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute bottom-10 right-10 w-48 h-48 bg-pink-400 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>
      <InterviewCreateForm />
    </div>
  );
};

export default DashboardPage;
