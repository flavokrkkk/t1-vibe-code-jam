import * as React from "react";
import { Input } from "./input";
import clsx from "clsx";
import { cn } from "@/shared/lib/mergeClass";

interface FloatingLabelInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  labelClassName?: string;
}

export const FloatingLabelInput = React.forwardRef<
  HTMLInputElement,
  FloatingLabelInputProps
>(({ label, labelClassName, className, ...props }, ref) => {
  const [isFocused, setIsFocused] = React.useState(false);
  const [hasValue, setHasValue] = React.useState(false);

  React.useEffect(() => {
    setHasValue(!!props.value);
  }, [props.value]);

  return (
    <div
      className={clsx(
        "relative border transition-colors duration-200 ease-in-out",
        className,
        isFocused && "border-blue-700"
      )}
    >
      <label
        className={cn(
          "absolute left-3 transition-all duration-200 pointer-events-none",
          isFocused || hasValue
            ? "top-[7px] text-[10px] text-gray-500"
            : "top-1/2 -translate-y-1/2 text-sm text-gray-400",
          labelClassName
        )}
      >
        {label}
      </label>
      <Input
        ref={ref}
        {...props}
        className={cn("pt-5 pb-2")}
        onFocus={(e) => {
          setIsFocused(true);
          props.onFocus?.(e);
        }}
        onBlur={(e) => {
          setIsFocused(false);
          props.onBlur?.(e);
        }}
        onChange={(e) => {
          setHasValue(!!e.target.value);
          props.onChange?.(e);
        }}
      />
    </div>
  );
});

FloatingLabelInput.displayName = "FloatingLabelInput";
