// my-website/src/pages/index.tsx
import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

export default function Home() {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="A complete textbook on embodied intelligence, humanoid robots, and real-world physical AI systems.">
      <main style={{ maxWidth: 980, margin: '2rem auto', padding: '0 1rem' }}>
        <header>
          <h1>Physical AI & Humanoid Robotics</h1>
          <p style={{ fontSize: '1.05rem', color: '#555' }}>
            A complete textbook on embodied intelligence, humanoid robots, and real-world physical AI systems.
          </p>
        </header>

        <section style={{ marginTop: '1.5rem', lineHeight: 1.7 }}>
          <h2>What this book covers</h2>
          <ul>
            <li>Fundamentals of Physical AI</li>
            <li>Robotics basics (ROS2, URDF)</li>
            <li>Humanoid robot design</li>
            <li>Sensing & perception (LiDAR, Depth, IMU)</li>
            <li>AI-based movement & control (Isaac Sim, Nav2)</li>
            <li>Embodied intelligence & VLA</li>
            <li>Training, sim-to-real, and capstone project</li>
          </ul>

          <p style={{ marginTop: '1rem' }}>
            Start reading the textbook:
            {' '}
            <Link to="/docs/physical-ai/01-introduction">Begin the Book →</Link>
          </p>
        </section>

        <footer style={{ marginTop: '3rem', color: '#666', fontSize: '.9rem' }}>
          <p>Author: Muhammad Muaaz Ansari</p>
        </footer>
      </main>
    </Layout>
  );
}
