import { writable } from 'svelte/store';

export interface AppState {
  isActive: boolean;
  bonkCount: number;
  groups: string[];
  activeGroup: string;
  isPlaying: boolean;
}

const initialState: AppState = {
  isActive: false,
  bonkCount: 1284,
  groups: ["Solana Degens", "SafeMoon Army", "Bitcoin Maxis"],
  activeGroup: "Solana Degens",
  isPlaying: true
};

export const appState = writable<AppState>(initialState);

// Helper functions
export const summonBot = () => {
  appState.update(state => ({ ...state, isActive: true }));
};

export const stopBot = () => {
  appState.update(state => ({ ...state, isActive: false }));
};

export const togglePlayPause = () => {
  appState.update(state => ({ ...state, isPlaying: !state.isPlaying }));
};

export const changeGroup = (group: string) => {
  if (group === "add_new") {
    appState.update(state => ({ ...state, isActive: false }));
  } else {
    appState.update(state => ({ ...state, activeGroup: group }));
  }
};

export const incrementBonkCount = () => {
  appState.update(state => ({ ...state, bonkCount: state.bonkCount + 1 }));
};