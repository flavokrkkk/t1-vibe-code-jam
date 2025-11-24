import { Sidebar } from "@/widgets/sidebar/ui/sidebar";
import { Suspense } from "react";
import { Outlet, useLocation } from "react-router-dom";

const RootPage = () => {
  const location = useLocation();
  const isAuthRoute = location.pathname.includes("auth");

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
      <div className="relative flex h-screen">
        {!isAuthRoute && <Sidebar />}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </Suspense>
  );
};

export default RootPage;
