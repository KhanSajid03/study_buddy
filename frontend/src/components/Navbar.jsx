import { Link, useNavigate } from 'react-router-dom';
import useStore from '../store/useStore';

function Navbar() {
  const { isAuthenticated, user, logout } = useStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>
          Study Buddy
        </Link>
      </div>
      <div className="navbar-menu">
        {isAuthenticated ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/settings">Settings</Link>
            <span>Hello, {user?.username}</span>
            <button onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
