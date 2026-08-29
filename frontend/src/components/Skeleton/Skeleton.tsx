import type { CSSProperties } from 'react';
import './Skeleton.css';

interface SkeletonProps {
  width?: string;
  height?: string;
  radius?: string;
  className?: string;
}

/**
 * Generic loading placeholder block. Purely presentational and reused
 * anywhere a piece of real content (balance, a transaction row, ...) is
 * still loading — keeps layout stable instead of collapsing/reflowing.
 */
export function Skeleton({ width, height, radius, className }: SkeletonProps) {
  const style: CSSProperties = {
    width,
    height,
    borderRadius: radius,
  };

  return (
    <span
      className={`skeleton${className ? ` ${className}` : ''}`}
      style={style}
      aria-hidden="true"
    />
  );
}
