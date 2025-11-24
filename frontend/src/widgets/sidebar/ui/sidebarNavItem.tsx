import { cn } from "@/shared/lib/mergeClass";
import { NavLink } from "react-router-dom";
import { NavOption } from "../types/types";

interface SidebarNavItemProps {
  isExpanded: boolean;
  item: NavOption;
}

export const SidebarNavItem = ({ item, isExpanded }: SidebarNavItemProps) => {
  return (
    <NavLink
      to={item.path}
      className={({ isActive }) =>
        cn(
          "flex items-center rounded-lg py-2 transition-colors duration-200 overflow-hidden",
          isExpanded ? "px-3 justify-start" : "px-3 justify-center",
          isActive
            ? "bg-blue-200 text-blue-600"
            : "text-zinc-500 hover:bg-gray-100"
        )
      }
      title={item.label}
    >
      {({ isActive }) => (
        <>
          {" "}
          <item.icon
            className={cn(
              "h-5 w-5 flex-shrink-0",
              isActive ? "text-blue-600" : "text-zinc-500"
            )}
          />
          <span
            className={cn(
              "whitespace-nowrap text-sm font-medium pt-0.5",
              "transition-all duration-150 ease-linear",
              isExpanded ? "opacity-100 w-auto ml-3" : "opacity-0 w-0 ml-0"
            )}
          >
            {isExpanded && item.label}
          </span>
        </>
      )}
    </NavLink>
  );
};
