const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

const primaryDir = path.join(__dirname, 'dist', 'appointocore-frontend', 'browser');
const fallbackDir = path.join(__dirname, 'dist', 'appointocare-frontend', 'browser');
const targetDir = fs.existsSync(primaryDir) ? primaryDir : fallbackDir;

function compressDirectory(dir) {
  if (!fs.existsSync(dir)) {
    console.log(`Directory ${dir} does not exist. Skipping pre-compression.`);
    return;
  }

  const entries = fs.readdirSync(dir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      compressDirectory(fullPath);
    } else if (entry.isFile()) {
      const ext = path.extname(entry.name).toLowerCase();
      if (['.js', '.css', '.html', '.svg', '.json', '.txt', '.ico'].includes(ext) && !entry.name.endsWith('.gz')) {
        const fileContent = fs.readFileSync(fullPath);
        if (fileContent.length >= 256) {
          const compressed = zlib.gzipSync(fileContent, { level: 9 });
          fs.writeFileSync(`${fullPath}.gz`, compressed);
          const originalKb = (fileContent.length / 1024).toFixed(1);
          const compressedKb = (compressed.length / 1024).toFixed(1);
          console.log(`Gzipped: ${entry.name} (${originalKb} KB -> ${compressedKb} KB)`);
        }
      }
    }
  }
}

console.log('Pre-compressing assets in dist/appointocare-frontend/browser...');
compressDirectory(targetDir);
console.log('Gzip pre-compression complete.');
