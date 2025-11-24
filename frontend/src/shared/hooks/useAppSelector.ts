import { useSelector } from "react-redux";
import { RootState } from "../lib/store";

export const useAppSelector = useSelector.withTypes<RootState>();
