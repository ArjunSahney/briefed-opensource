const fs = require('fs');

// Read the JSON data from the file
const jsonData = JSON.parse(fs.readFileSync('SAMPLE.json', 'utf8'));

// Generate the MJML content
const generateMJML = (data) => {
  const { 'Top Headlines': topHeadlines, 'Custom Headlines': customHeadlines, 'Trending Headlines': trendingHeadlines } = data;

  const mjmlContent = `
    <mjml>
      <mj-head>
        <mj-style>
          .headline {
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 10px;
          }
          .summary {
            font-size: 14px;
            color: #666666;
            margin-bottom: 10px;
          }
          .source {
            font-size: 12px;
            color: #999999;
            margin-bottom: 5px;
          }
        </mj-style>
      </mj-head>
      <mj-body>
        <mj-section>
          <mj-column>
            <mj-text font-size="24px" font-weight="bold" align="center">Top Headlines</mj-text>
            ${topHeadlines.map(headline => `
              <mj-text css-class="headline">${headline.Title}</mj-text>
              <mj-text css-class="summary">${headline.Summary}</mj-text>
              ${headline.sources.map(source => `
                <mj-text css-class="source">${source[0]} - ${source[2]}</mj-text>
              `).join('')}
              <mj-image src="${headline['Image Filepath']}" alt="${headline.Title}" width="600px" />
            `).join('')}
          </mj-column>
        </mj-section>
        ${Object.entries(customHeadlines).map(([topic, headlines]) => `
          <mj-section>
            <mj-column>
              <mj-text font-size="24px" font-weight="bold" align="center">${topic}</mj-text>
              ${headlines.map(headline => `
                <mj-text css-class="headline">${headline.Title}</mj-text>
                <mj-text css-class="summary">${headline.Summary}</mj-text>
                ${headline.sources.map(source => `
                  <mj-text css-class="source">${source[0]} - ${source[2]}</mj-text>
                `).join('')}
                <mj-image src="${headline['Image Filepath']}" alt="${headline.Title}" width="600px" />
              `).join('')}
            </mj-column>
          </mj-section>
        `).join('')}
        <mj-section>
          <mj-column>
            <mj-text font-size="24px" font-weight="bold" align="center">Trending Headlines</mj-text>
            ${trendingHeadlines.map(headline => `
              <mj-text css-class="headline">${headline.Title}</mj-text>
              <mj-text css-class="summary">${headline.Summary}</mj-text>
              ${headline.sources.map(source => `
                <mj-text css-class="source">${source[0]} - ${source[2]}</mj-text>
              `).join('')}
              <mj-image src="${headline['Image Filepath']}" alt="${headline.Title}" width="600px" />
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

// Write the MJML content to a file with the same name as the JSON file
const mjmlFilename = 'paste.mjml';
fs.writeFileSync(mjmlFilename, mjmlContent);

console.log(`MJML file "${mjmlFilename}" has been created.`);