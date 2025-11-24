import { Form, FormField, FormItem } from "@/shared/ui/form/form";
import { FloatingLabelInput } from "@/shared/ui/input/floatingInputLabel";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  createInterviewSchema,
  CreateInterviewFormData,
} from "../lib/schemes/createInterviewSchema";
import { cn } from "@/shared/lib/mergeClass";
import { Button } from "@/shared/ui/button/button";
import { useState } from "react";
import { useCreateInterview } from "../hooks/useCreateInterview";
import { SkillsInput } from "./SkillsInput";

const questionOptions = [5, 10, 15, 20, 25, 30];

export const InterviewCreateForm = () => {
  const [currentAmountOfQuestions, setCurrentAmountOfQuestions] = useState(
    questionOptions[0]
  );

  const form = useForm<CreateInterviewFormData>({
    resolver: zodResolver(createInterviewSchema),
    defaultValues: {
      job_role_description: "",
      amount_of_tasks: currentAmountOfQuestions,
      key_skills: [],
      preferences: "",
    },
  });

  const {
    handleSubmit,
    formState: { errors },
  } = form;

  const {
    mutate: createInterviewMutation,
    isError,
    isPending,
    error,
  } = useCreateInterview();

  const onSubmit = async (interviewData: CreateInterviewFormData) => {
    createInterviewMutation(interviewData);
  };

  return (
    <div className="relative text-white flex items-center justify-center p-4">
      <div className="relative z-10 w-full max-w-3xl rounded-3xl p-8 py-12 space-y-8 text-center overflow-hidden">
        <h1 className="text-4xl font-extrabold mb-4 text-zinc-600">
          Создайте ваше интервью
        </h1>
        <p className="text-base text-gray-600 mx-auto mb-12">
          Укажите должность, добавьте ключевые навыки, пожелания и количество
          вопросов. После этого начнется собеседование. Удачи!
        </p>
        <Form {...form}>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <div className="text-left">
              <label
                htmlFor="jobRoleDescription"
                className="block text-gray-600 text-sm font-medium mb-2"
              >
                Должностная роль, отрасль или описание
              </label>
              <FormField
                control={form.control}
                name="job_role_description"
                render={({ field }) => (
                  <FormItem className="relative">
                    <FloatingLabelInput
                      {...field}
                      label="Введите здесь..."
                      labelClassName="text-zinc-600"
                      className={cn(
                        "py-2.5 bg-zinc-200 rounded-2xl border border-gray-300 text-zinc-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500",
                        errors.job_role_description && "border-red-500",
                        isPending && "opacity-70 cursor-not-allowed"
                      )}
                      disabled={isPending}
                    />
                    {errors.job_role_description && (
                      <p className="text-red-500 text-sm mt-1 text-left">
                        {errors.job_role_description.message}
                      </p>
                    )}
                  </FormItem>
                )}
              />
            </div>

            <div className="text-left">
              <label className="block text-gray-600 text-sm font-medium mb-2">
                Ключевые навыки
              </label>
              <FormField
                control={form.control}
                name="key_skills"
                render={({ field }) => (
                  <FormItem>
                    <SkillsInput
                      skills={field.value}
                      onChange={field.onChange}
                      maxSkills={5}
                      disabled={isPending}
                      error={errors.key_skills?.message}
                    />
                  </FormItem>
                )}
              />
            </div>

            <div className="text-left">
              <label
                htmlFor="preferences"
                className="block text-gray-600 text-sm font-medium mb-2"
              >
                Пожелания (необязательно)
              </label>
              <FormField
                control={form.control}
                name="preferences"
                render={({ field }) => (
                  <FormItem className="relative">
                    <FloatingLabelInput
                      {...field}
                      label="Введите ваши пожелания..."
                      labelClassName="text-zinc-600"
                      className={cn(
                        "py-2.5 bg-zinc-200 rounded-2xl border border-gray-300 text-zinc-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500",
                        errors.preferences && "border-red-500",
                        isPending && "opacity-70 cursor-not-allowed"
                      )}
                      disabled={isPending}
                    />
                    {errors.preferences && (
                      <p className="text-red-500 text-sm mt-1 text-left">
                        {errors.preferences.message}
                      </p>
                    )}
                  </FormItem>
                )}
              />
            </div>

            <div className="text-left">
              <label className="block text-gray-600 text-sm font-medium mb-2">
                Количество вопросов
              </label>
              <div className="flex flex-wrap gap-4 justify-center">
                {questionOptions.map((amount) => (
                  <Button
                    key={amount}
                    type="button"
                    onClick={() => {
                      setCurrentAmountOfQuestions(amount);
                      form.setValue("amount_of_tasks", amount);
                    }}
                    className={cn(
                      "rounded-2xl p-7 text-lg font-semibold cursor-pointer",
                      currentAmountOfQuestions === amount
                        ? "bg-blue-600/60 hover:bg-blue-700/60 text-white shadow-lg"
                        : "bg-zinc-200 hover:bg-zinc-300 text-gray-700 border border-gray-300",
                      isPending && "opacity-50 cursor-not-allowed"
                    )}
                    disabled={isPending}
                  >
                    {amount}
                  </Button>
                ))}
              </div>
              {isError && (
                <p className="text-red-500 text-sm mt-3 text-left">
                  Ошибка: {error?.message || "Неизвестная ошибка"}
                </p>
              )}
            </div>

            <Button
              size="lg"
              disabled={!form.formState.isValid || isPending}
              type="submit"
              className={cn(
                "mt-8 bg-blue-600/60 hover:bg-blue-700/60 text-white p-7 px-12 rounded-3xl cursor-pointer text-xl font-bold shadow-lg transition-all duration-200",
                (!form.formState.isValid || isPending) &&
                  "opacity-70 cursor-not-allowed"
              )}
            >
              {isPending ? "Создание..." : "Создать"}
            </Button>
          </form>
        </Form>
      </div>
    </div>
  );
};
