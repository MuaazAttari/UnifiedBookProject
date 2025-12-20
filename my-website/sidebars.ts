import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  textbookSidebar: [
    {
      type: 'category',
      label: 'Physical AI & Humanoid Robotics',
      collapsible: false,
      items: [
        'physical-ai/introduction',
        'physical-ai/what-is-physical-ai',
        'physical-ai/robotics-basics',
        'physical-ai/humanoid-robot-design',
        'physical-ai/ai-sensing-perception',
        'physical-ai/ai-movement-control',
        'physical-ai/embodied-intelligence',
        'physical-ai/robotic-systems-architecture',
        'physical-ai/training-fine-tuning',
        'physical-ai/real-world-usecases',
        'physical-ai/future-of-physical-ai',
      ],
    },
  ],
};

export default sidebars;
