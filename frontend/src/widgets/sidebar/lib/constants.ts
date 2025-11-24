import { ERouteNames } from "@/shared/lib/routeVariables";
import {
  Building,
  ClipboardList,
  Cloud,
  HardDrive,
  Settings,
} from "lucide-react";

export const mainNavItems = [
  { icon: Cloud, label: "AI Мок-интервью", path: "/mock-interview" },
  {
    icon: ClipboardList,
    label: "История интервью",
    path: `/${ERouteNames.DASHBOARD_ROUTE}/${ERouteNames.INTERVIEW_HISTORY_ROUTE}`,
  },
];

export const betaFeaturesNavItems = [
  { icon: HardDrive, label: "Оценка резюме", path: "/cv-scorer" },
  {
    icon: Building,
    label: "Исследователь компаний",
    path: "/company-researcher",
  },
  { path: "/settings", label: "Настройки", icon: Settings },
];
