import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';
import { FormField } from '../components/FormField/FormField';
import { PasswordField } from '../components/PasswordField/PasswordField';
import { AuthLayout } from '../layouts/AuthLayout';
import { mockAuthService } from '../services/authService';
import { MOCK_TAKEN_USERNAMES } from '../data/mockAuth';
import {
  getPasswordStrength,
  validateConfirmPassword,
  validateFullName,
  validateNewPassword,
  validateRegisterEmail,
  validateUsername,
} from '../utils/validation';
import './RegisterPage.css';

interface FieldErrors {
  fullName?: string;
  email?: string;
  username?: string;
  password?: string;
  confirmPassword?: string;
}

interface Touched {
  fullName?: boolean;
  email?: boolean;
  username?: boolean;
  password?: boolean;
  confirmPassword?: boolean;
}

const STRENGTH_LABEL: Record<string, string> = {
  weak: 'Weak',
  fair: 'Fair',
  strong: 'Strong',
};

/**
 * Feature 43 — Registration.
 *
 * Mirrors LoginPage's structure: local form state, derived validation on
 * every render, and a single mock service call on submit. All "account
 * creation" is handled by `mockAuthService.register` — no backend, no
 * session/token storage. On success, this screen shows a clear mock
 * confirmation instead of silently redirecting.
 */
export function RegisterPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [touched, setTouched] = useState<Touched>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | undefined>(undefined);
  const [successBalance, setSuccessBalance] = useState<number | undefined>(undefined);

  const errors: FieldErrors = {
    fullName: validateFullName(fullName),
    email: validateRegisterEmail(email),
    username: validateUsername(username, MOCK_TAKEN_USERNAMES),
    password: validateNewPassword(password),
    confirmPassword: validateConfirmPassword(password, confirmPassword),
  };
  const isValid = Object.values(errors).every((error) => !error);
  const strength = getPasswordStrength(password);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched({
      fullName: true,
      email: true,
      username: true,
      password: true,
      confirmPassword: true,
    });
    setFormError(undefined);

    if (!isValid || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    mockAuthService
      .register({ fullName, email, username, password })
      .then((result) => {
        if (result.ok) {
          setSuccessBalance(result.startingBalance);
          return;
        }
        setFormError(result.message);
      })
      .finally(() => {
        setIsSubmitting(false);
      });
  }

  if (successBalance !== undefined) {
    return (
      <AuthLayout title="Account created" description="Your account is ready to use.">
        <div className="register-success">
          <p className="register-success__message">
            Your account is ready. Your starting balance is{' '}
            <strong>BDT {successBalance.toLocaleString('en-US')}</strong>.
          </p>
          <p className="register-success__note">
            This is mock, display-only data for the current frontend — no real money or account
            was created.
          </p>
          <Button fullWidth onClick={() => navigate('/dashboard')}>
            Continue to dashboard
          </Button>
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout
      title="Create your account"
      description="Set up mock access to manage your money and transactions."
      footer={
        <span>
          Already have an account? <Link to="/login">Sign in</Link>
        </span>
      }
    >
      <form className="register-form" onSubmit={handleSubmit} noValidate>
        {formError && <ErrorMessage message={formError} />}

        <FormField
          label="Full name"
          type="text"
          name="fullName"
          autoComplete="name"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, fullName: true }))}
          error={touched.fullName ? errors.fullName : undefined}
          disabled={isSubmitting}
        />

        <FormField
          label="Email"
          type="email"
          name="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, email: true }))}
          error={touched.email ? errors.email : undefined}
          disabled={isSubmitting}
        />

        <FormField
          label="Username"
          type="text"
          name="username"
          autoComplete="username"
          hint="3–20 characters: letters, numbers, periods, and underscores."
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, username: true }))}
          error={touched.username ? errors.username : undefined}
          disabled={isSubmitting}
        />

        <div className="register-form__password-group">
          <PasswordField
            label="Password"
            name="password"
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, password: true }))}
            error={touched.password ? errors.password : undefined}
            disabled={isSubmitting}
          />
          {strength && (
            <div
              className={`password-strength password-strength--${strength}`}
              role="status"
              aria-live="polite"
            >
              <span className="password-strength__track">
                <span className="password-strength__fill" />
              </span>
              <span className="password-strength__label">
                Password strength: {STRENGTH_LABEL[strength]}
              </span>
            </div>
          )}
        </div>

        <PasswordField
          label="Confirm password"
          name="confirmPassword"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, confirmPassword: true }))}
          error={touched.confirmPassword ? errors.confirmPassword : undefined}
          disabled={isSubmitting}
        />

        <Button
          type="submit"
          fullWidth
          disabled={!isValid}
          isLoading={isSubmitting}
          loadingLabel="Creating account…"
        >
          Create account
        </Button>
      </form>
    </AuthLayout>
  );
}
