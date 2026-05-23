import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import LiveData from './pages/LiveData';
import Analytics from './pages/Analytics';
import DataCapture from './pages/DataCapture';
import LandingPage from './pages/LandingPage';

const DashboardLayout = () => {
  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<Login />} />
        
        <Route element={<DashboardLayout />}>
          <Route path="/live-data" element={<LiveData />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/data-capture" element={<DataCapture />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
