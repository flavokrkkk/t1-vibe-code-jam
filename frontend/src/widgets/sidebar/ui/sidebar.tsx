import { useState, useCallback } from "react";
import { Link, NavLink } from "react-router-dom";
import { cn } from "@/shared/lib/mergeClass";
import { SidebarNavItem } from "./sidebarNavItem";
import { SidebarSeparator } from "./sidebarSeparator";
import { Image } from "@/shared/ui/image/image";
import { betaFeaturesNavItems, mainNavItems } from "../lib/constants";
import { Avatar, AvatarFallback, AvatarImage } from "@/shared/ui/avatar/avatar";
import { ERouteNames } from "@/shared/lib/routeVariables";

export const Sidebar = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  const handleMouseEnter = useCallback(() => {
    setIsExpanded(true);
  }, []);

  const handleMouseLeave = useCallback(() => {
    setIsExpanded(false);
  }, []);

  return (
    <div
      className={cn(
        "flex h-screen flex-col justify-between relative border-r rounded-r-2xl space-y-2 border-gray-200 bg-white shadow-md transition-[width] duration-200 ease-linear overflow-hidden",
        isExpanded ? "w-64" : "w-16"
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div
        className={cn(
          "flex items-center justify-center pt-4 pb-2",
          isExpanded ? "px-4 justify-start" : "px-0"
        )}
      >
        <NavLink
          to="/"
          className={cn(
            "flex items-center text-gray-900",
            isExpanded ? "justify-start" : "justify-center w-full"
          )}
        >
          <Image
            alt="logo-suspese"
            src="/images/logo.jpg"
            className="w-10 h-10 rounded-lg"
          />
          {isExpanded && (
            <span
              className={cn(
                "whitespace-nowrap text-xl font-bold",
                "transition-all duration-150 ease-linear",
                isExpanded ? "opacity-100 w-auto ml-3" : "opacity-0 w-0 ml-0"
              )}
            >
              T1 Course
            </span>
          )}
        </NavLink>
      </div>
      <SidebarSeparator isExpanded={isExpanded} />

      <div className="flex flex-grow flex-col justify-start space-y-2 py-2">
        <nav className="flex flex-col space-y-1 px-3">
          {mainNavItems.map((item) => (
            <SidebarNavItem
              key={item.path}
              item={item}
              isExpanded={isExpanded}
            />
          ))}
        </nav>

        <SidebarSeparator isExpanded={isExpanded} />

        <nav className="flex flex-col space-y-1 px-3">
          {betaFeaturesNavItems.map((item) => (
            <SidebarNavItem
              key={item.path}
              item={item}
              isExpanded={isExpanded}
            />
          ))}
        </nav>
      </div>
      <Link to={`/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.PROFILE_ROUTE}`}>
        <div className="px-4 -space-x-1 absolute bottom-0 w-full bg-white flex items-center h-16 rounded-lg cursor-pointer">
          <Avatar>
            <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
            <AvatarFallback>CN</AvatarFallback>
          </Avatar>

          <div
            className={cn(
              "whitespace-nowrap text-sm font-medium flex flex-col justify-center pb-1.5",
              "transition-all duration-150 ease-linear",
              isExpanded ? "opacity-100 w-auto ml-3" : "opacity-0 w-0 ml-0"
            )}
          >
            <span>Егор</span>
            <p className="text-xs text-zinc-500 leading-2 ">
              Frontend Developer
            </p>
          </div>
        </div>
      </Link>
    </div>
  );
};
