import { Variants } from "framer-motion";
import {
  Zap,
  MessageSquare,
  Clock,
  FileText,
  TrendingUp,
  Users,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";

export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
};

export const cardVariants: Variants = {
  hidden: { opacity: 0, y: 30, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut",
    },
  },
  hover: {
    y: -8,
    scale: 1.02,
    transition: {
      duration: 0.3,
      ease: "easeOut",
    },
  },
};

export const imageVariants: Variants = {
  hidden: { opacity: 0, scale: 0.8, x: 50 },
  visible: {
    opacity: 1,
    scale: 1,
    x: 0,
    transition: {
      duration: 0.8,
      ease: "easeOut",
    },
  },
};

export const floatingVariants: Variants = {
  animate: {
    y: [0, -20, 0],
    transition: {
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

export interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

export const features: Feature[] = [
  {
    icon: FileText,
    title: "ИИ-интервьюер",
    description:
      "Автоматизированное собеседование с ИИ на основе Scibox LLM, которое генерирует адаптивные задачи и ведет естественный диалог",
  },
  {
    icon: Clock,
    title: "Браузерная IDE",
    description: "Полнофункциональная IDE с синтаксической подсветкой, автодополнением и безопасным выполнением кода в Docker",
  },
  {
    icon: MessageSquare,
    title: "Адаптивная сложность",
    description:
      "Система автоматически подстраивает сложность задач на основе уровня кандидата и качества решений",
  },
  {
    icon: TrendingUp,
    title: "Детальная аналитика",
    description:
      "Комплексные метрики, оценка качества кода и персонализированная обратная связь с разбором сильных и слабых сторон",
  },
];

export const benefits: string[] = [
  "Объективная оценка практических навыков",
  "Снижение стресса для кандидатов",
  "Масштабируемый процесс найма",
  "Система защиты от читерства",
  "Автоматизированное тестирование кода",
  "Детальные отчеты и метрики",
];

export interface Statistic {
  icon: LucideIcon;
  value: string;
  label: string;
}

export const statistics: Statistic[] = [
  {
    icon: Users,
    value: "1000+",
    label: "Активных пользователей",
  },
  {
    icon: Clock,
    value: "24/7",
    label: "Доступность сервиса",
  },
  {
    icon: Zap,
    value: "99.9%",
    label: "Надежность системы",
  },
];

export interface Testimonial {
  quote: string;
  author: string;
  role: string;
  avatar?: string;
}

export const testimonials: Testimonial[] = [
  {
    quote:
      "AI Copilot помог мне сократить время на обработку документов на 70%. Теперь я могу больше времени уделять клиентам и развитию бизнеса.",
    author: "Мария Иванова",
    role: "Владелец кофейни",
  },
  {
    quote:
      "Отличный помощник для малого бизнеса! Быстро получаю ответы на юридические и финансовые вопросы, не тратя время на поиск информации.",
    author: "Алексей Петров",
    role: "Директор салона красоты",
  },
  {
    quote:
      "Использую для создания контента и анализа данных. Сервис стал незаменимым инструментом в моей ежедневной работе.",
    author: "Елена Смирнова",
    role: "Предприниматель",
  },
];
