import React from "react";

type P = { readonly size?: number; readonly color?: string };

export const ShirtIcon: React.FC<P> = ({ size = 96, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
    <path
      d="M22 8l-14 8 6 12 6-3v31h24V25l6 3 6-12-14-8c-1 4-5 7-10 7s-9-3-10-7z"
      stroke={color}
      strokeWidth={4}
      strokeLinejoin="round"
    />
  </svg>
);

export const TvIcon: React.FC<P> = ({ size = 96, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
    <rect x={6} y={12} width={52} height={34} rx={4} stroke={color} strokeWidth={4} />
    <path d="M22 56h20M32 46v10" stroke={color} strokeWidth={4} strokeLinecap="round" />
  </svg>
);

export const SofaIcon: React.FC<P> = ({ size = 96, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
    <path
      d="M12 30v-8a6 6 0 016-6h28a6 6 0 016 6v8M6 32a5 5 0 0110 0v6h32v-6a5 5 0 0110 0v14H6V32zM12 46v6M52 46v6"
      stroke={color}
      strokeWidth={4}
      strokeLinejoin="round"
      strokeLinecap="round"
    />
  </svg>
);

export const CheckIcon: React.FC<P> = ({ size = 48, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
    <path d="M10 25l9 9 19-20" stroke={color} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const CrossIcon: React.FC<P> = ({ size = 48, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
    <path d="M13 13l22 22M35 13L13 35" stroke={color} strokeWidth={6} strokeLinecap="round" />
  </svg>
);

export const SearchIcon: React.FC<P> = ({ size = 40, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 48 48" fill="none">
    <circle cx={21} cy={21} r={13} stroke={color} strokeWidth={5} />
    <path d="M31 31l10 10" stroke={color} strokeWidth={5} strokeLinecap="round" />
  </svg>
);

export const BookIcon: React.FC<P> = ({ size = 64, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 64 64" fill="none">
    <path
      d="M32 16c-6-5-14-6-24-5v38c10-1 18 0 24 5 6-5 14-6 24-5V11c-10-1-18 0-24 5zM32 16v38"
      stroke={color}
      strokeWidth={4}
      strokeLinejoin="round"
    />
  </svg>
);
