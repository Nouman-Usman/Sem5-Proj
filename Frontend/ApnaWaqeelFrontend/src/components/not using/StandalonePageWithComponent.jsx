// components/StandalonePageWithComponent.jsx
import React from 'react';

function StandalonePageWithComponent() {
  return (
    <div>
      <iframe 
        src="/landing/index.html" 
        style={{ width: '100%', height: '500px', border: 'none' }}
        title="Standalone Page"
      />
    </div>
  );
}

export default StandalonePageWithComponent;
