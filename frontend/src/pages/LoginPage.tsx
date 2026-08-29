import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/Button/Button';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';
import { FormField } from '../components/FormField/FormField';
import { PasswordField } from '../components/PasswordField/PasswordField';
import { AuthLayout } from '../layouts/AuthLayout';
import { authService } from '../services/authService';
import { validateLoginIdentifier, validateLoginPassword } from '../utils/validation';
import './LoginPage.css';

interface FieldErrors {
  identifier?: string;
  password?: string;
}

export function LoginPage() {
  const navigate = useNavigate();

  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [touched, setTouched] = useState<{ identifier?: boolean; password?: boolean }>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | undefined>(undefined);

  const errors: FieldErrors = {
    identifier: validateLoginIdentifier(identifier),
    password: validateLoginPassword(password),
  };
  const isValid = !errors.identifier && !errors.password;

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setTouched({ identifier: true, password: true });
    setFormError(undefined);

    if (!isValid || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    authService
      .login({ identifier, password })
      .then((result) => {
        if (result.ok) {
          navigate('/dashboard', { replace: true });
          return;
        }
        setFormError(result.message);
      })
      .finally(() => {
        setIsSubmitting(false);
      });
  }

  return (
    <AuthLayout
      title="Welcome back"
      description="Sign in to manage your money and transactions."
      footer={
        <span>
          Don&apos;t have an account? <Link to="/register">Create one</Link>
        </span>
      }
    >
      <form className="login-form" onSubmit={handleSubmit} noValidate>
        {formError && <ErrorMessage message={formError} />}

        <FormField
          label="Email, Username or Phone"
          type="text"
          name="identifier"
          autoComplete="username"
          value={identifier}
          onChange={(e) => setIdentifier(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, identifier: true }))}
          error={touched.identifier ? errors.identifier : undefined}
          disabled={isSubmitting}
        />

        <PasswordField
          label="Password"
          name="password"
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onBlur={() => setTouched((t) => ({ ...t, password: true }))}
          error={touched.password ? errors.password : undefined}
          disabled={isSubmitting}
        />

        <Button
          type="submit"
          fullWidth
          disabled={!isValid}
          isLoading={isSubmitting}
          loadingLabel="Signing in…"
        >
          Sign in
        </Button>
      </form>
    </AuthLayout>
  );
}
