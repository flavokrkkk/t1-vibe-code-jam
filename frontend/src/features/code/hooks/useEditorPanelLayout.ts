import { useState, useMemo, useCallback } from "react";

export enum EditorPanelHeights {
  Folded = "48px",
  MaximizedEditor = "100%",
  Hidden = "0px",
  Split = "50%",
}

interface EditorPanelLayout {
  isCodeEditorMaximized: boolean;
  isTestPanelFolded: boolean;
  editorHeight: string;
  testPanelHeight: string;
  handleToggleMaximizeEditor: () => void;
  handleToggleFoldTestPanel: () => void;
}

export const useEditorPanelLayout = (): EditorPanelLayout => {
  const [isCodeEditorMaximized, setIsCodeEditorMaximized] =
    useState<boolean>(false);
  const [isTestPanelFolded, setIsTestPanelFolded] = useState<boolean>(false);

  const handleToggleMaximizeEditor = useCallback(() => {
    setIsCodeEditorMaximized((prev) => !prev);
    if (!isCodeEditorMaximized) {
      setIsTestPanelFolded(true);
    }
  }, [isCodeEditorMaximized]);

  const handleToggleFoldTestPanel = useCallback(() => {
    setIsTestPanelFolded((prev) => !prev);
    if (isCodeEditorMaximized) {
      setIsCodeEditorMaximized(false);
    }
  }, [isCodeEditorMaximized]);

  const { editorHeight, testPanelHeight } = useMemo(() => {
    const foldedHeight = EditorPanelHeights.Folded;

    const currentEditorHeight = isCodeEditorMaximized
      ? EditorPanelHeights.MaximizedEditor
      : isTestPanelFolded
      ? `calc(${EditorPanelHeights.MaximizedEditor} - ${foldedHeight})`
      : EditorPanelHeights.Split;

    const currentTestPanelHeight = isCodeEditorMaximized
      ? EditorPanelHeights.Hidden
      : isTestPanelFolded
      ? foldedHeight
      : EditorPanelHeights.Split;

    return {
      editorHeight: currentEditorHeight,
      testPanelHeight: currentTestPanelHeight,
    };
  }, [isCodeEditorMaximized, isTestPanelFolded]);

  return {
    isCodeEditorMaximized,
    isTestPanelFolded,
    editorHeight,
    testPanelHeight,
    handleToggleMaximizeEditor,
    handleToggleFoldTestPanel,
  };
};
