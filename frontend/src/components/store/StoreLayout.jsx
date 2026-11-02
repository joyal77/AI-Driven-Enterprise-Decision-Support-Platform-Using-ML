import React from 'react';
import StoreNavbar from './StoreNavbar';

const StoreLayout = ({ children }) => {
  return (
    <div className="store-layout-root" style={{ minHeight: '100vh', backgroundColor: '#e3e6e6' }}>
      <StoreNavbar />
      <main className="store-layout-main" style={{ minHeight: 'calc(100vh - 120px)' }}>
        {children}
      </main>
    </div>
  );
};

export default StoreLayout;
