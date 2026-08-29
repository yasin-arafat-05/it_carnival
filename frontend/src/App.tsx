import { BrowserRouter } from 'react-router-dom';
import { AppRoutes } from './routes/AppRoutes';
import { FloatingChatWidget } from './components/FloatingChatWidget/FloatingChatWidget';

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
      <FloatingChatWidget />
    </BrowserRouter>
  );
}

export default App;
