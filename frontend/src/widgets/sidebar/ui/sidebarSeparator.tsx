import { cn } from "@/shared/lib/mergeClass";

export const SidebarSeparator = ({ isExpanded }: { isExpanded: boolean }) => {
  return (
    <div
      className={cn(
        "mx-auto h-[1px] bg-gray-200",
        isExpanded ? "w-[calc(100%-1.5rem)]" : "w-[calc(100%-1.5rem)]"
      )}
    ></div>
  );
};
