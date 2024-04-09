// (env) arjuncode@Arjuns-MacBook-Air news-backend % rm output.html                 
// (env) arjuncode@Arjuns-MacBook-Air news-backend % rm SAMPLE.mjml                 
// (env) arjuncode@Arjuns-MacBook-Air news-backend % node json_to_mjml.js SAMPLE.json
// MJML file "SAMPLE.mjml" has been created.
// (env) arjuncode@Arjuns-MacBook-Air news-backend % mjml SAMPLE.mjml -o output.html 

// (env) arjuncode@Arjuns-MacBook-Air news-backend % open output.html  

import fs from 'fs';
import path from 'path';

// Get the filename from the command-line argument
const jsonFilename = process.argv[2];

// Read the JSON data from the file
const jsonData = JSON.parse(fs.readFileSync(jsonFilename, 'utf8'));

// Function to find the source link based on the source name
const findSourceLink = (sources, sourceName) => {
  const source = sources.find(([name]) => name === sourceName);
  return source ? source[1] : null;
};

// Generate the MJML content
const generateMJML = (data) => {
  const { 'Top Headlines': topHeadlines, 'Custom Headlines': customHeadlines, 'Trending Headlines': trendingHeadlines } = data;

  const mjmlContent = `
    <mjml>
      <mj-head>
        <mj-font name="Georgia" href="https://fonts.googleapis.com/css2?family=Georgia" />
        <mj-attributes>
          <mj-all font-family="Georgia, serif" />
          <mj-text font-size="16px" color="#000000" />
          <mj-section background-color="#ffffff" padding="20px" />
          <mj-class name="headline-box" background-color="#1a237e" color="#000000" font-size="24px" font-weight="bold" padding="15px" border-radius="5px" />
          <mj-class name="headline-text" color="#000000" />
          <mj-class name="summary" color="#000000" font-size="16px" line-height="1.5" />
          <mj-class name="divider" border-color="#cccccc" border-width="1px" />
          <mj-class name="source-link" color="#000000" font-size="14px" text-decoration="underline" />
        </mj-attributes>
        <mj-style inline="inline">
          .headline-box {
            margin-bottom: 20px;
          }
          .summary {
            margin-bottom: 20px;
          }
          .image {
            margin-bottom: 30px;
          }
          a, a:visited, a:hover, a:active {
            color: #000000 !important; /* Make sure all links are black */
          }
        </mj-style>
      </mj-head>
      <mj-body background-color="#f4f4f4">
        <mj-section background-color="#1a237e" padding="20px">
          <mj-column>
            <mj-text align="center" color="#ffffff" font-size="48px" font-weight="bold" font-family="Georgia, serif">Briefed</mj-text>
          </mj-column>
        </mj-section>
        <mj-section padding="0">
          <mj-column>
            <mj-divider mj-class="divider" />
          </mj-column>
        </mj-section>
        <mj-section>
          <mj-column>
            <mj-text mj-class="headline-box" align="center">
              <span class="headline-text">Top Headlines</span>
            </mj-text>
            ${topHeadlines.map(headline => `
              <mj-text mj-class="headline-box">
                <span class="headline-text">${headline.Title}</span>
              </mj-text>
              <mj-text mj-class="summary">
                ${headline.Summary.replace(/\(([^)]+)\)/g, (match, source) => {
                  const sourceName = source.split(', ')[0];
                  const sourceLink = findSourceLink(headline.sources, sourceName);
                  if (sourceLink) {
                    return `(<a href="${sourceLink}" target="_blank" class="source-link">${sourceName}</a>)`;
                  }
                  return match;
                })}
              </mj-text>
              <mj-image src="${headline['Image Filepath']}" alt="${headline.Title}" width="600px" css-class="image" />
              <mj-divider mj-class="divider" />
            `).join('')}
          </mj-column>
        </mj-section>
        ${Object.entries(customHeadlines).map(([topic, headlines]) => `
          <mj-section>
            <mj-column>
              <mj-text mj-class="headline-box" align="center">
                <span class="headline-text">${topic}</span>
              </mj-text>
              ${headlines.map(headline => `
                <mj-text mj-class="headline-box">
                  <span class="headline-text">${headline.Title}</span>
                </mj-text>
                <mj-text mj-class="summary">
                  ${headline.Summary.replace(/\(([^)]+)\)/g, (match, source) => {
                    const sourceName = source.split(', ')[0];
                    const sourceLink = findSourceLink(headline.sources, sourceName);
                    if (sourceLink) {
                      return `(<a href="${sourceLink}" target="_blank" class="source-link">${sourceName}</a>)`;
                    }
                    return match;
                  })}
                </mj-text>
                <mj-image src="${headline['Image Filepath']}" alt="${headline.Title}" width="600px" css-class="image" />
                <mj-divider mj-class="divider" />
              `).join('')}
            </mj-column>
          </mj-section>
        `).join('')}
        <mj-section>
          <mj-column>
            <mj-text mj-class="headline-box" align="center">
              <span class="headline-text">Trending Headlines</span>
            </mj-text>
            ${trendingHeadlines.map(headline => `
              <mj-text mj-class="headline-box">
                <span class="headline-text">${headline.Title}</span>
              </mj-text>
              <mj-text mj-class="summary">
                ${headline.Summary.replace(/\(([^)]+)\)/g, (match, source) => {
                  const sourceName = source.split(', ')[0];
                  const sourceLink = findSourceLink(headline.sources, sourceName);
                  if (sourceLink) {
                    return `(<a href="${sourceLink}" target="_blank" class="source-link">${sourceName}</a>)`;
                  }
                  return match;
                })}
              </mj-text>
              <mj-image src="${headline['Image Filepath']}" alt="${headline.Title}" width="600px" css-class="image" />
              <mj-divider mj-class="divider" />
            `).join('')}
          </mj-column>
        </mj-section>
      </mj-body>
    </mjml>
  `;

  return mjmlContent.trim();
};

// Generate the MJML content
const mjmlContent = generateMJML(jsonData);

// Generate the output filename by replacing the extension
const mjmlFilename = path.basename(jsonFilename, 'brief_files/' + path.extname(jsonFilename)) + '.mjml';

// Write the MJML content to a file with the same name as the JSON file
fs.writeFileSync(mjmlFilename, mjmlContent);

console.log(`MJML file "${mjmlFilename}" has been created.`);
 