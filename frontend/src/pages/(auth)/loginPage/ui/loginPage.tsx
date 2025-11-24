import { AuthWrapper } from "@/entities/auth/ui/authWrapper";
import { LoginForm } from "@/entities/auth/ui/loginForm";

const LoginPage = () => {
  return (
    <div className="space-y-2 w-full flex flex-col justify-center">
      <AuthWrapper>
        <LoginForm />
      </AuthWrapper>
    </div>
  );
};

export default LoginPage;
