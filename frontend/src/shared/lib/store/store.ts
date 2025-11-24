import { interviewSlice } from "@/entities/interview/model/store/interviewSlice";
import {
  combineSlices,
  configureStore,
  ThunkAction,
  UnknownAction,
} from "@reduxjs/toolkit";

export const rootReducer = combineSlices(interviewSlice);

export const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;

export type AppDispatch = typeof store.dispatch;

export type AppThunk<R = void> = ThunkAction<
  R,
  RootState,
  unknown,
  UnknownAction
>;
