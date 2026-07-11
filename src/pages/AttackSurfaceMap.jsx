import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { reportApi } from '../api/reportApi.js';
import { getToken } from '../api/client.js';
import * as THREE from 'three';
import '../styles/global.css';

const AttackSurfaceMap = () => {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const containerRef = useRef(null);
  const animationRef = useRef(null);
  const sceneRef = useRef(null);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      navigate('/login');
      return;
    }

    loadData();
  }, [scanId]);

  useEffect(() => {
    if (data) {
      initThreeScene();
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (sceneRef.current) {
        sceneRef.current.dispose();
      }
    };
  }, [data]);

  const loadData = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await reportApi.getReport(scanId);
      if (response.success) {
        const surfaceData = response.report.scan.attack_surface_data;
        setData(surfaceData || {});
      } else {
        setError(response.message || 'Failed to load attack surface data.');
      }
    } catch (err) {
      console.error('Attack surface error:', err);
      setError('An error occurred while loading data.');
    } finally {
      setLoading(false);
    }
  };

  const initThreeScene = () => {
    const container = containerRef.current;
    if (!container) return;

    // Clean up previous scene
    if (sceneRef.current) {
      sceneRef.current.dispose();
    }

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a1a);

    const width = container.clientWidth;
    const height = container.clientHeight || 400;
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 5, 10);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Get endpoints
    const endpoints = data?.endpoints || [];
    const count = Math.min(endpoints.length, 30);

    if (count === 0) {
      // Create demo network
      createDemoNetwork(scene);
    } else {
      createNetwork(scene, endpoints);
    }

    // Add lights
    const ambientLight = new THREE.AmbientLight(0x222244, 0.5);
    scene.add(ambientLight);
    const dirLight = new THREE.DirectionalLight(0x00f0ff, 0.5);
    dirLight.position.set(5, 10, 5);
    scene.add(dirLight);

    // Animation loop
    let nodes = null;
    let edges = null;
    scene.children.forEach(child => {
      if (child.type === 'Points') nodes = child;
      if (child.type === 'LineSegments') edges = child;
    });

    const animate = () => {
      if (nodes) {
        nodes.rotation.y += 0.003;
        nodes.rotation.x = Math.sin(Date.now() * 0.0001) * 0.05;
      }
      if (edges) {
        edges.rotation.y += 0.003;
        edges.rotation.x = Math.sin(Date.now() * 0.0001) * 0.05;
      }
      renderer.render(scene, camera);
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    // Handle resize
    const handleResize = () => {
      const w = container.clientWidth;
      const h = container.clientHeight || 400;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener('resize', handleResize);

    sceneRef.current = {
      dispose: () => {
        renderer.dispose();
        if (container.contains(renderer.domElement)) {
          container.removeChild(renderer.domElement);
        }
        window.removeEventListener('resize', handleResize);
      }
    };
  };

  const createNetwork = (scene, endpoints) => {
    const count = Math.min(endpoints.length, 30);
    const positions = [];
    const colors = [];

    // Central node
    positions.push(0, 0, 0);
    colors.push(0, 0.94, 1);

    for (let i = 1; i < count + 1; i++) {
      const angle = (i / (count + 1)) * Math.PI * 2;
      const radius = 2 + Math.random() * 1.5;
      const height = (Math.random() - 0.5) * 1.5;

      positions.push(
        Math.cos(angle + Math.random() * 0.2) * radius,
        height,
        Math.sin(angle + Math.random() * 0.2) * radius
      );

      colors.push(0, 0.4 + Math.random() * 0.6, 0.6 + Math.random() * 0.4);
    }

    // Node geometry
    const nodeGeometry = new THREE.BufferGeometry();
    nodeGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    nodeGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const nodeMaterial = new THREE.PointsMaterial({
      size: 0.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending
    });

    const nodes = new THREE.Points(nodeGeometry, nodeMaterial);
    scene.add(nodes);

    // Edge geometry
    const edgePositions = [];
    for (let i = 0; i < positions.length; i += 3) {
      for (let j = i + 3; j < positions.length; j += 3) {
        if (Math.random() < 0.1) {
          edgePositions.push(
            positions[i], positions[i + 1], positions[i + 2],
            positions[j], positions[j + 1], positions[j + 2]
          );
        }
      }
    }

    if (edgePositions.length > 0) {
      const edgeGeometry = new THREE.BufferGeometry();
      edgeGeometry.setAttribute('position', new THREE.Float32BufferAttribute(edgePositions, 3));

      const edgeMaterial = new THREE.LineBasicMaterial({
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.1,
        blending: THREE.AdditiveBlending
      });

      const edges = new THREE.LineSegments(edgeGeometry, edgeMaterial);
      scene.add(edges);
    }
  };

  const createDemoNetwork = (scene) => {
    const nodeCount = 20;
    const positions = [];
    const colors = [];

    positions.push(0, 0, 0);
    colors.push(0, 0.94, 1);

    for (let i = 1; i < nodeCount; i++) {
      const angle = (i / nodeCount) * Math.PI * 2;
      const radius = 2 + Math.random() * 1.5;
      const height = (Math.random() - 0.5) * 1.5;

      positions.push(
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius
      );
      colors.push(0, 0.4 + Math.random() * 0.6, 0.6 + Math.random() * 0.4);
    }

    const nodeGeometry = new THREE.BufferGeometry();
    nodeGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    nodeGeometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const nodeMaterial = new THREE.PointsMaterial({
      size: 0.25,
      vertexColors: true,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    const nodes = new THREE.Points(nodeGeometry, nodeMaterial);
    scene.add(nodes);

    // Random edges
    const edgePositions = [];
    for (let i = 0; i < 30; i++) {
      const idx1 = Math.floor(Math.random() * nodeCount) * 3;
      const idx2 = Math.floor(Math.random() * nodeCount) * 3;
      if (idx1 !== idx2) {
        edgePositions.push(
          positions[idx1], positions[idx1 + 1], positions[idx1 + 2],
          positions[idx2], positions[idx2 + 1], positions[idx2 + 2]
        );
      }
    }

    if (edgePositions.length > 0) {
      const edgeGeometry = new THREE.BufferGeometry();
      edgeGeometry.setAttribute('position', new THREE.Float32BufferAttribute(edgePositions, 3));
      const edgeMaterial = new THREE.LineBasicMaterial({
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.08,
        blending: THREE.AdditiveBlending
      });
      const edges = new THREE.LineSegments(edgeGeometry, edgeMaterial);
      scene.add(edges);
    }
  };

  const renderList = (items, limit = 50) => {
    if (!items || items.length === 0) {
      return <div className="no-data">None detected</div>;
    }

    const displayItems = items.slice(0, limit);
    const hasMore = items.length > limit;

    return (
      <>
        {displayItems.map((item, index) => (
          <div key={index} className="item">{item}</div>
        ))}
        {hasMore && (
          <div className="item" style={{ color: '#667', fontStyle: 'italic' }}>
            + {items.length - limit} more...
          </div>
        )}
      </>
    );
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-container">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2 text-muted">Loading attack surface data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="alert alert-danger" role="alert">
          <i className="fas fa-exclamation-circle me-2"></i>
          {error}
        </div>
        <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
          <i className="fas fa-arrow-left"></i> Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1 className="page-title">
          <i className="fas fa-sitemap"></i> Attack Surface Map
        </h1>
        <span className="text-muted" style={{ fontSize: '0.85rem' }}>
          {data?.target_url || 'N/A'}
        </span>
      </div>

      {/* Stats */}
      <div className="surface-stats">
        <div className="surface-stat">
          <div className="num">{data?.total_pages || 0}</div>
          <div className="label">Total Pages</div>
        </div>
        <div className="surface-stat">
          <div className="num">{(data?.endpoints || []).length}</div>
          <div className="label">Endpoints</div>
        </div>
        <div className="surface-stat">
          <div className="num">{(data?.forms || []).length}</div>
          <div className="label">Forms</div>
        </div>
        <div className="surface-stat">
          <div className="num">{(data?.login_pages || []).length}</div>
          <div className="label">Login Pages</div>
        </div>
        <div className="surface-stat">
          <div className="num">{(data?.api_endpoints || []).length}</div>
          <div className="label">API Endpoints</div>
        </div>
        <div className="surface-stat">
          <div className="num">{(data?.admin_pages || []).length}</div>
          <div className="label">Admin Pages</div>
        </div>
      </div>

      {/* 3D Map */}
      <div className="surface-map-container" ref={containerRef} style={{ minHeight: '400px' }}></div>

      {/* Details */}
      <div className="surface-details">
        <div className="surface-section">
          <h4><i className="fas fa-code"></i> Technologies Detected</h4>
          <div className="technologies">
            {data?.technologies && data.technologies.length > 0 ? (
              data.technologies.map((tech, index) => (
                <span key={index} className="tech-tag">{tech}</span>
              ))
            ) : (
              <div className="no-data">No technologies detected</div>
            )}
          </div>
        </div>

        <div className="surface-section">
          <h4><i className="fas fa-file"></i> File Types</h4>
          <div>
            {data?.file_types && Object.keys(data.file_types).length > 0 ? (
              Object.entries(data.file_types)
                .sort((a, b) => b[1] - a[1])
                .map(([ext, count]) => (
                  <div key={ext} className="item">
                    <span>.<strong>{ext}</strong></span>
                    <span className="badge-count">{count}</span>
                  </div>
                ))
            ) : (
              <div className="no-data">No files detected</div>
            )}
          </div>
        </div>

        <div className="surface-section">
          <h4><i className="fas fa-link"></i> Directories</h4>
          <div className="item-list">
            {renderList(data?.directories)}
          </div>
        </div>

        <div className="surface-section">
          <h4><i className="fas fa-user-lock"></i> Login Pages</h4>
          <div className="item-list">
            {renderList(data?.login_pages)}
          </div>
        </div>

        <div className="surface-section">
          <h4><i className="fas fa-server"></i> API Endpoints</h4>
          <div className="item-list">
            {renderList(data?.api_endpoints)}
          </div>
        </div>

        <div className="surface-section">
          <h4><i className="fas fa-user-shield"></i> Admin Pages</h4>
          <div className="item-list">
            {renderList(data?.admin_pages)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AttackSurfaceMap;