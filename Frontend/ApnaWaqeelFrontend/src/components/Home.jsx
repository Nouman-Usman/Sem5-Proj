// components/StandalonePageWithComponent.jsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleMessage = (event) => {
      // console.log("Message received from iframe:", event.data); // Debug: Check received message

      if (event.data.action === "navigate" && event.data.path) {
        // console.log("Navigating to:", event.data.path); // Debug: Confirm path
        navigate(event.data.path); // Navigate to specified path
      }
    };

    window.addEventListener("message", handleMessage);

    // Clean up the event listener on component unmount
    return () => {
      window.removeEventListener("message", handleMessage);
    };
  }, [navigate]);

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <iframe
        src="/landing/index.html"
        style={{ width: '100%', height: '100vh', border: 'none', flex: 1 }}
        title="Standalone Page"
      />
    </div>
  );
}

export default Home;


// import { useNavigate } from 'react-router-dom';
// import React, { useEffect, useState } from 'react';


// function Home() {
//   const [htmlContent, setHtmlContent] = useState('');

//   useEffect(() => {
//     // Fetch the HTML file from the public folder
//     fetch('/landing/index.html')
//       .then((response) => response.text())
//       .then((data) => setHtmlContent(data))
//       .catch((error) => console.error('Error loading HTML file:', error));
//   }, []);

//   return (
//     <div>
//       {/* Display the raw HTML content using dangerouslySetInnerHTML */}
//       <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
//     </div>
//   );
// };


// export default Home;
