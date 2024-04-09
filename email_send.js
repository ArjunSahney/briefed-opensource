// Takes json formatted for briefed, formats it and sends it as an email 
// node email_send.js SAMPLE.json recipient@example.com
import fs from 'fs';
import path from 'path';
import mjml2html from 'mjml';
import nodemailer from 'nodemailer';

// Get the filename and email recipient from the command-line arguments
const jsonFilename = process.argv[2];
const recipientEmail = process.argv[3];

// Read the JSON data from the file
const jsonData = JSON.parse(fs.readFileSync(jsonFilename, 'utf8'));

// Function to find the source link based on the source name
const findSourceLink = (sources, sourceName) => {
  if (!Array.isArray(sources)) {
    console.error('Invalid or undefined sources array');
    return null;
  }
  const source = sources.find(([name]) => name === sourceName);
  return source ? source[1] : null;
};

// Generate the MJML content
const generateMJML = (data) => {
  // Provide default empty arrays for destructured properties to prevent errors
  const {
    'Top Headlines': topHeadlines = [],
    'Custom Headlines': customHeadlines = [],
    'Trending Headlines': trendingHeadlines = []
  } = data;

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

// Compile MJML to HTML
const { html, errors } = mjml2html(mjmlContent);

if (errors.length > 0) {
  console.error('MJML compilation errors:', errors);
  process.exit(1);
}

// Generate the output filename by replacing the extension
const htmlFilename = path.basename(jsonFilename, path.extname(jsonFilename)) + '.html';

// Create the "mvp_client" directory if it doesn't exist
const outputDir = 'mvp_client';
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir);
}

// Write the HTML content to a file in the "mvp_client" directory
const outputPath = path.join(outputDir, htmlFilename);
fs.writeFileSync(outputPath, html);

console.log(`HTML file "${outputPath}" has been created.`);

// Create a transporter using Gmail SMTP
const transporter = nodemailer.createTransport({
  host: 'smtp.gmail.com',
  port: 465,
  secure: true,
  auth: {
    user: 'newsbriefsforyou@gmail.com',
    pass: 'axxa ayoy vitv ojiu',
  },
});

// Configure the email options
const mailOptions = {
  from: 'newsbriefsforyou@gmail.com',
  to: recipientEmail,
  subject: "Briefed: Your Daily Briefs",
  html: html,
};

// Send the email
transporter.sendMail(mailOptions, (error, info) => {
  if (error) {
    console.error('Error sending email:', error);
  } else {
    console.log('Email sent:', info.response);
  }
});