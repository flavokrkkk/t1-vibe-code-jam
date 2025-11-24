import { Outlet } from "react-router-dom";

const AuthPage = () => {
  return (
    <div className="h-full w-full flex items-center justify-center">
      <Outlet />
    </div>
  );
};

export default AuthPage;
