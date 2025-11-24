import { createRoot } from "react-dom/client";
import "@shared/styles/index.css";
import { App } from "./app";

createRoot(document.getElementById("root")!).render(<App />);
