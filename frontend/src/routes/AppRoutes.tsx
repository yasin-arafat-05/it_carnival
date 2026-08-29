import { Route, Routes } from 'react-router-dom';
import { AdminDashboardPage } from '../pages/AdminDashboardPage';
import { DashboardPage } from '../pages/DashboardPage';
import { LoginPage } from '../pages/LoginPage';
import { PlaceholderPage } from '../pages/PlaceholderPage';
import { ProfilePage } from '../pages/ProfilePage';
import { RegisterPage } from '../pages/RegisterPage';
import { RequestMoneyPage } from '../pages/RequestMoneyPage';
import { SelectRecipientPage } from '../pages/SelectRecipientPage';
import { SendMoneyPage } from '../pages/SendMoneyPage';
import { SplashPage } from '../pages/SplashPage';
import { TransactionsPage } from '../pages/TransactionsPage';

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
      <Route path="/request" element={<RequestMoneyPage />} />
      <Route path="/transactions" element={<TransactionsPage />} />
      <Route path="/admin/dashboard" element={<AdminDashboardPage />} />
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
