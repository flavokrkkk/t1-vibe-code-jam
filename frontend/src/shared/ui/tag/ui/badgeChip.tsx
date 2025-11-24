import { cn } from "@/shared/lib/mergeClass";
import { TagChipProps } from "../types/types";

export const TagChip: React.FC<TagChipProps> = ({
  children,
  variant = "glassLight",
  size = "sm",
  className,
}) => {
  const base = "rounded-full inline-flex items-center whitespace-nowrap";
  const sizeCls = {
    sm: "text-xs h-7 px-3",
    md: "text-sm h-8 px-4",
  }[size];

  const variantCls = {
    glassLight: "bg-indigo-500/50 text-white",
    solidDark: "bg-neutral-800 text-gray-300",
    outline: "borderborder-white/20 text-white",
  }[variant];

  return (
    <span className={cn(base, sizeCls, variantCls, className)}>{children}</span>
  );
};
