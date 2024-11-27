// components/StandalonePageWithComponent.jsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  useEffect(() => {
    const handleMessage = (event) => {

      if (event.data.action === "navigate" && event.data.path) {
        navigate(event.data.path); 
      }
    };

    window.addEventListener("message", handleMessage);

    return () => {
      window.removeEventListener("message", handleMessage);
    };
  }, [navigate]);

  return (
    <div className="min-h-screen flex flex-col">
      <iframe
        src="/landing/index.html"
        className="w-full h-full border-none flex-1"
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
