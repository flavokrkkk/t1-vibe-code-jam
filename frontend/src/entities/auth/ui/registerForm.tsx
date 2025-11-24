import { useForm } from "react-hook-form";
import {
  RegisterSchema,
  TypeRegisterSchema,
} from "../lib/schemes/registerSchema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Form, FormField, FormItem } from "@/shared/ui/form/form";
import { FloatingLabelInput } from "@/shared/ui/input/floatingInputLabel";
import { CircleAlert, X } from "lucide-react";
import { Link } from "react-router-dom";
import { useRegisterMutation } from "../hooks/useRegister";
import { cn } from "@/shared/lib/mergeClass";
import { Button } from "@/shared/ui/button/button";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const RegisterForm = () => {
  const form = useForm<TypeRegisterSchema>({
    resolver: zodResolver(RegisterSchema),
    defaultValues: {
      email: "",
      password: "",
      username: "",
    },
  });

  const { mutate } = useRegisterMutation();

  const {
    handleSubmit,
    reset,
    formState: { errors },
  } = form;

  const onSubmit = (authForm: TypeRegisterSchema) => {
    mutate({ ...authForm });
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
              Давай познакомимся!
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
              name="username"
              render={({ field }) => (
                <FormItem className="relative gap-1">
                  <FloatingLabelInput
                    {...field}
                    label={"ФИО"}
                    className={cn(
                      "py-1.5 text-black bg-zinc-200 rounded-xl shadow-sm border-zinc-200",
                      errors.username && "border-red-700"
                    )}
                  />
                  {errors.username && (
                    <span className="text-red-800 text-xs px-3">
                      {errors.username.message}
                    </span>
                  )}
                  {field.value && !errors.username && (
                    <button
                      className="absolute right-4 top-4.5 text-blue-800 cursor-pointer"
                      onClick={() => field.onChange("")}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                  {errors.username && (
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
              Зарегестрироваться
            </Button>
          </section>
          <p className="text-black text-center text-sm">
            У меня есть аккаунт,{" "}
            <Link
              to={`/${ERouteNames.AUTH_ROUTE}/${ERouteNames.LOGIN_ROUTE}`}
              className="text-blue-600 cursor-pointer"
            >
              войти
            </Link>
          </p>
        </form>
      </Form>
    </div>
  );
};
