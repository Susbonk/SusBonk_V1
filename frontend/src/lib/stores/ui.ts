import { writable } from 'svelte/store';

export type TabType = 'dashboard' | 'logs' | 'settings';

export interface UIState {
  activeTab: TabType;
  showOnboarding: boolean;
}

const initialState: UIState = {
  activeTab: 'dashboard',
  showOnboarding: false
};

export const uiState = writable<UIState>(initialState);
