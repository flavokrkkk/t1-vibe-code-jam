import { Button } from "@/shared/ui/button/button";
import React from "react";

interface SuggestionsPanelProps {
  suggestions: string[];
  onSelectSuggestion: (suggestion: string) => void;
  isDisabled: boolean;
}

export const SuggestionsPanel: React.FC<SuggestionsPanelProps> = ({
  suggestions,
  onSelectSuggestion,
  isDisabled,
}) => {
  if (suggestions.length === 0) {
    return null;
  }

  return (
    <div className="p-4 grid grid-cols-2 gap-3 bg-transparent w-full max-w-[800px]">
      {suggestions.map((suggestion, index) => (
        <Button
          key={index}
          variant="outline"
          className="h-auto text-sm py-3 text-left justify-start whitespace-normal text-white bg-blue-500 transition-colors ease-in-out rounded-lg cursor-pointer hover:border-blue-400"
          onClick={() => onSelectSuggestion(suggestion)}
          disabled={isDisabled}
        >
          {suggestion}
        </Button>
      ))}
    </div>
  );
};
