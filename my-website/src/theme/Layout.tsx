import React, { useEffect } from 'react';
import OriginalLayout from '@theme-original/Layout';
import ChatWidget from '../components/RAGChat/ChatWidget';
import ChapterToolbar from '../components/RAGChat/ChapterToolbar';

type LayoutProps = {
  children: React.ReactNode;
};

export default function Layout(props: LayoutProps): JSX.Element {
  useEffect(() => {
    // Add logic to show/hide chapter toolbar based on current page
    const updateToolbarVisibility = () => {
      const isChapterPage = window.location.pathname.includes('/docs/');
      const toolbar = document.querySelector('.chapter-toolbar');

      if (toolbar) {
        if (isChapterPage) {
          toolbar.classList.add('show');
        } else {
          toolbar.classList.remove('show');
        }
      }
    };

    // Run on initial load
    updateToolbarVisibility();

    // Run when route changes (in a real app, you'd use Docusaurus's route change events)
    const handleRouteChange = () => {
      updateToolbarVisibility();
    };

    window.addEventListener('popstate', handleRouteChange);

    // Also check on hash changes (for SPAs)
    window.addEventListener('hashchange', handleRouteChange);

    return () => {
      window.removeEventListener('popstate', handleRouteChange);
      window.removeEventListener('hashchange', handleRouteChange);
    };
  }, []);

  return (
    <>
      <OriginalLayout {...props} />
      <ChapterToolbar />
      <ChatWidget />
    </>
  );
}