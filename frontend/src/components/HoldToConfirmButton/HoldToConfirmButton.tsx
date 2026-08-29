import React, { useState, useRef, useEffect, useCallback } from 'react';
import './HoldToConfirmButton.css';

interface HoldToConfirmButtonProps {
  onConfirm: () => void;
  durationMs?: number; // Default 5000ms (5 seconds)
  disabled?: boolean;
  isSubmitting?: boolean;
}

export function HoldToConfirmButton({
  onConfirm,
  durationMs = 5000,
  disabled = false,
  isSubmitting = false,
}: HoldToConfirmButtonProps) {
  const [isHolding, setIsHolding] = useState(false);
  const [progress, setProgress] = useState(0); // 0 to 100%
  const [secondsRemaining, setSecondsRemaining] = useState(Math.ceil(durationMs / 1000));

  const animationFrameRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const isTriggeredRef = useRef(false);

  const reset = useCallback(() => {
    setIsHolding(false);
    setProgress(0);
    setSecondsRemaining(Math.ceil(durationMs / 1000));
    startTimeRef.current = null;
    isTriggeredRef.current = false;

    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, [durationMs]);

  const updateProgress = useCallback(() => {
    if (!startTimeRef.current || isTriggeredRef.current) return;

    const now = Date.now();
    const elapsed = now - startTimeRef.current;
    const currentProgress = Math.min(100, (elapsed / durationMs) * 100);
    const remainingSecs = Math.max(0, Math.ceil((durationMs - elapsed) / 1000));

    setProgress(currentProgress);
    setSecondsRemaining(remainingSecs);

    if (elapsed >= durationMs) {
      isTriggeredRef.current = true;
      setIsHolding(false);
      setProgress(100);
      onConfirm();
    } else {
      animationFrameRef.current = requestAnimationFrame(updateProgress);
    }
  }, [durationMs, onConfirm]);

  const startHold = (e: React.MouseEvent | React.TouchEvent) => {
    if (disabled || isSubmitting || isTriggeredRef.current) return;
    // Prevent default touch scrolling behavior on button press
    if ('touches' in e && e.cancelable) {
      // e.preventDefault();
    }

    setIsHolding(true);
    startTimeRef.current = Date.now();
    isTriggeredRef.current = false;
    animationFrameRef.current = requestAnimationFrame(updateProgress);
  };

  const endHold = () => {
    if (!isTriggeredRef.current) {
      reset();
    }
  };

  useEffect(() => {
    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return (
    <div className="hold-button-container">
      <button
        type="button"
        className={`hold-to-confirm-btn ${isHolding ? 'holding' : ''} ${disabled || isSubmitting ? 'disabled' : ''}`}
        onMouseDown={startHold}
        onMouseUp={endHold}
        onMouseLeave={endHold}
        onTouchStart={startHold}
        onTouchEnd={endHold}
        onTouchCancel={endHold}
        disabled={disabled || isSubmitting}
      >
        <div
          className="hold-to-confirm-btn__progress"
          style={{ width: `${progress}%` }}
        />
        <span className="hold-to-confirm-btn__text">
          {isSubmitting ? (
            'Sending transfer…'
          ) : isHolding ? (
            `Hold for ${secondsRemaining}s to Confirm`
          ) : (
            `Press & Hold to Confirm (${Math.ceil(durationMs / 1000)}s)`
          )}
        </span>
      </button>

      {isHolding && (
        <div className="hold-hint">
          Keep pressing until the bar fills ({Math.round(progress)}%)
        </div>
      )}
    </div>
  );
}
