import { Route, Routes } from 'react-router-dom';
import { DashboardPage } from '../pages/DashboardPage';
import { LoginPage } from '../pages/LoginPage';
import { PlaceholderPage } from '../pages/PlaceholderPage';
import { ProfilePage } from '../pages/ProfilePage';
import { RegisterPage } from '../pages/RegisterPage';
import { SelectRecipientPage } from '../pages/SelectRecipientPage';
import { SendMoneyPage } from '../pages/SendMoneyPage';
import { SplashPage } from '../pages/SplashPage';

/**
 * Top-level route table.
 *
 * Splash (41), Login (42), Register (43), Profile (4/54), and Dashboard
 * (5/44) have real UI. The Send Money flow (7/46, 8/45, 9, 10/47, 13, 48)
 * spans /send (recipient search) and /send/:userId (amount/note, review,
 * confirm, and result). Request Money and Transaction History remain
 * placeholders reserved for later groups.
 */
export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<SplashPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/profile" element={<ProfilePage />} />
      <Route path="/send" element={<SelectRecipientPage />} />
      <Route path="/send/:userId" element={<SendMoneyPage />} />
      <Route
        path="/request"
        element={
          <PlaceholderPage
            title="Request money coming soon"
            description="Requesting money from someone will live here."
          />
        }
      />
      <Route
        path="/transactions"
        element={
          <PlaceholderPage
            title="Transaction history coming soon"
            description="Your full transaction history will live here."
          />
        }
      />
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
