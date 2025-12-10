// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Unified Physical AI & Humanoid Robotics Learning Book',
  tagline: 'Comprehensive textbook on Physical AI and Humanoid Robotics',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-username.github.io',
  // Set the /<base>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<username>.github.io/<repo-name>'
  baseUrl: '/unified-book/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'your-organization', // Usually your GitHub org/user name.
  projectName: 'unified-book', // Usually your repo name.
  deploymentBranch: 'gh-pages', // Branch that GitHub pages will deploy from.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
          // Configure search functionality
          showLastUpdateTime: true,
          showLastUpdateAuthor: true,
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  plugins: [
    [
      require.resolve("@cmfcmf/docusaurus-search-local"),
      {
        // whether to index docs pages
        indexDocs: true,
        // Whether to also index the titles of the parent categories in the sidebar of each doc.
        // 0 disables this feature.
        // 1 indexes the direct parent category in the sidebar of each doc page
        // 2 indexes up to 2 nested parent categories
        // 3...
        indexDocSidebarParentCategories: 0,
        // whether to index blog pages
        indexBlog: true,
        // whether to index static pages
        // /404.html is never indexed
        indexPages: false,
        // language of your documentation, see next section
        language: "en",
        // when using the default docusaurus theme, this will also add a search icon to the navbar
        // when using a custom theme, use the hook or component to add the search bar yourself
        style: undefined,
        // lunr.js-specific settings
        lunr: {
          // see https://lunrjs.com/docs/lunr.Builder.html#field
          titleBoost: 100,
          contentBoost: 10,
          tagsBoost: 10,
          parentCategoriesBoost: 10, // Only used when indexDocSidebarParentCategories > 0
        },
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'Physical AI & Robotics Book',
        logo: {
          alt: 'Physical AI Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Textbook',
          },
          {to: '/blog', label: 'Blog', position: 'left'},
          {
            href: 'https://github.com/facebook/docusaurus',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Chapters',
            items: [
              {
                label: 'Introduction',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'ROS Community',
                href: 'https://discourse.ros.org/',
              },
              {
                label: 'Robotics Stack Exchange',
                href: 'https://robotics.stackexchange.com/',
              },
            ],
          },
          {
            title: 'Resources',
            items: [
              {
                label: 'NVIDIA Isaac',
                href: 'https://developer.nvidia.com/isaac',
              },
              {
                label: 'Gazebo Sim',
                href: 'https://gazebosim.org/',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Unified Physical AI & Humanoid Robotics Learning Book. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['python', 'bash', 'json', 'yaml'],
      },
      // Book reading experience enhancements
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: false,
        }
      },
      algolia: {
        // The application ID provided by Algolia
        appId: process.env.REACT_APP_ALGOLIA_APP_ID || 'YOUR_APP_ID',
        // Public API key: it is safe to commit it
        apiKey: process.env.REACT_APP_ALGOLIA_SEARCH_KEY || 'YOUR_SEARCH_API_KEY',
        indexName: process.env.REACT_APP_ALGOLIA_INDEX_NAME || 'your-index-name',
        // Optional: see doc link below
        contextualSearch: true,
        // Optional: Specify domains where the navigation should occur through window.location instead on history.push. Useful when our Algolia config crawls multiple documentation sites and we want to navigate with window.location.href to them.
        externalUrlRegex: 'external\\.com|domain\\.com',
        // Optional: Replace parts of the item URLs from Algolia. Useful when using the same search index for multiple deployments using a different baseUrl. You can use regexp or string in the `from` param. For example: localhost:3000 vs myCompany.com/docs
        replaceSearchResultPathname: {
          from: '/docs/', // or as RegExp: /\/docs\//
          to: '/',
        },
        // Optional: Algolia search parameters
        searchParameters: {},
        // Optional: path for search page that enabled by default (`false` to disable it)
        searchPagePath: 'search',
      },
    }),
};

module.exports = config;