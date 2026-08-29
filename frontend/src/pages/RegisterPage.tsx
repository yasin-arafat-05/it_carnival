import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';
import { FormField } from '../components/FormField/FormField';
import { PasswordField } from '../components/PasswordField/PasswordField';
import { AuthLayout } from '../layouts/AuthLayout';
import { authService } from '../services/authService';
import {
  getPasswordStrength,
  validateConfirmPassword,
  validateFullName,
  validateNewPassword,
  validateRegisterEmail,
} from '../utils/validation';
import './RegisterPage.css';

interface FieldErrors {
  fullName?: string;
  email?: string;
  username?: string;
  phoneNumber?: string;
  password?: string;
  confirmPassword?: string;
}

interface Touched {
  fullName?: boolean;
  email?: boolean;
  username?: boolean;
  phoneNumber?: boolean;
  password?: boolean;
  confirmPassword?: boolean;
}

const STRENGTH_LABEL: Record<string, string> = {
  weak: 'Weak',
  fair: 'Fair',
  strong: 'Strong',
};

export function RegisterPage() {
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [touched, setTouched] = useState<Touched>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | undefined>(undefined);
  const [successBalance, setSuccessBalance] = useState<number | undefined>(undefined);

  const errors: FieldErrors = {
    fullName: validateFullName(fullName),
    email: validateRegisterEmail(email),
    username: username.length < 3 ? 'Username must be at least 3 characters' : undefined,
    phoneNumber: phoneNumber && phoneNumber.length < 10 ? 'Phone number must be at least 10 digits' : undefined,
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
      phoneNumber: true,
      password: true,
      confirmPassword: true,
    });
    setFormError(undefined);

    if (!isValid || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    authService
      .register({ fullName, email, username, password, phoneNumber } as any)
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
      <AuthLayout title="Account created" description="Your digital wallet account is ready to use.">
        <div className="register-success">
          <p className="register-success__message">
            Your account is ready. Your starting balance is{' '}
            <strong>BDT {successBalance.toLocaleString('en-US')}</strong>.
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
      title="Create account"
      description="Enter your details to register your digital wallet."
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
          hint="Letters, numbers, and underscores (e.g. yasin_arafat_05)"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, username: true }))}
          error={touched.username ? errors.username : undefined}
          disabled={isSubmitting}
        />

        <FormField
          label="Phone number"
          type="tel"
          name="phoneNumber"
          autoComplete="tel"
          hint="e.g. 01700000000"
          value={phoneNumber}
          onChange={(e) => setPhoneNumber(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, phoneNumber: true }))}
          error={touched.phoneNumber ? errors.phoneNumber : undefined}
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

          {password.length > 0 && (
            <div className="register-form__strength">
              <div
                className={`register-form__strength-bar register-form__strength-bar--${strength}`}
              />
              <span className="register-form__strength-text">
                Strength: {STRENGTH_LABEL[strength || 'weak'] || 'Weak'}
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

        <Button type="submit" fullWidth isLoading={isSubmitting}>
          Create account
        </Button>
      </form>
    </AuthLayout>
  );
}
