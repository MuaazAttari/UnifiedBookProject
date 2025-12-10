// Docusaurus build configuration
const path = require('path');

// Configuration for different environments
const buildConfigs = {
  development: {
    baseUrl: '/',
    trailingSlash: true,
    sitemap: false,
    minify: false,
  },
  staging: {
    baseUrl: process.env.DEPLOY_PRIME_URL || '/',
    trailingSlash: undefined, // Use Docusaurus default
    sitemap: true,
    minify: true,
  },
  production: {
    baseUrl: process.env.BASE_URL || '/unified-book/',
    trailingSlash: false,
    sitemap: true,
    minify: true,
  }
};

// Get the current environment
const environment = process.env.NODE_ENV || 'development';
const config = buildConfigs[environment];

console.log(`Using build configuration for: ${environment}`);

module.exports = {
  ...config,
  environment,
  // Additional build options
  buildOptions: {
    // Whether to include the link to the source code of the docs in the footer
    editUrl: process.env.EDIT_URL || null,

    // Whether to generate a sitemap
    sitemap: {
      changefreq: 'weekly',
      priority: 0.5,
      ignorePatterns: ['/tags/**'],
      filename: 'sitemap.xml',
    },
  }
};