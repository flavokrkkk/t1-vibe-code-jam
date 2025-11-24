import { X, Plus } from "lucide-react";
import { cn } from "@/shared/lib/mergeClass";
import React, { useCallback, useState, KeyboardEvent } from "react";

interface SkillsInputProps {
  skills: string[];
  onChange: (skills: string[]) => void;
  maxSkills?: number;
  disabled?: boolean;
  error?: string;
}

export const SkillsInput: React.FC<SkillsInputProps> = ({
  skills,
  onChange,
  maxSkills = 5,
  disabled = false,
  error,
}) => {
  const [inputValue, setInputValue] = useState("");

  const addSkill = useCallback(
    (skill: string) => {
      const trimmedSkill = skill.trim();
      if (
        !trimmedSkill ||
        skills.length >= maxSkills ||
        skills.includes(trimmedSkill)
      ) {
        return;
      }
      onChange([...skills, trimmedSkill]);
      setInputValue("");
    },
    [skills, maxSkills, onChange]
  );

  const removeSkill = useCallback(
    (index: number) => {
      onChange(skills.filter((_, i) => i !== index));
    },
    [skills, onChange]
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" || e.key === "+") {
        e.preventDefault();
        addSkill(inputValue);
      } else if (e.key === "Backspace" && !inputValue && skills.length > 0) {
        removeSkill(skills.length - 1);
      }
    },
    [inputValue, skills, addSkill, removeSkill]
  );

  const handleAddClick = useCallback(() => {
    addSkill(inputValue);
  }, [inputValue, addSkill]);

  return (
    <div className="space-y-2">
      <div
        className={cn(
          "min-h-[58px] bg-zinc-200 rounded-2xl border border-gray-300 p-2 px-3 flex flex-wrap gap-2 items-center",
          error && "border-red-500",
          disabled && "opacity-70 cursor-not-allowed"
        )}
      >
        {skills.map((skill, index) => (
          <span
            key={index}
            className="inline-flex items-center gap-1.5 bg-blue-600/60 text-white px-3 py-1.5 rounded-xl text-sm font-medium"
          >
            {skill}
            {!disabled && (
              <button
                type="button"
                onClick={() => removeSkill(index)}
                className="hover:bg-blue-700/60 rounded-full p-0.5 transition-colors"
                tabIndex={-1}
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </span>
        ))}
        {skills.length < maxSkills && (
          <div className="flex items-center gap-1 flex-1 min-w-[120px]">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={
                skills.length === 0
                  ? "Введите навык и нажмите Enter или +"
                  : "Добавить еще..."
              }
              className="flex-1 bg-transparent border-none outline-none text-zinc-800 placeholder:text-zinc-600 text-sm"
            />
            {inputValue.trim() && (
              <button
                type="button"
                onClick={handleAddClick}
                disabled={disabled}
                className="p-1 hover:bg-zinc-300 rounded-lg transition-colors disabled:opacity-50"
                tabIndex={-1}
              >
                <Plus className="h-4 w-4 text-zinc-700" />
              </button>
            )}
          </div>
        )}
      </div>
      {skills.length > 0 && (
        <p className="text-xs text-gray-500 text-left">
          Добавлено: {skills.length}/{maxSkills}
        </p>
      )}
      {error && <p className="text-red-500 text-sm mt-1 text-left">{error}</p>}
    </div>
  );
};
