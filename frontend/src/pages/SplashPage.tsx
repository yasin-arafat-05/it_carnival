import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Logo } from '../components/Brand/Logo';
import { LoadingIndicator } from '../components/LoadingIndicator/LoadingIndicator';
import { checkSession } from '../services/appInitService';
import './SplashPage.css';

/**
 * Feature 41 — Splash / App Entry.
 *
 * Full-viewport entry screen shown while the app performs its (currently
 * mocked) session check, then routes the user to Login or Dashboard.
 * All initialization/session logic lives in `appInitService`; this
 * component only reacts to its result.
 */
export function SplashPage() {
  const navigate = useNavigate();
  const [failed, setFailed] = useState(false);

  // Avoid a state update / navigation after the component has unmounted
  // if the user somehow navigates away mid-check.
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;

    checkSession()
      .then((result) => {
        if (!isMounted.current) return;
        navigate(result.status === 'authenticated' ? '/dashboard' : '/login', {
          replace: true,
        });
      })
      .catch(() => {
        if (!isMounted.current) return;
        setFailed(true);
      });

    return () => {
      isMounted.current = false;
    };
  }, [navigate]);

  return (
    <main className="splash">
      <div className="splash__content">
        <Logo size={64} />
        <p className="splash__tagline">Making everyday transactions simple.</p>

        <div className="splash__status">
          {failed ? (
            <p className="splash__error" role="alert">
              Something went wrong while starting the app. Please refresh to try again.
            </p>
          ) : (
            <LoadingIndicator label="Getting things ready…" />
          )}
        </div>
      </div>
    </main>
  );
}
