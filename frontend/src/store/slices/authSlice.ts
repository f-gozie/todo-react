import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
}

// Load initial state from localStorage
const loadTokensFromStorage = (): AuthState => {
  try {
    const accessToken = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');
    return { accessToken, refreshToken };
  } catch {
    return { accessToken: null, refreshToken: null };
  }
};

const initialState: AuthState = loadTokensFromStorage();

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setTokens(state: AuthState, action: PayloadAction<{ accessToken: string; refreshToken: string }>) {
      state.accessToken = action.payload.accessToken;
      state.refreshToken = action.payload.refreshToken;
      // Persist to localStorage
      localStorage.setItem('accessToken', action.payload.accessToken);
      localStorage.setItem('refreshToken', action.payload.refreshToken);
    },
    logout(state: AuthState) {
      state.accessToken = null;
      state.refreshToken = null;
      // Clear from localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    },
  },
});

export const { setTokens, logout } = authSlice.actions;
export default authSlice.reducer; 