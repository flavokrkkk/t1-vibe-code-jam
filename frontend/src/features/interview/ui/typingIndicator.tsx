import { motion } from "framer-motion";

export const TypingIndicator = () => {
  return (
    <div className="flex items-center gap-2 py-3 pl-1">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="w-2.5 h-2.5 rounded-full"
          animate={{
            backgroundColor: [
              "#60A5FA", // blue-400
              "#3B82F6", // blue-500
              "#2563EB", // blue-600
              "#1D4ED8", // blue-700
              "#60A5FA", // blue-400
            ],
            scale: [1, 1.4, 1],
            opacity: [0.6, 1, 0.6],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            delay: i * 0.3,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
};

