import { interviewActions } from "@/entities/interview/model/store/interviewSlice";
import { bindActionCreators } from "@reduxjs/toolkit";
import { useDispatch } from "react-redux";

export const useActions = () => {
  const dispatch = useDispatch();

  return bindActionCreators({ ...interviewActions }, dispatch);
};
