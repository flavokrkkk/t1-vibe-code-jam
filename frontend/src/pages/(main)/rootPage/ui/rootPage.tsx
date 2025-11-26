import { Sidebar } from "@/widgets/sidebar/ui/sidebar";
import { Suspense } from "react";
import { Outlet, useLocation } from "react-router-dom";

const RootPage = () => {
  const location = useLocation();
  const isAuthRoute = location.pathname.includes("auth");
  const isLandingRoute = location.pathname.includes("landing");

  return (
    <Suspense
      fallback={
        <div className="flex h-screen w-full items-center justify-center">
          <img
            alt="logo-suspense"
            src="/images/logo.jpg"
            className="h-6 w-6 animate-ping rounded-sm"
          />
        </div>
      }
    >
      <div className="relative flex h-screen bg-gradient-to-br from-[#e0f2f7] to-[#fce4ec]">
        <div className="absolute inset-0 z-0 pointer-events-none">
          <div className="absolute top-10 left-10 w-48 h-48 bg-purple-500 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
          <div className="absolute bottom-10 right-10 w-48 h-48 bg-pink-400 opacity-20 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
        </div>
        {!isAuthRoute && !isLandingRoute && <Sidebar />}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </Suspense>
  );
};

export default RootPage;
