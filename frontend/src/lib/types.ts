// Shared types
export type TabType = 'dashboard' | 'logs' | 'settings';
export type StrengthLevel = 'Chill' | 'Normal' | 'Bonkers';

// Design tokens
export const colors = {
  primary: '#CCFF00',      // Lime green - active states
  secondary: '#FF8A00',    // Orange - CTAs
  black: '#000000',
  white: '#FFFFFF',
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
  },
  hover: {
    primary: '#d9ff33',
    secondary: '#ff9f2e',
    item: '#fff9e6',
  }
} as const;
