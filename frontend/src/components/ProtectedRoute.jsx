import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  const userStr = localStorage.getItem('user');

  if (!userStr) {
    return <Navigate to="/login?error=admin_required" replace />;
  }

  try {
    const user = JSON.parse(userStr);
    if (!user || user.role !== 'admin') {
      return <Navigate to="/login?error=admin_required" replace />;
    }
  } catch (e) {
    return <Navigate to="/login?error=admin_required" replace />;
  }

  return children;
};

export default ProtectedRoute;