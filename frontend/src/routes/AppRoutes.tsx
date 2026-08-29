import { Route, Routes } from 'react-router-dom';
import { DashboardPlaceholderPage } from '../pages/DashboardPlaceholderPage';
import { LoginPage } from '../pages/LoginPage';
import { PlaceholderPage } from '../pages/PlaceholderPage';
import { ProfilePage } from '../pages/ProfilePage';
import { RegisterPage } from '../pages/RegisterPage';
import { SplashPage } from '../pages/SplashPage';

/**
 * Top-level route table.
 *
 * Splash (41), Login (42), Register (43), and Profile (4/54) have real
 * UI. Dashboard is a placeholder reserved for Group B.
 */
export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<SplashPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard" element={<DashboardPlaceholderPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route
        path="*"
        element={
          <PlaceholderPage
            title="Page not found"
            description="The page you're looking for doesn't exist."
          />
        }
      />
    </Routes>
  );
}
