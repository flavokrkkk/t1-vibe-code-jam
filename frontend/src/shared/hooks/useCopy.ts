import { useState, useTransition } from "react";

export const useCopied = () => {
  const [isCopied, setIsCopied] = useState(false);
  const [isPending, startTransition] = useTransition();

  const handleCopyClick = async (
    event: React.MouseEvent<HTMLButtonElement>
  ) => {
    startTransition(async () => {
      try {
        const textToCopy = event.currentTarget.value;
        if (!textToCopy) throw new Error("Is empty copy value!");

        if (navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(textToCopy);
        } else {
          const textarea = document.createElement("textarea");
          textarea.value = textToCopy;
          document.body.appendChild(textarea);
          textarea.select();
          document.execCommand("copy");
          document.body.removeChild(textarea);
        }

        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
      } catch (err) {
        console.error("Ошибка при копировании текста:", err);
        setIsCopied(false);
      }
    });
  };

  return {
    isCopied,
    isPending,
    handleCopyClick,
  };
};
