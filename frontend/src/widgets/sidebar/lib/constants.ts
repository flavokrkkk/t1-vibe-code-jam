import { ERouteNames } from "@/shared/lib/routeVariables";
import {
  Building,
  ClipboardList,
  BarChart,
  HardDrive,
  Settings,
} from "lucide-react";

export const mainNavItems = [
  {
    icon: BarChart,
    label: "Аналитика интервью",
    path: `/${ERouteNames.DASHBOARD_ROUTE}/analitics`,
  },
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
