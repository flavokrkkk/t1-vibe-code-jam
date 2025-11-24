import Editor from "@monaco-editor/react";
import { Code, Expand } from "lucide-react";

interface CodeEditorProps {
  initialCode: string;
  language: string;
  onCodeChange: (newCode: string | undefined) => void;
  isMaximized: boolean;
  onToggleMaximize: () => void;
  editorHeight: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({
  initialCode,
  language,
  onCodeChange,
  isMaximized,
  onToggleMaximize,
  editorHeight,
}) => {
  return (
    <div
      className={`relative rounded-[22px] text-white bg-white shadow-lg overflow-hidden ${
        isMaximized ? "fixed inset-0 z-50" : ""
      }`}
      style={{ height: isMaximized ? "100vh" : editorHeight }}
    >
      <div className="flex justify-between items-center bg-[#3d66ff] transition-colors ease-in-out rounded-t-[22px] px-4 py-2">
        <div className="flex items-center gap-1">
          <button className={`flex items-center gap-1 text-sm`}>
            <Code size={16} />
            Код
          </button>
        </div>

        <div className="flex space-x-2">
          <button
            onClick={onToggleMaximize}
            className="p-1 rounded text-white hover:text-white transition-colors"
            title={isMaximized ? "Minimize" : "Maximize"}
          >
            <Expand size={18} />
          </button>
        </div>
      </div>

      <Editor
        height={isMaximized ? "calc(100vh - 48px)" : "calc(100% - 48px)"}
        language={language}
        defaultValue={initialCode}
        theme="vs-white"
        onChange={onCodeChange}
        options={{
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          fontSize: 14,
          wordWrap: "on",
        }}
        className="mt-1"
      />
    </div>
  );
};

export default CodeEditor;
