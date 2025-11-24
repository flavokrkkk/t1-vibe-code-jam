import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { InterviewSliceState } from "../types/types";

const initialState: InterviewSliceState = {
  currentQuestionIndex: 0,
};

export const interviewSlice = createSlice({
  name: "interview-slice",
  initialState,
  selectors: {},
  reducers: (create) => ({
    setCurrentQuestionIndex: create.reducer(
      (state, action: PayloadAction<number>) => {
        state.currentQuestionIndex = action.payload;
      }
    ),
  }),
});

export const interviewActions = interviewSlice.actions;
export const interviewSelectors = interviewSlice.selectors;
