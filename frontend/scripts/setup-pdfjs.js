import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const copyPdfWorker = () => {
  const sourceFile = path.resolve(__dirname, '../node_modules/pdfjs-dist/build/pdf.worker.min.js');
  const targetDir = path.resolve(__dirname, '../public/pdfjs');
  const targetFile = path.resolve(targetDir, 'pdf.worker.min.js');

  if (!fs.existsSync(targetDir)) {
    fs.mkdirSync(targetDir, { recursive: true });
  }

  // Read and write with explicit encoding
  const content = fs.readFileSync(sourceFile, 'utf8');
  fs.writeFileSync(targetFile, content, { encoding: 'utf8' });
  
  console.log('PDF.js worker file copied successfully');
};

try {
  copyPdfWorker();
} catch (error) {
  console.error('Error copying PDF worker:', error);
  process.exit(1);
}
