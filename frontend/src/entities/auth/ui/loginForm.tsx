import { useForm } from "react-hook-form";
import { LoginSchema, TypeLoginSchema } from "../lib/schemes/loginSchema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormField, FormItem } from "@/shared/ui/form/form";
import { FloatingLabelInput } from "@/shared/ui/input/floatingInputLabel";
import { CircleAlert, X } from "lucide-react";
import { Link } from "react-router-dom";
import { useLoginMutation } from "../hooks/useLogin";
import { cn } from "@/shared/lib/mergeClass";
import { Button } from "@/shared/ui/button/button";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const LoginForm = () => {
  const form = useForm<TypeLoginSchema>({
    resolver: zodResolver(LoginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const { mutate } = useLoginMutation();

  const {
    handleSubmit,
    reset,
    formState: { errors },
  } = form;

  const onSubmit = (data: TypeLoginSchema) => {
    mutate(data);
    reset();
  };

  return (
    <div className="space-y-2 flex flex-col w-full justify-center h-full bg-white p-6 md:p-10 rounded-3xl">
      <Form {...form}>
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="space-y-3 flex flex-col w-full h-full justify-between"
        >
          <section className="space-y-3">
            <h2 className="font-medium text-black text-lg text-center">
              C возвращением!
            </h2>
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem className="relative gap-1">
                  <FloatingLabelInput
                    {...field}
                    label="Почта"
                    className={cn(
                      "py-1.5 text-black bg-zinc-200 rounded-xl shadow-sm border-zinc-200",
                      errors.email && "border-red-700"
                    )}
                  />
                  {errors.email && (
                    <span className="text-red-800 text-xs px-3">
                      {errors.email.message}
                    </span>
                  )}
                  {field.value && !errors.email && (
                    <button
                      className="absolute right-4 top-4.5 text-blue-800 cursor-pointer"
                      onClick={() => field.onChange("")}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                  {errors.email && (
                    <button className="absolute right-4 top-4.5 text-red-800 cursor-pointer">
                      <CircleAlert className="w-4 h-4" />
                    </button>
                  )}
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem className="relative gap-1">
                  <FloatingLabelInput
                    {...field}
                    label="Пароль"
                    type="password"
                    className={cn(
                      "py-1.5 text-black bg-zinc-200 rounded-xl shadow-sm border-zinc-200",
                      errors.password && "border-red-700"
                    )}
                  />
                  {errors.password && (
                    <span className="text-red-800 text-xs px-3">
                      {errors.password.message}
                    </span>
                  )}
                  {field.value && !errors.password && (
                    <button
                      className="absolute right-4 top-4.5 text-blue-800 cursor-pointer"
                      onClick={() => field.onChange("")}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                  {errors.password && (
                    <button className="absolute right-4 top-4.5 text-red-800 cursor-pointer">
                      <CircleAlert className="w-4 h-4" />
                    </button>
                  )}
                </FormItem>
              )}
            />

            <Button
              type="submit"
              variant={"outline"}
              className="px-6 py-5 w-full bg-gradient-to-br from-[#7460e6] to-[#3361EC] text-white rounded-xl cursor-pointer hover:text-white"
            >
              Войти
            </Button>
          </section>
          <p className="text-black text-center text-sm">
            У меня нет аккаунта,{" "}
            <Link
              to={`/${ERouteNames.AUTH_ROUTE}/${ERouteNames.REGISTER_ROUTE}`}
              className="text-blue-600 cursor-pointer"
            >
              зарегестрироваться
            </Link>
          </p>
        </form>
      </Form>
    </div>
  );
};
