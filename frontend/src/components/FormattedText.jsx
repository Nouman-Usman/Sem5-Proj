import React from 'react';

const FormattedText = ({ text }) => {
  const formatText = (text) => {
    // Split the text into paragraphs and list items
    const paragraphs = text.split('\n\n');
    return paragraphs.map((paragraph, index) => {
      if (paragraph.match(/^\d+\./)) {
        const listItems = paragraph.split('\n').map((item, idx) => (
          <li key={idx}>{formatBoldText(item.replace(/^\d+\.\s*/, ''))}</li>
        ));
        return <ul className="list-disc list-inside mb-2" key={index}>{listItems}</ul>;
      }
      return <p className="mb-2" key={index}>{formatBoldText(paragraph)}</p>;
    });
  };

  const formatBoldText = (text) => {
    const parts = text.split(/(".*?")/g); // Split by text enclosed in double quotes
    return parts.map((part, index) => {
      if (part.startsWith('"') && part.endsWith('"')) {
        return <strong key={index}>{part.slice(1, -1)}</strong>; // Remove the quotes
      }
      return part;
    });
  };

  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-md dark:bg-gray-800 dark:border-gray-700">
      {formatText(text)}
    </div>
  );
};

export default FormattedText;