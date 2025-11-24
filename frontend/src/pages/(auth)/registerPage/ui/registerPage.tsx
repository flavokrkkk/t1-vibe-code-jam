import { RegisterForm } from "@/entities/auth/ui/registerForm";
import { AuthWrapper } from "@/entities/auth/ui/authWrapper";

const RegisterPage = () => {
  return (
    <div className="space-y-2 w-full flex flex-col justify-center">
      <AuthWrapper>
        <RegisterForm />
      </AuthWrapper>
    </div>
  );
};

export default RegisterPage;
